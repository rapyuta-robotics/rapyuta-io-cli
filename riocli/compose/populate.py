from __future__ import annotations

import fnmatch
import shlex
from typing import TYPE_CHECKING, Any

import click
from munch import Munch

if TYPE_CHECKING:
    from collections.abc import Sequence

from riocli.compose.defaults import (
    CLOUD_RUNTIME,
    CONFIGS_DIR,
    generate_roscore_service,
    get_default_volume_mounts,
)
from riocli.compose.model import DependsCondition, DockerCompose, HealthCheck, Service
from riocli.constants.colors import Colors
from riocli.constants.symbols import Symbols
from riocli.model.base import package_key
from riocli.utils.spinner import with_spinner

# Constants
VOLUME_PERMISSIONS = {
    755: "rw",
    777: "rw",
}

FIXPERMS_IMAGE = "alpine:latest"

ROS_MASTER_URI = "http://127.0.0.1:1234"


@with_spinner(text="Converting...", timer=True)
def populate(
    ctx: click.Context,
    deployments: dict[str, dict],
    packages: dict[str, dict],
    configs_path: str | None = None,
    ignore_volume_source: Sequence[str] = (),
    *args,
    **kwargs,
) -> DockerCompose:
    """
    Converts a set of rapyuta.io deployments and packages into a Docker Compose structure.

    Args:
        deployments: Dictionary of deployment definitions.
        packages: Dictionary of package definitions.
        configs_path: Host-side path to bind-mount in place of CONFIGS_DIR
            wherever CONFIGS_DIR appears as a volume's host path.
        ignore_volume_source: gitignore-style patterns matched against a volume's
            full host-side path -- binds matching one are dropped entirely.
            Independent of configs_path; applies whether or not it's also given.

    Returns:
        DockerCompose object representing the final configuration.
    """
    spinner = kwargs.get("spinner")
    services: dict[str, Service] = {}
    processed_deployments: dict[str, dict] = {}
    named_volumes: set[str] = set()

    # Process deployments and create services
    for key, deployment in deployments.items():
        try:
            _process_deployment_services(
                ctx=ctx,
                deployment=deployment,
                deployments=deployments,
                packages=packages,
                services=services,
                named_volumes=named_volumes,
                configs_path=configs_path,
                ignore_volume_source=ignore_volume_source,
                spinner=spinner,
            )
            processed_deployments[key] = deployment
        except (KeyError, ValueError) as e:
            # Log error but continue processing other deployments
            spinner.text = click.style(
                f"Warning: Skipping deployment {deployment.get('metadata', {}).get('name', 'unknown')}: {e}",
                fg=Colors.YELLOW,
            )
            spinner.yellow.warning(Symbols.WARNING)
            continue

    spinner.text = click.style("Conversion successful.", fg=Colors.BRIGHT_GREEN)
    spinner.green.ok(Symbols.SUCCESS)

    fixup_vols = get_volumes_requiring_fixup(
        processed_deployments, configs_path, ignore_volume_source
    )
    if fixup_vols:
        fix_cmds = [_build_fixup_cmd(entry) for entry in fixup_vols]
        fixperms_vols = [
            f"{entry['host']}:{entry['container']}:rw" for entry in fixup_vols
        ]
        services["init-fixperms"] = Service(
            container_name="init-fixperms",
            image=FIXPERMS_IMAGE,
            user="0:0",
            command=["sh", "-c", " && ".join(fix_cmds)],
            volumes=fixperms_vols,
            restart="no",
        )
        affected_paths = {entry["container"] for entry in fixup_vols}
        for name, svc in services.items():
            if name == "init-fixperms":
                continue
            if any(
                isinstance(vol, str) and _get_volume_target(vol) in affected_paths
                for vol in getattr(svc, "volumes", [])
            ):
                if svc.depends_on is None:
                    svc.depends_on = {}
                svc.depends_on["init-fixperms"] = DependsCondition(
                    condition="service_completed_successfully"
                )

    # Declare top-level named volumes for any disk-backed cloud mounts. A non-empty
    # mapping ({"driver": "local"}) is required because clean_dict() drops keys whose
    # value is {} or None — an empty volume config would be stripped from the output.
    volumes = (
        {name: {"driver": "local"} for name in sorted(named_volumes)}
        if named_volumes
        else None
    )

    return DockerCompose(services=services, volumes=volumes)


def _build_fixup_cmd(entry: dict) -> str:
    """Build a shell compound command that handles both file and directory mount paths.

    Uses a runtime [ -f ] check so file mounts (pre-existing host files) receive
    plain chown/chmod while directory mounts receive mkdir -p + recursive chown.
    The returned string is a single if/else/fi block safe to && -chain with others.

    Docker bind-mount caveat: when the host path does not exist, Docker automatically
    creates a *directory* there while setting up the init container's own bind mount —
    even for file mounts.  This happens before the init container's shell command runs,
    so the init container is responsible for correcting the path type.
    The [ -f ] check handles two of the three possible states correctly:
      - host path is a file     → true branch, chown/chmod applied directly ✓
      - host path is a directory and intended to be one → false branch, mkdir -p
                                  is a no-op ✓
    The remaining gap is:
      - host path is intended to be a file but the init container finds a directory
        there (created automatically during bind-mount setup) → [ -f ] is false, so
        the else branch runs mkdir -p (a no-op) and the wrong type persists.
        The fix belongs here: detect [ -d path ] for file mounts, remove the
        directory, and touch the file in its place.
    """
    path = shlex.quote(entry["container"])
    dir_cmds = [f"mkdir -p {path}"]
    file_cmds = []

    if entry["uid"] is not None or entry["gid"] is not None:
        owner = str(entry["uid"]) if entry["uid"] is not None else ""
        group = str(entry["gid"]) if entry["gid"] is not None else ""
        dir_cmds.append(f"chown -R {owner}:{group} {path}")
        file_cmds.append(f"chown {owner}:{group} {path}")

    if entry["perm"] is not None:
        dir_cmds.append(f"chmod {entry['perm']} {path}")
        file_cmds.append(f"chmod {entry['perm']} {path}")

    dir_block = " && ".join(dir_cmds)
    file_block = " && ".join(file_cmds) if file_cmds else ":"

    return f"if [ -f {path} ]; then {file_block}; else {dir_block}; fi"


def _get_volume_target(vol: str) -> str | None:
    """Extracts the container-side mount path from a compose volume string.

    Parses from the right, not `vol.split(":")[1]`, so a host path containing
    a literal ':' doesn't shift the field positions -- e.g. a Compose short
    volume syntax quirk rather than a Windows accommodation (this project does
    not target Windows); relevant now that --configs-path lets a user point
    at any host directory name, including one with a colon in it. The trailing
    segment is treated as a mode ("rw", "ro", "rslave", ...) rather than the
    container path whenever it doesn't look like an absolute path.
    """
    parts = vol.split(":")
    if len(parts) < 2:
        return None
    if len(parts) >= 3 and not parts[-1].startswith("/"):
        return parts[-2]
    return parts[-1]


def _is_ignored_volume_source(host_path: str, ignore_patterns: Sequence[str]) -> bool:
    """gitignore-style match against a volume's full host-side path.

    Patterns are evaluated in order, last match wins; a leading '!' negates a
    preceding match (so a later, more specific pattern can re-include a path an
    earlier, broader pattern excluded -- e.g. ["/opt/rapyuta/configs/station/*",
    "!/opt/rapyuta/configs/station/sim-nginx.conf.template"]). A pattern matches
    host_path itself (fnmatch-style glob) or, treated as a directory prefix, any
    path under it. Not scoped to CONFIGS_DIR or configs_path in any way -- any
    absolute host path a deployment declares as a volume source is a valid
    pattern target.
    """
    ignored = False
    for raw in ignore_patterns:
        negate = raw.startswith("!")
        pattern = (raw[1:] if negate else raw).rstrip("/")
        if not pattern:
            continue
        if fnmatch.fnmatch(host_path, pattern) or host_path.startswith(pattern + "/"):
            ignored = not negate
    return ignored


def _under_configs_dir(host_path: str) -> bool:
    """True if host_path is CONFIGS_DIR itself or a path inside it."""
    return host_path == CONFIGS_DIR or host_path.startswith(CONFIGS_DIR + "/")


def _substitute_configs_path(
    host_path: str | None,
    configs_path: str | None,
    ignore_patterns: Sequence[str] = (),
) -> str | None:
    """Rewrites a volume's host path from under CONFIGS_DIR to under configs_path, if given.

    Returns None (signalling "drop this volume") when host_path matches one of
    ignore_patterns -- lets callers omit binds that have no local equivalent
    instead of pointing them at a directory that doesn't exist. Independent of
    configs_path: ignoring and redirecting are two separate operations on the
    same bind, so ignore_patterns is checked first and applies whether or not
    configs_path is given.
    """
    if not host_path:
        return host_path
    if ignore_patterns and _is_ignored_volume_source(host_path, ignore_patterns):
        return None
    if not configs_path:
        return host_path
    if host_path == CONFIGS_DIR:
        return configs_path
    if _under_configs_dir(host_path):
        return configs_path.rstrip("/") + host_path[len(CONFIGS_DIR) :]
    return host_path


def get_volumes_requiring_fixup(
    deployments: dict[str, dict],
    configs_path: str | None = None,
    ignore_volume_source: Sequence[str] = (),
) -> list[dict]:
    """Collects volumes declaring uid/gid/perm into init-fixperms fixup entries.

    Skips any volume whose subPath was redirected under configs_path: that
    bind now points at the developer's own local directory, and running
    chown/chmod as root against it (as init-fixperms does for real device
    paths) would change ownership/mode of the developer's files rather than
    fixing up a device path -- see init-fixperms's root user and _build_fixup_cmd.
    No generate-time existence check either: generate and up/down can run on
    different machines, so the generation host's filesystem proves nothing.
    """
    volumes_by_path: dict[tuple, dict] = {}
    for dep in deployments.values():
        for volume in dep.spec.get("volumes", []):
            uid, gid, perm = volume.get("uid"), volume.get("gid"), volume.get("perm")
            if uid is None and gid is None and perm is None:
                continue
            sub_path = volume.get("subPath")
            if configs_path and sub_path and _under_configs_dir(sub_path):
                continue
            host = _substitute_configs_path(sub_path, configs_path, ignore_volume_source)
            container = volume.get("mountPath")
            if not host or not container:
                continue

            if not container.startswith("/"):
                raise ValueError(
                    f"mountPath must be an absolute path, got: {container!r}"
                )

            if uid is not None:
                uid = int(uid)
                if uid < 0:
                    raise ValueError(f"uid must be a non-negative integer, got: {uid}")

            if gid is not None:
                gid = int(gid)
                if gid < 0:
                    raise ValueError(f"gid must be a non-negative integer, got: {gid}")

            if perm is not None:
                perm = int(perm)
                if not (0 <= perm <= 7777):
                    raise ValueError(
                        f"perm must be a valid octal permission value (0–7777), got: {perm}"
                    )

            key = (host, container)
            if key not in volumes_by_path:
                volumes_by_path[key] = {
                    "host": host,
                    "container": container,
                    "uid": uid,
                    "gid": gid,
                    "perm": perm,
                }
    return list(volumes_by_path.values())


def _is_ros_enabled(deployment: Munch, package: Munch) -> bool:
    if not package.spec.get("ros", {}).get("enabled", False):
        return False
    if "envArgs" in deployment.spec:
        deployment.spec.envArgs.append(
            {"name": "ROS_MASTER_URI", "value": ROS_MASTER_URI}
        )
    else:
        package.spec.get("environmentVars", []).append(
            {"name": "ROS_MASTER_URI", "default": ROS_MASTER_URI}
        )

    return True


def _process_deployment_services(
    ctx: click.Context,
    deployment: dict,
    deployments: dict[str, dict],
    packages: dict[str, dict],
    services: dict[str, Service],
    named_volumes: set[str],
    configs_path: str | None = None,
    ignore_volume_source: Sequence[str] = (),
    spinner=None,
) -> None:
    """Process a single deployment and add its services to the services dictionary.

    ``named_volumes`` accumulates the names of disk-backed volumes encountered so the
    caller can declare them under the compose file's top-level ``volumes:`` key.
    ``spinner`` is forwarded to ``build_volume_mounts`` for subPath warnings.
    """
    dep_name = deployment.metadata.name
    pkg_dep = deployment.metadata.depends
    package = find_package(packages, pkg_dep.nameOrGUID, pkg_dep.version)

    # Get restart policy with normalization
    restart_policy = deployment.spec.get("restart", None)
    restart_policy = restart_policy or package.spec.get("device", {}).get(
        "restart", "always"
    )

    if restart_policy == "onfailure":
        restart_policy = "on-failure"
    elif restart_policy == "never":
        restart_policy = "no"

    # Build volume mounts, dependencies, and environment variables
    volume_mounts = build_volume_mounts(
        deployment, named_volumes, configs_path, ignore_volume_source, spinner=spinner
    )
    ros_enabled = _is_ros_enabled(deployment=deployment, package=package)
    if ros_enabled and "ros-master" not in services:
        services["ros-master"] = generate_roscore_service()
    depends_on = populate_depends_on(
        deployment=deployment,
        deployments=deployments,
        packages=packages,
        ros_enabled=ros_enabled,
    )
    env = merge_env_vars(
        ctx,
        package.spec.get("environmentVars", []),
        deployment.spec.get("envArgs", []),
    )

    # Create services for each executable
    for exe in package.spec.executables:
        service = create_service(
            dep_name, exe, restart_policy, env, volume_mounts, depends_on
        )
        services[service.container_name] = service


def create_service(
    dep_name: str,
    exe: dict,
    restart_policy: str,
    env: dict[str, str],
    volume_mounts: list[str],
    depends_on: dict[str, DependsCondition],
) -> Service:
    """
    Creates a Docker Compose Service object for an executable.

    Args:
        dep_name: Name of the deployment.
        exe: Executable dictionary from package.
        restart_policy: Restart policy string.
        env: Environment variables.
        volume_mounts: List of volume mount strings.
        depends_on: Dependency dictionary.

    Returns:
        A populated Service object.
    """
    exe_name = exe.name
    image = exe.docker.image
    limits = exe.get("limits", {})

    # Format resource limits using utility functions
    mem_limit = f"{limits.get('memory')}m" if limits.get("memory") else None
    cpu_limit = limits.get("cpu", None)

    return Service(
        container_name=f"{dep_name}_{exe_name}",
        image=image,
        restart=restart_policy,
        environment=env,
        volumes=volume_mounts,
        depends_on=depends_on,
        command=populate_command(exe),
        entrypoint=populate_entrypoint(exe),
        healthcheck=populate_healthcheck(exe),
        mem_limit=mem_limit,
        cpus=cpu_limit,
    )


def build_volume_mounts(
    deployment: dict,
    named_volumes: set[str],
    configs_path: str | None = None,
    ignore_volume_source: Sequence[str] = (),
    spinner=None,
) -> list[str]:
    """
    Constructs a list of volume mount strings for a given deployment.

    The default host mounts (``DEFAULT_VOLUME_MOUNTS``) are applied only to the
    ``device`` runtime. A cloud pod receives none of them on the platform (they are
    device-daemon paths — host ``/dev``, other containers' state, the on-device log
    dirs), so cloud services start from an empty list and get only their own declared
    volumes.

    Two kinds of custom volume are supported:

    * Device bind mounts, where ``subPath`` is an absolute host path mounted at
      ``mountPath`` (optionally with a permission-derived mode).
    * Cloud disk mounts, where the volume depends on a ``Disk`` resource. These have
      no host path; they are mapped to a named Docker volume keyed by the disk name,
      and that name is recorded in ``named_volumes`` for top-level declaration. The
      SDK's ``DiskDepends`` model accepts ``"Disk"``/``"disk"`` and defaults to
      ``"Disk"``, so the kind is matched case-insensitively and an omitted kind is
      treated as a disk depends. A disk mount's ``subPath`` cannot be expressed in
      Compose short syntax (the whole volume is mounted); a warning is emitted since
      the platform mounts only the subtree.

    Args:
        deployment: The deployment definition dictionary.
        named_volumes: Mutable set collecting disk-backed named-volume names.
        configs_path: Host-side path to bind-mount in place of CONFIGS_DIR
            wherever CONFIGS_DIR appears as a volume's host path (device
            bind mounts only; cloud disk mounts have no host path).
        ignore_volume_source: gitignore-style patterns matched against a volume's
            full host-side path -- binds matching one are dropped entirely.
            Independent of configs_path; applies whether or not it's also given.
        spinner: Optional spinner used to surface subPath warnings.

    Returns:
        List of Docker volume mount strings.
    """
    # Device runtime gets the standard host mounts (optionally redirected under
    # configs_path, with ignore_volume_source able to drop any default mount,
    # including the whole-tree CONFIGS_DIR bind -- matched against CONFIGS_DIR
    # itself, not the redirected host path, so patterns stay written against
    # the un-rewritten path like every other ignore match); cloud starts empty.
    runtime = deployment.spec.get("runtime")
    if runtime == CLOUD_RUNTIME:
        service_volumes = []
    else:
        service_volumes = get_default_volume_mounts(configs_path)
        if ignore_volume_source:
            service_volumes = [
                vol
                for vol in service_volumes
                if not _is_ignored_volume_source(
                    CONFIGS_DIR
                    if _get_volume_target(vol) == CONFIGS_DIR
                    else vol.split(":", 1)[0],
                    ignore_volume_source,
                )
            ]

    # Add custom volumes from deployment
    for volume in deployment.spec.get("volumes", []):
        dst = volume.get("mountPath")
        if not dst:
            continue

        # Cloud disk-backed volume -> named Docker volume. Match the SDK's DiskDepends
        # semantics: kind is "Disk"/"disk" (case-insensitive) and defaults to "Disk".
        depends = volume.get("depends") or {}
        if depends and str(depends.get("kind", "disk")).lower() == "disk":
            disk_name = depends.get("nameOrGUID")
            if not disk_name:
                continue
            sub_path = volume.get("subPath")
            if sub_path and spinner is not None:
                spinner.write(
                    click.style(
                        f"{Symbols.WARNING} disk '{disk_name}': subPath '{sub_path}' "
                        f"cannot be expressed in Compose short syntax; mounting the "
                        f"whole volume at {dst} (the platform mounts only the subtree).",
                        fg=Colors.YELLOW,
                    )
                )
            service_volumes.append(f"{disk_name}:{dst}")
            named_volumes.add(disk_name)
            continue

        # Device bind mount -> host path mounted at container path, subject to
        # the same configs_path redirect / ignore_volume_source drop as the
        # default CONFIGS_DIR mount above.
        src = _substitute_configs_path(
            volume.get("subPath"), configs_path, ignore_volume_source
        )
        if not src:
            continue

        # Determine volume mode based on permissions
        perm = volume.get("perm")
        mode = ""
        if perm in VOLUME_PERMISSIONS:
            mode = f":{VOLUME_PERMISSIONS.get(perm)}"
        service_volumes.append(f"{src}:{dst}{mode}")

    return service_volumes


def populate_command(exe: dict) -> list[str] | str | None:
    """
    Constructs the command to run for a container from the executable definition.
    If runAsBash is True, wraps the command in a shell invocation.
    Otherwise, returns the command as-is.
    """
    cmd_raw = exe.get("command")
    if not cmd_raw:
        return None

    result: list[str] | str | None = None

    if exe.get("runAsBash") in (True, "true"):
        cmd_str = cmd_raw if isinstance(cmd_raw, str) else " ".join(cmd_raw)
        result = ["/bin/bash", "-c", cmd_str]
    elif isinstance(cmd_raw, list) and len(cmd_raw) == 1:
        result = cmd_raw[0]
    else:
        result = cmd_raw

    return sanitize_command(result)


def sanitize_command(input: list[str] | str | None) -> list[str] | str | None:
    # Docker compose tries to render the $VAR before running the container.
    # Escape all the $VAR -> $$VAR.
    # But there might already be escaped vars, avoid them.
    if isinstance(input, list):
        out = []
        for each in input:
            replaced = each.replace("$", "$$").replace("$$$$", "$$")
            out.append(replaced)

        return out

    if isinstance(input, str):
        return input.replace("$", "$$").replace("$$$$", "$$")


def populate_entrypoint(exe: dict) -> list[str] | str | None:
    """
    Constructs the Docker Compose ``entrypoint`` override from the executable's
    declared ``entrypoint`` field.

    Unlike ``command``, which only supplies arguments to the image's existing
    ENTRYPOINT, this replaces the image's ENTRYPOINT outright -- needed when an
    executable must run a different process than the image's default launcher
    (e.g. a bootstrap script instead of the image's normal server process).

    NOTE: this only affects `rio compose generate`'s local Docker Compose
    output. Real device deployments (`rio apply`) don't read this field at
    all -- there is no ENTRYPOINT-override concept in the device runtime,
    only `command`. Declaring `entrypoint` in a manifest has zero effect
    outside the compose pipeline.
    """
    if "entrypoint" not in exe or exe.get("entrypoint") is None:
        return None

    return sanitize_command(exe.get("entrypoint"))


def find_package(packages: dict[str, dict], name: str, version: str) -> dict:
    """
    Finds a package by name and version in the provided dictionary.
    """
    # Packages are keyed by name and version, so a manifest carrying several
    # versions of the same Package resolves to the right one. The key encodes
    # the version, which is what the caller asked for, so there is nothing
    # left to cross-check afterwards.
    pkg = packages.get(package_key(name, version))
    if not pkg:
        raise KeyError(f"No Package found with name '{name}' and version '{version}'")
    return pkg


def merge_env_vars(
    ctx: click.Context, *env_vars_lists: list[dict[str, Any]]
) -> dict[str, str]:
    """
    Efficiently merges multiple lists of environment variable definitions into a single dictionary.
    Later variables override earlier ones with the same name.
    """
    env = Munch()

    # Flatten all lists into one using generator expression for memory efficiency
    for var in (var for vars_list in env_vars_lists for var in vars_list):
        name = var.get("name", "")
        if name is not None:
            value = var.get("default", var.get("value", ""))
            env[name] = str(value) if value is not None else ""

    env["RIO_CONFIGS_DIR"] = "/opt/rapyuta/configs"

    ctx_vars = {
        "RIO_AuthToken": ctx.obj.data.get("auth_token"),
        "RIO_PROJECT_ID": ctx.obj.data.get("project_id"),
        "RIO_PROJECT_NAME": ctx.obj.data.get("project_name"),
        "RIO_ORGANIZATION_ID": ctx.obj.data.get("organization_id"),
        "RIO_ORGANIZATION_SHORT_GUID": ctx.obj.data.get("organization_short_id"),
        "RIO_ORGANIZATION_NAME": ctx.obj.data.get("organization_name"),
    }
    for key, value in ctx_vars.items():
        if value is not None:
            env[key] = value

    return env


def populate_depends_on(
    deployment: dict,
    deployments: dict[str, dict],
    packages: dict[str, dict],
    ros_enabled: bool = False,
) -> dict[str, DependsCondition]:
    """
    Builds the depends_on relationships for a Docker Compose service
    based on other deployments it references.
    """
    depends_on = Munch()

    if ros_enabled:
        depends_on["ros-master"] = DependsCondition()

    for dep in deployment.spec.get("depends", {}):
        if dep.kind != "deployment":
            continue

        dep_name = dep.nameOrGUID
        dependent_deployment = deployments.get(f"deployment:{dep_name}")
        if not dependent_deployment:
            continue

        # Find the associated package for the dependent deployment
        dep_pkg_meta = dependent_deployment.metadata.depends
        try:
            pkg = find_package(packages, dep_pkg_meta.nameOrGUID, dep_pkg_meta.version)
        except (KeyError, ValueError):
            continue

        # Generate service names for each executable in the dependent package
        for exe in pkg.get("spec", {}).get("executables", []):
            service_name = f"{dep_name}_{exe['name']}"
            condition = DependsCondition()
            # Wait for the dependency to be healthy whenever it emits a healthcheck.
            # Only exec probes produce one (see populate_healthcheck); httpGet probes
            # do not, so those dependencies fall back to service_started.
            if populate_healthcheck(exe):
                condition.condition = "service_healthy"

            depends_on[service_name] = condition

    return depends_on


def populate_healthcheck(exe: dict) -> HealthCheck | None:
    """
    Generates a Docker Compose healthcheck configuration from a livenessProbe.

    Only ``exec`` probes are translated: they name a command the image is expected to
    provide. ``httpGet`` probes are intentionally ignored — rapyuta.io evaluates them
    externally, so container images routinely omit an HTTP client (curl/wget) and an
    in-container HTTP healthcheck would report a false ``unhealthy``. Dependencies whose
    only probe is ``httpGet`` therefore fall back to ``service_started`` ordering (see
    ``populate_depends_on``).
    """
    probe = exe.get("livenessProbe")
    if not probe:
        return None

    command = probe.get("exec", {}).get("command")
    if not command:
        return None

    start_period = None
    if probe.get("initialDelaySeconds") is not None:
        start_period = f"{probe.get('initialDelaySeconds')}s"

    return HealthCheck(
        test=" ".join(shlex.quote(part) for part in command),
        timeout=f"{probe.get('timeoutSeconds', 30)}s",
        interval=f"{probe.get('periodSeconds', 10)}s",
        retries=probe.get("failureThreshold", 3),
        start_period=start_period,
    )

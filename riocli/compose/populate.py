from __future__ import annotations

from typing import Dict, List, Any, Optional

import click
from munch import Munch

from riocli.constants.colors import Colors
from riocli.compose.defaults import generate_roscore_service, DEFAULT_VOLUME_MOUNTS
from riocli.compose.model import DockerCompose, Service, DependsCondition, HealthCheck
from riocli.constants.symbols import Symbols
from riocli.utils.spinner import with_spinner

# Constants
VOLUME_PERMISSIONS = {
    755: "rw",
    777: "rw",
}

ROS_MASTER_URI = "http://127.0.0.1:1234"


@with_spinner(text="Converting...", timer=True)
def populate(
    ctx: click.Context,
    deployments: Dict[str, dict],
    packages: Dict[str, dict],
    *args,
    **kwargs,
) -> DockerCompose:
    """
    Converts a set of rapyuta.io deployments and packages into a Docker Compose structure.

    Args:
        deployments: Dictionary of deployment definitions.
        packages: Dictionary of package definitions.

    Returns:
        DockerCompose object representing the final configuration.
    """
    spinner = kwargs.get("spinner")
    services: Dict[str, Service] = {}

    # Process deployments and create services
    for deployment in deployments.values():
        try:
            _process_deployment_services(
                ctx=ctx,
                deployment=deployment,
                deployments=deployments,
                packages=packages,
                services=services,
            )
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

    return DockerCompose(services=services)


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
    deployments: Dict[str, dict],
    packages: Dict[str, dict],
    services: Dict[str, Service],
) -> None:
    """Process a single deployment and add its services to the services dictionary."""
    dep_name = deployment.metadata.name
    pkg_dep = deployment.metadata.depends
    package = find_package(packages, pkg_dep.nameOrGUID, pkg_dep.version)

    # Get restart policy with normalization
    restart_policy = package.spec.get("device", {}).get("restart", "always")
    if restart_policy == "onfailure":
        restart_policy = "on-failure"

    # Build volume mounts, dependencies, and environment variables
    volume_mounts = build_volume_mounts(deployment)
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
    env: Dict[str, str],
    volume_mounts: List[str],
    depends_on: Dict[str, DependsCondition],
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
        healthcheck=populate_healthcheck(exe),
        mem_limit=mem_limit,
        cpus=cpu_limit,
    )


def build_volume_mounts(deployment: dict) -> List[str]:
    """
    Constructs a list of volume mount strings for a given deployment.
    Includes default volumes and custom volumes specified in the deployment.

    Args:
        deployment: The deployment definition dictionary.

    Returns:
        List of Docker volume mount strings.
    """
    # Start with default volume mounts
    service_volumes = DEFAULT_VOLUME_MOUNTS.copy()

    # Add custom volumes from deployment
    for volume in deployment.spec.get("volumes", []):
        src = volume.get("subPath")
        dst = volume.get("mountPath")
        if not src or not dst:
            continue

        # Determine volume mode based on permissions
        perm = volume.get("perm")
        mode = VOLUME_PERMISSIONS.get(perm, "rslave")
        service_volumes.append(f"{src}:{dst}:{mode}")

    return service_volumes


def populate_command(exe: dict) -> Optional[List[str]]:
    """
    Constructs the command to run for a container from the executable definition.
    If runAsBash is True, wraps the command in a shell invocation.
    Otherwise, returns the command as-is.
    """
    cmd_raw = exe.get("command")
    if not cmd_raw:
        return None

    if exe.get("runAsBash") in (True, "true"):
        cmd_str = cmd_raw if isinstance(cmd_raw, str) else " ".join(cmd_raw)
        return ["/bin/bash", "-c", cmd_str]
    else:
        return cmd_raw if isinstance(cmd_raw, list) else [cmd_raw]


def find_package(packages: Dict[str, dict], name: str, version: str) -> dict:
    """
    Finds a package by name and version in the provided dictionary.
    """
    pkg = packages.get(f"package:{name}")
    if not pkg:
        raise KeyError(f"No Package found with name '{name}'")
    if str(pkg.get("metadata", {}).get("version")) != str(version):
        raise ValueError(
            f"Version mismatch: expected {version}, found {pkg['metadata'].get('version')}"
        )
    return pkg


def merge_env_vars(
    ctx: click.Context, *env_vars_lists: List[Dict[str, Any]]
) -> Dict[str, str]:
    """
    Efficiently merges multiple lists of environment variable definitions into a single dictionary.
    Later variables override earlier ones with the same name.
    """
    env = Munch()

    env["RIO_AuthToken"] = ctx.obj.data.get("auth_token", None)
    env["RIO_CONFIGS_DIR"] = "/opt/rapyuta/configs"
    env["RIO_PROJECT_ID"] = ctx.obj.data.get("project_id", None)
    env["RIO_PROJECT_NAME"] = ctx.obj.data.get("project_name", None)
    env["RIO_ORGANIZATION_ID"] = ctx.obj.data.get("organization_id", None)
    env["RIO_ORGANIZATION_SHORT_GUID"] = ctx.obj.data.get("organization_short_id", None)
    env["RIO_ORGANIZATION_NAME"] = ctx.obj.data.get("organization_name", None)
    # Flatten all lists into one using generator expression for memory efficiency
    for var in (var for vars_list in env_vars_lists for var in vars_list):
        name = var.get("name", "")
        if name is not None:
            value = var.get("default", var.get("value", ""))
            env[name] = str(value) if value is not None else ""
    return env


def populate_depends_on(
    deployment: dict,
    deployments: Dict[str, dict],
    packages: Dict[str, dict],
    ros_enabled: bool = False,
) -> Dict[str, DependsCondition]:
    """
    Builds the depends_on relationships for a Docker Compose service
    based on other deployments it references.
    """
    depends_on = Munch()

    if ros_enabled:
        depends_on["ros-master"] = DependsCondition()

    for dep in deployment.spec.get("depends", {}):
        if deployment.kind != "deployment":
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
            depends_on[service_name] = DependsCondition()

    return depends_on


def populate_healthcheck(exe: dict) -> Optional[HealthCheck]:
    """
    Generates a Docker Compose healthcheck configuration from a livenessProbe.
    """
    probe = exe.get("livenessProbe")
    if not probe:
        return None

    command = probe.get("exec", {}).get("command")
    if not command:
        return None

    return HealthCheck(
        test=" ".join(command),
        timeout=f"{probe.get('timeoutSeconds', 30)}s",
        interval=f"{probe.get('periodSeconds', 10)}s",
        retries=probe.get("failureThreshold", 3),
    )

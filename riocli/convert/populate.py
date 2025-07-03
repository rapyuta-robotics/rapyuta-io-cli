from typing import Dict, List, Any
from riocli.convert.defaults import get_roscore
from riocli.convert.model import (
    DockerCompose,
    Service,
    DependsCondition,
    HealthCheck,
)
import shlex


def populate(deployments: Dict[str, dict], packages: Dict[str, dict]) -> DockerCompose:
    services: Dict[str, Service] = {}
    ros_enabled = False

    for deployment in deployments.values():
        dep_name = deployment["metadata"]["name"]
        pkg_dep = deployment["metadata"]["depends"]
        package = find_package(packages, pkg_dep["nameOrGUID"], pkg_dep["version"])

        if not ros_enabled:
            ros_enabled = package.get("spec", {}).get("ros", {}).get("enabled", False)

        restart_policy = package["spec"].get("device", {}).get("restart", "always")
        if restart_policy == "onfailure":
            restart_policy = "on-failure"

        env = merge_env_vars(
            package["spec"].get("environmentVars", []),
            deployment["spec"].get("envArgs", []),
        )
        volume_mounts = build_volume_mounts(deployment)
        depends_on = populate_depends_on(
            deployment,
            deployments=deployments,
            packages=packages,
        )

        for exe in package["spec"]["executables"]:
            exe_name = exe["name"]
            image = exe["docker"]["image"]
            # Check limits
            limits = exe.get("limits", {})
            cpu_limit = limits.get("cpu", None)
            mem_limit = (
                str(limits.get("memory", "")) + "m" if limits.get("memory") else None
            )

            service_name = f"{dep_name}_{exe_name}"

            services[service_name] = Service(
                container_name=service_name,
                image=image,
                restart=restart_policy,
                environment=env,
                volumes=volume_mounts,
                depends_on=depends_on,
                command=populate_command(exe=exe),
                # healthcheck=populate_healthcheck(exe),
                mem_limit=mem_limit,
                cpus=cpu_limit,
            )

    if ros_enabled == "true" or ros_enabled:
        services["ros-master"] = get_roscore()

    return DockerCompose(version="3", services=services)


def build_volume_mounts(deployment: dict) -> List[Any]:
    """
    Builds a mapping from executable name to volume mount strings.
    Also populates the volumes_dict with named volumes if needed.
    """
    service_volumes: List = [
        "/opt/rapyuta/configs:/opt/rapyuta/configs:rslave",
        "/var/log/riouser:/var/log/riouser:rslave",
        "/var/log/rapyuta/deployments:/var/log/rapyuta/deployments:rslave",
        "/var/lib/docker/containers:/var/lib/docker/containers:rslave",
        "/dev:/dev:rslave",
    ]
    volumes = deployment.get("spec", {}).get("volumes", {})

    for volume in volumes:
        mount_path = volume.get("mountPath")
        sub_path = volume.get("subPath")
        permissions = volume.get("perm")
        read_only = "rw" if permissions in [755, 777] else "rslave"

        if not (mount_path or sub_path):
            continue
        service_volume = "{}:{}:{}".format(sub_path, mount_path, read_only)
        service_volumes.append(service_volume)

    return service_volumes


def populate_command(exe: dict) -> list:
    """
    Returns:
    - If runAsBash == true: ['sh', '-c', '<command string>']
    - Else: shlex.split(<command string>)
    """
    command_raw = exe.get("command")
    run_as_bash = exe.get("runAsBash", False)

    if not command_raw:
        return None

    # Normalize command to string
    if isinstance(command_raw, list):
        command_str = " ".join(str(item) for item in command_raw).strip()
    else:
        command_str = str(command_raw).strip()

    if run_as_bash == "true" or run_as_bash is True:
        return ["bash", "-c", command_str]

    return shlex.split(command_str)


def find_package(packages: Dict[str, dict], name: str, version: str) -> dict:
    """Find package related to deployment.

    Args:
        packages (Dict[str, dict]): dictionary of packages
        name (str): name of package
        version (str): version of package

    Returns:
        dict
    """
    key = f"package:{name}"
    pkg = packages.get(key)
    if not pkg:
        raise KeyError(f"No Package found with name '{name}'")
    if str(pkg.get("metadata", {}).get("version", "")) != str(version):
        raise ValueError(
            f"Version mismatch: expected {version}, found {pkg['metadata'].get('version')}"
        )
    return pkg


def merge_env_vars(*env_vars_lists: List[Dict]) -> Dict[str, str]:
    """
    Merges multiple lists of environment variable dictionaries into a single dict.
    Later lists override earlier ones for duplicate names.
    """
    env_dict = {}
    for env_vars in env_vars_lists:
        for env in env_vars:
            name = env.get("name")
            if name:
                env_dict[name] = env.get("default", "") or env.get("value", "")
    return env_dict


def populate_depends_on(
    deployment: dict,
    deployments: Dict[str, dict],
    packages: Dict[str, dict],
) -> Dict[str, DependsCondition]:
    """
    Builds the depends_on field for a service based on deployment.spec.depends.

    Args:
        deployment: The deployment being processed.
        deployments: All deployments keyed by kind:name.
        packages: All packages keyed by kind:name.

    Returns:
        List of dependent service names OR dict with DependsCondition objects.
    """
    dep_list = deployment.get("spec", {}).get("depends")
    depends_on: Dict[str, DependsCondition] = {}
    if dep_list is None:
        return depends_on

    for dep in dep_list:
        if dep.get("kind") != "deployment":
            continue

        dep_name = dep["nameOrGUID"]
        dependent_deployment = deployments.get(f"deployment:{dep_name}")
        if not dependent_deployment:
            continue

        # Find the associated package for the dependent deployment
        dep_pkg_meta = dependent_deployment.get("metadata", {}).get("depends", {})
        pkg = find_package(
            packages,
            name=dep_pkg_meta.get("nameOrGUID"),
            version=dep_pkg_meta.get("version"),
        )

        # Generate service names for each executable in the dependent package
        for exe in pkg.get("spec", {}).get("executables", []):
            service_name = f"{dep_name}_{exe['name']}"
            depends_on[service_name] = DependsCondition(
                # condition="service_completed_successfully" if use_conditions else "service_started"
            )

    return depends_on


def populate_healthcheck(exe: dict):
    probe = exe.get("livenessProbe")
    if not probe or not probe.get("exec", {}).get("command"):
        return None
    return HealthCheck(
        test=" ".join(probe["exec"]["command"]),
        timeout=f"{probe.get('timeoutSeconds', 30)}s",
        interval=f"{probe.get('periodSeconds', 10)}s",
        retries=probe.get("failureThreshold", 3),
    )

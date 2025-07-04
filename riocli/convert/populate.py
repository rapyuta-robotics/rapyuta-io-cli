from __future__ import annotations

import shlex
from typing import Dict, List, Any, Optional

from riocli.convert.defaults import get_roscore, get_default_volume_mounts
from riocli.convert.model import DockerCompose, Service, DependsCondition, HealthCheck
from riocli.convert.utils import (
    safe_get_nested,
    normalize_restart_policy,
    format_memory_limit,
    format_cpu_limit,
)

# Constants
VOLUME_PERMISSIONS = {
    755: "rw",
    777: "rw",
}


def populate(deployments: Dict[str, dict], packages: Dict[str, dict]) -> DockerCompose:
    """
    Converts a set of Kubernetes-style deployments and packages into a Docker Compose structure.

    Args:
        deployments: Dictionary of deployment definitions.
        packages: Dictionary of package definitions.

    Returns:
        DockerCompose object representing the final configuration.
    """
    services: Dict[str, Service] = {}

    # Check if ROS is enabled in any package (optimized with early exit)
    ros_enabled = _is_ros_enabled(deployments, packages)

    # Process deployments and create services
    for deployment in deployments.values():
        try:
            _process_deployment(
                deployment=deployment,
                deployments=deployments,
                packages=packages,
                services=services,
            )
        except (KeyError, ValueError) as e:
            # Log error but continue processing other deployments
            print(
                f"Warning: Skipping deployment {deployment.get('metadata', {}).get('name', 'unknown')}: {e}"
            )
            continue

    # Add ROS master service if needed
    if ros_enabled:
        services["ros-master"] = get_roscore()

    return DockerCompose(version="3", services=services)


def _is_ros_enabled(deployments: Dict[str, dict], packages: Dict[str, dict]) -> bool:
    """Check if ROS is enabled in any deployment package."""
    for deployment in deployments.values():
        try:
            pkg_dep = deployment["metadata"]["depends"]
            package = find_package(packages, pkg_dep["nameOrGUID"], pkg_dep["version"])
            if package.get("spec", {}).get("ros", {}).get("enabled", False):
                return True
        except (KeyError, ValueError):
            continue
    return False


def _process_deployment(
    deployment: dict,
    deployments: Dict[str, dict],
    packages: Dict[str, dict],
    services: Dict[str, Service],
) -> None:
    """Process a single deployment and add its services to the services dictionary."""
    dep_name = deployment["metadata"]["name"]
    pkg_dep = deployment["metadata"]["depends"]
    package = find_package(packages, pkg_dep["nameOrGUID"], pkg_dep["version"])

    # Get restart policy with normalization
    restart_policy = safe_get_nested(
        package, "spec", "device", "restart", default="always"
    )
    restart_policy = normalize_restart_policy(restart_policy)

    # Merge environment variables
    env = merge_env_vars(
        safe_get_nested(package, "spec", "environmentVars", default=[]),
        safe_get_nested(deployment, "spec", "envArgs", default=[]),
    )

    # Build volume mounts
    volume_mounts = build_volume_mounts(deployment)

    # Build dependencies
    depends_on = populate_depends_on(
        deployment=deployment, deployments=deployments, packages=packages
    )

    # Create services for each executable
    for exe in safe_get_nested(package, "spec", "executables", default=[]):
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
    exe_name = exe["name"]
    image = exe["docker"]["image"]
    limits = exe.get("limits", {})

    # Format resource limits using utility functions
    mem_limit = format_memory_limit(limits.get("memory"))
    cpu_limit = format_cpu_limit(limits.get("cpu"))

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
    service_volumes = get_default_volume_mounts()

    # Add custom volumes from deployment
    for volume in safe_get_nested(deployment, "spec", "volumes", default=[]):
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
    Wraps the command in a shell invocation if runAsBash is True.

    Args:
        exe: Executable dictionary from package spec.

    Returns:
        List of command arguments suitable for Docker Compose, or None if no command.
    """
    cmd_raw = exe.get("command")
    if not cmd_raw:
        return None

    run_as_bash = exe.get("runAsBash", False)

    # Convert command to string if it's a list
    cmd_str = " ".join(cmd_raw) if isinstance(cmd_raw, list) else str(cmd_raw).strip()

    # Return shell-wrapped command or split command
    if run_as_bash in (True, "true"):
        return ["bash", "-c", cmd_str]
    else:
        return shlex.split(cmd_str)


def find_package(packages: Dict[str, dict], name: str, version: str) -> dict:
    """
    Finds a package by name and version in the provided dictionary.

    Args:
        packages: All package definitions.
        name: Name of the package.
        version: Expected version.

    Returns:
        The matched package dictionary.

    Raises:
        KeyError: If package is not found.
        ValueError: If version mismatch occurs.
    """
    pkg = packages.get(f"package:{name}")
    if not pkg:
        raise KeyError(f"No Package found with name '{name}'")
    if str(pkg.get("metadata", {}).get("version")) != str(version):
        raise ValueError(
            f"Version mismatch: expected {version}, found {pkg['metadata'].get('version')}"
        )
    return pkg


def merge_env_vars(*env_vars_lists: List[Dict[str, Any]]) -> Dict[str, str]:
    """
    Merges multiple lists of environment variable definitions into a single dictionary.
    Later variables override earlier ones with the same name.

    Args:
        *env_vars_lists: Lists of environment variable dictionaries.

    Returns:
        Dictionary of environment variable name to value.
    """
    env = {}
    for vars_list in env_vars_lists:
        for var in vars_list:
            name = var.get("name")
            if name:
                # Convert value to string for consistency
                value = var.get("default") or var.get("value", "")
                env[name] = str(value) if value is not None else ""
    return env


def populate_depends_on(
    deployment: dict,
    deployments: Dict[str, dict],
    packages: Dict[str, dict],
) -> Dict[str, DependsCondition]:
    """
    Builds the depends_on relationships for a Docker Compose service
    based on other deployments it references.

    Args:
        deployment: The current deployment.
        packages: All package definitions.

    Returns:
        Dictionary of service name to DependsCondition.
    """
    depends_on = {}

    for dep in safe_get_nested(deployment, "spec", "depends", default=[]):
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
            depends_on[service_name] = DependsCondition()

    return depends_on


def populate_healthcheck(exe: dict) -> Optional[HealthCheck]:
    """
    Generates a Docker Compose healthcheck configuration from a livenessProbe.

    Args:
        exe: Executable dictionary from package spec.

    Returns:
        HealthCheck object or None if no valid probe is found.
    """
    probe = exe.get("livenessProbe")
    if not probe or not safe_get_nested(probe, "exec", "command"):
        return None

    return HealthCheck(
        test=" ".join(probe["exec"]["command"]),
        timeout=f"{probe.get('timeoutSeconds', 30)}s",
        interval=f"{probe.get('periodSeconds', 10)}s",
        retries=probe.get("failureThreshold", 3),
    )

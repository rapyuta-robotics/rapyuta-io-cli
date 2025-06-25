from typing import Dict, List, Any
from riocli.convert.model import (
    DockerCompose,
    Service,
    DependsCondition,
    HealthCheck,
)


def populate(deployments: Dict[str, dict], packages: Dict[str, dict]) -> DockerCompose:
    services: Dict[str, Service] = {}

    for deployment in deployments.values():
        dep_name = deployment["metadata"]["name"]
        pkg_dep = deployment["metadata"]["depends"]
        package = find_package(packages, pkg_dep["nameOrGUID"], pkg_dep["version"])

        restart_policy = package["spec"].get("device", {}).get("restart", "always")
        env = merge_env_vars(package["spec"].get("environmentVars", []))
        volume_mounts = build_volume_mounts(deployment)
        depends_on = populate_depends_on(
            deployment,
            deployments=deployments,
            packages=packages,
        )

        for exe in package["spec"]["executables"]:
            exe_name = exe["name"]
            image = exe["docker"]["image"]
            service_name = f"{dep_name}_{exe_name}"

            services[service_name] = Service(
                container_name=service_name,
                image=image,
                restart=restart_policy,
                environment=env,
                volumes=volume_mounts,
                depends_on=depends_on,
                command="{}".format(exe.get("command", "")),
                healthcheck=populate_healthcheck(exe),
            )

    return DockerCompose(version="3", services=services)


def build_volume_mounts(deployment: dict) -> list[Any]:
    """
    Builds a mapping from executable name to volume mount strings.
    Also populates the volumes_dict with named volumes if needed.
    """
    service_volumes = []
    volumes = deployment.get("spec", {}).get("volumes", {})

    for volume in volumes:
        mount_path = volume.get("mountPath")
        sub_path = volume.get("subPath")
        permissions = volume.get("perm")
        read_only = "r" if permissions in [755, 777] else "rw"

        if not (mount_path or sub_path):
            continue
        service_volume = "{}:{}:{}".format(mount_path, sub_path, read_only)
        service_volumes.append(service_volume)

    return service_volumes


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


def merge_env_vars(env_vars: List[Dict]) -> Dict[str, str]:
    return {
        env.get("name"): env.get("default", "") for env in env_vars if env.get("name")
    }


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
        use_conditions = dep.get("wait", False)
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
                condition="service_healthy" if use_conditions else "service_started"
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

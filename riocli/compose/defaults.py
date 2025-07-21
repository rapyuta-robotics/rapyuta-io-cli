from riocli.compose.model import Service

# Constants
DEFAULT_COMPOSE_FILENAME = "docker-compose.yaml"
DEVICE_RUNTIME = "device"
ROS_MASTER_IMAGE = "quay.io/rapyuta/ros-base-melodic:master"
ROS_MASTER_PORT = 1234
ROS_MASTER_CONTAINER_NAME = "roscore"
DEFAULT_VOLUME_MOUNTS = [
    "/opt/rapyuta/configs:/opt/rapyuta/configs:rslave",
    "/var/log/riouser:/var/log/riouser:rslave",
    "/var/log/rapyuta/deployments:/var/log/rapyuta/deployments:rslave",
    "/var/lib/docker/containers:/var/lib/docker/containers:rslave",
    "/dev:/dev:rslave",
]


def generate_roscore_service() -> Service:
    """
    Creates a ROS master service configuration.

    Returns:
        Service: Configured ROS master service
    """
    return Service(
        container_name=ROS_MASTER_CONTAINER_NAME,
        image=ROS_MASTER_IMAGE,
        pull_policy="if_not_present",
        restart="always",
        command=["roscore", "-p", str(ROS_MASTER_PORT)],
        network_mode="host",
    )

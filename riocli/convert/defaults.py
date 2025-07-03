from riocli.convert.model import Service

# Constants
ROS_MASTER_IMAGE = "quay.io/rapyuta/ros-base-melodic:master"
ROS_MASTER_PORT = 1234
ROS_MASTER_CONTAINER_NAME = "roscore"

# Default volume mappings (source, destination, mode)
DEFAULT_VOLUME_MAPPINGS = [
    ("/opt/rapyuta/configs", "/opt/rapyuta/configs", "rslave"),
    ("/var/log/riouser", "/var/log/riouser", "rslave"),
    ("/var/log/rapyuta/deployments", "/var/log/rapyuta/deployments", "rslave"),
    ("/var/lib/docker/containers", "/var/lib/docker/containers", "rslave"),
    ("/dev", "/dev", "rslave"),
]


def get_roscore() -> Service:
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
        command=f"roscore -p {ROS_MASTER_PORT}",
        network_mode="host",
    )


def get_default_volume_mounts() -> list:
    """
    Gets default volume mount strings for containers.

    Returns:
        list[str]: List of formatted volume mount strings
    """
    return [f"{src}:{dst}:{mode}" for src, dst, mode in DEFAULT_VOLUME_MAPPINGS]

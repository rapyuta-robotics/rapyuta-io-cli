from riocli.convert.model import Service

ROS_MASTER_IMAGE = "quay.io/rapyuta/ros-base-melodic:master"
DEFAULT_VOLUMES = [
    "/opt/rapyuta/configs",
    "/var/log/riouser",
    "/var/log/rapyuta/deployments",
    "/var/lib/docker/containers",
    "/dev",
]


def get_roscore():
    return Service(
        container_name="roscore",
        image=ROS_MASTER_IMAGE,
        pull_policy="if_not_present",
        restart="always",
        command="roscore -p 1234",
        network_mode="host",
    )

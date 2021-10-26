# Copyright 2021 Rapyuta Robotics
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
import click
from click_spinner import spinner
from rapyuta_io import ROSDistro
from rapyuta_io.clients.device import DevicePythonVersion, Device, DeviceRuntime

from riocli.config import new_client


@click.command('create')
@click.option('--description', type=str, help='Description of the device', default='')
@click.option('--runtime', help='Runtime of the Device', default='dockercompose',
              type=click.Choice(['preinstalled', 'dockercompose'], case_sensitive=False))
@click.option('--ros', help='ROS Distribution for the Device', default='melodic',
              type=click.Choice(['kinetic', 'melodic', 'noetic'], case_sensitive=False))
@click.option('--python', help='Python Version to use on the Device', default='3',
              type=click.Choice(['2', '3'], case_sensitive=False))
@click.option('--rosbag-mount-path', type=str, default='/opt/rapyuta/volumes/rosbag',
              help='Path to store recorded ROSBags (only dockercompose)')
@click.option('--catkin-workspace', default='/home/rapyuta/catkin_ws',
              help='Path to the Catkin Workspace (only preinstalled)')
@click.argument('device-name', type=str)
def create_device(
        device_name: str,
        description: str,
        runtime: str,
        ros: str,
        python: str,
        rosbag_mount_path: str,
        catkin_workspace: str,
) -> None:
    """
    Create a new device on the Platform
    """
    try:
        client = new_client()
        with spinner():
            python_version = DevicePythonVersion(python)
            ros_distro = ROSDistro(ros)
            runtime = DeviceRuntime(runtime)
            device = Device(name=device_name, description=description, runtime=runtime, ros_distro=ros_distro,
                            python_version=python_version, rosbag_mount_path=rosbag_mount_path,
                            ros_workspace=catkin_workspace)
            client.create_device(device)
        click.secho('Device created successfully!', fg='green')
    except Exception as e:
        click.secho(str(e), fg='red')
        exit(1)

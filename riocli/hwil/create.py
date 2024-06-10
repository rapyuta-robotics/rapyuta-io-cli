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
import time
import typing
import click
from click_spinner import spinner
from click_help_colors import HelpColorsCommand
from riocli.constants import Colors
from rapyuta_io.utils import ConflictError
from rapyuta_io.clients.device import DevicePythonVersion, Device, DeviceStatus
from riocli.utils import tabulate_data
from riocli.device.util import find_device_guid
from riocli.hwil.util import name_to_id

from riocli.config import new_client, new_hwil_client
from riocli.hwilclient.client import Client
from rapyuta_io import Client as v1Client
from riocli.utils.spinner import with_spinner


@click.command('create',
               cls=HelpColorsCommand,
               help_headers_color=Colors.YELLOW,
               help_options_color=Colors.GREEN,)
@click.option('--arch', 'arch', help='device family type',
              type=click.Choice(['amd64', 'arm64']), default='amd64')
@click.option('--os', 'os', help='type of os',
              type=click.Choice(['debian', 'ubuntu']), default='ubuntu')
@click.option('--codename', 'codename', help='code name of os',
              type=click.Choice(['bionic', 'focal', 'jammy', 'bullseye']), default='focal')
@click.option('--onboard', 'onboard', is_flag=True, type=bool, default=False)
@click.argument('device-name', type=str)
@with_spinner(text='Creating HWIL device...')
def create_device(
        device_name: str,
        arch: str,
        os: str,
        codename: str,
        onboard: bool,
) -> None:
    """
    Create a new virtual device on the cloud
    """
    try:
        client = new_client()
        hwil_client = new_hwil_client()
        with spinner():
            try:
                hwil_client.create_device(device_name, arch, os, codename)
                click.secho('HWIL Device created successfully!', fg='green')
            except ConflictError as c:
                click.secho('HWIL Device {} already exists in cluster!'.format(device_name), fg='green')

            if onboard:
                try:
                    device = Device(name=device_name, description='onboarded using hwil', ros_distro='melodic',
                                    runtime_docker=True, runtime_preinstalled=False,
                                    python_version=DevicePythonVersion.PYTHON3)
                    device = client.create_device(device)
                    click.secho('Device created successfully in rapyuta.io!', fg='green')
                    onboard_command = device.onboard_script().full_command()
                    _onboard_hwil_device(hwil_client=hwil_client, client=client, device_name=device_name,
                                         onboard_command=onboard_command,
                                         device_uuid=device.uuid)
                except ConflictError as c:
                    click.secho('Device {} already exists in rapyuta.io!'.format(device_name), fg='green')
                    device = client.get_device(device_id=find_device_guid(client, device_name))
                    if device.is_online() or device.status == DeviceStatus.INITIALIZING:
                        click.secho('Device {} already {} in rapyuta.io!'.format(device.status,
                                                                                 device_name), fg='green')
                        raise SystemExit(0)
                    _onboard_hwil_device(hwil_client=hwil_client, client=client, device_name=device_name,
                                         onboard_command=device.onboard_script().full_command(),
                                         device_uuid=device.uuid)

    except Exception as e:
        click.secho(str(e), fg='red')
        raise SystemExit(1)


@name_to_id
def _onboard_hwil_device(hwil_client: Client, client: v1Client, device_name: str, onboard_command: str,
                         device_id: int, device_uuid: str):
    try:
        hwil_client.poll_till_device_ready(device_id, sleep_interval=5, retry_limit=3)
        hwil_client.execute_cmd(device_id, onboard_command)
        for _ in range(10):
            device = client.get_device(device_uuid)
            if device.is_online():
                click.secho('Device {} came online in rapyuta.io!'.format(device_name), fg='green')
                return
            click.secho('Device {} state {}  in rapyuta.io!'.format(device_name, device.status), fg='green')
            time.sleep(20)
        click.secho('Device {} state {}  in rapyuta.io!'.format(device_name, device.status), fg='red')
    except Exception as e:
        click.secho(str(e), fg='red')
        raise SystemExit(1)


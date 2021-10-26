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
import typing

import click
from rapyuta_io.clients import Device

from riocli.config import new_client


@click.command('list')
def list_devices() -> None:
    """
    List all the devices in the selected Project
    """
    try:
        client = new_client()
        devices = client.get_all_devices()
        _display_device_list(devices, show_header=True)
    except Exception as e:
        click.secho(str(e), fg='red')
        exit(1)


def _display_device_list(devices: typing.List[Device], show_header: bool = True) -> None:
    if show_header:
        click.secho('{:<38} {:<28} {:15}'.format('Device ID', 'Name', 'Status'), fg='yellow')

    for device in devices:
        click.echo('{:38} {:<28} {:15}'.format(device.uuid, device.name, device.status))

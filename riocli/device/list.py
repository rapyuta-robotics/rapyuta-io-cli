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
from riocli.utils import tabulate_data


@click.command('list')
def list_devices() -> None:
    """
    List all the devices in the selected Project
    """
    try:
        client = new_client()
        devices = client.get_all_devices()
        devices = sorted(devices, key=lambda d: d.name.lower())
        _display_device_list(devices, show_header=True)
    except Exception as e:
        click.secho(str(e), fg='red')
        raise SystemExit(1)


def _display_device_list(devices: typing.List[Device], show_header: bool = True) -> None:
    headers = []
    if show_header:
        headers = ('Device ID', 'Name', 'Status')

    data = [[d.uuid, d.name, d.status] for d in devices]

    tabulate_data(data, headers)

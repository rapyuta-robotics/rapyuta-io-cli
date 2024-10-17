# Copyright 2024 Rapyuta Robotics
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
from click_help_colors import HelpColorsCommand
from rapyuta_io.clients import Device

from riocli.config import new_client
from riocli.constants import Colors
from riocli.utils import tabulate_data


@click.command(
    "list",
    cls=HelpColorsCommand,
    help_headers_color=Colors.YELLOW,
    help_options_color=Colors.GREEN,
)
def list_devices() -> None:
    """List all the devices in the current project."""
    try:
        client = new_client()
        devices = client.get_all_devices()
        devices = sorted(devices, key=lambda d: d.name.lower())
        _display_device_list(devices, show_header=True)
    except Exception as e:
        click.secho(str(e), fg=Colors.RED)
        raise SystemExit(1)


def _display_device_list(devices: typing.List[Device], show_header: bool = True) -> None:
    headers = []
    if show_header:
        headers = ("Device ID", "Name", "Status")

    data = [[d.uuid, d.name, d.status] for d in devices]

    tabulate_data(data, headers)

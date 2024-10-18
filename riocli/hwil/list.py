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

from riocli.config import new_hwil_client
from riocli.constants import Colors
from riocli.utils import tabulate_data


@click.command(
    "list",
    cls=HelpColorsCommand,
    help_headers_color=Colors.YELLOW,
    help_options_color=Colors.GREEN,
)
def list_devices() -> None:
    """Lists hardware-in-loop devices."""
    try:
        devices = new_hwil_client().list_devices()
        devices = sorted(devices, key=lambda d: d.name.lower())
        _display_device_list(devices, show_header=True)
    except Exception as e:
        click.secho(str(e), fg=Colors.RED)
        raise SystemExit(1)


def _display_device_list(devices: typing.List[dict], show_header: bool = True) -> None:
    headers = []
    if show_header:
        headers = ("ID", "Name", "Status", "Static IP", "Dynamic IP", "Flavor")

    data = [
        [d.id, d.name, d.status, d.static_ip, d.ip_address, d.flavor] for d in devices
    ]

    tabulate_data(data, headers)

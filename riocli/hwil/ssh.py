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
import os

import click
from click_help_colors import HelpColorsCommand

from riocli.config import new_hwil_client
from riocli.constants import Colors, Symbols
from riocli.hwil.util import name_to_id


@click.command(
    "ssh",
    cls=HelpColorsCommand,
    help_headers_color=Colors.YELLOW,
    help_options_color=Colors.GREEN,
)
@click.argument("device-name", required=True, type=str)
@name_to_id
def ssh(device_name: str, device_id: str, spinner=None) -> None:
    """SSH into a hardware-in-the-loop device.

    This command acts as a wrapper on top of the ``ssh`` command.
    It fetches the static IP address of the device and logs you in
    using the username configured for the device at the time of its
    creation. You will be prompted for the password which is also
    presented to you on the terminal.
    """
    try:
        device = new_hwil_client().get_device(device_id)

        if not device.get("static_ip"):
            click.secho(
                f"{Symbols.ERROR} Device does not have a static IP address",
                fg=Colors.RED,
            )
            raise SystemExit(1)

        click.secho(
            f"{Symbols.INFO} Enter this password when prompted: {device.password}",
            fg=Colors.BRIGHT_CYAN,
        )
        os.system(f'ssh {device.username}@{device["static_ip"]}')
    except Exception as e:
        click.secho(str(e), fg=Colors.RED)
        raise SystemExit(1)

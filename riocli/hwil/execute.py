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
import sys

import click
from click_help_colors import HelpColorsCommand

from riocli.config import new_hwil_client
from riocli.constants import Colors
from riocli.hwil.util import name_to_id, execute_command


@click.command(
    "execute",
    cls=HelpColorsCommand,
    help_headers_color=Colors.YELLOW,
    help_options_color=Colors.GREEN,
)
@click.argument("device-name", required=True, type=str)
@click.argument("command", required=True, type=str)
@name_to_id
def execute(device_name: str, device_id: str, command: str) -> None:
    """Execute a command on a hardware-in-the-loop device.

    Ensure that you wrap the command in quotes to avoid any issues.
    """
    try:
        code, stdout, stderr = execute_command(new_hwil_client(), device_id, command)
        sys.stdout.write(stdout)
        sys.stderr.write(stderr)
        sys.exit(code)
    except Exception as e:
        click.secho(str(e), fg=Colors.RED)
        raise SystemExit(1)

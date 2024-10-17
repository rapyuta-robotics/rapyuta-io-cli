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

import click
from click_help_colors import HelpColorsCommand
from munch import unmunchify

from riocli.config import new_hwil_client
from riocli.constants import Colors
from riocli.hwil.util import name_to_id
from riocli.utils import inspect_with_format


@click.command(
    "inspect",
    cls=HelpColorsCommand,
    help_headers_color=Colors.YELLOW,
    help_options_color=Colors.GREEN,
)
@click.option(
    "--format",
    "-f",
    "format_type",
    default="yaml",
    type=click.Choice(["json", "yaml"], case_sensitive=False),
)
@click.argument("device-name", type=str)
@name_to_id
def inspect_device(format_type: str, device_name: str, device_id: str) -> None:
    """Print the details of a hardware-in-the-loop device."""
    client = new_hwil_client()

    try:
        device = client.get_device(device_id)
        inspect_with_format(unmunchify(device), format_type)
    except Exception as e:
        click.secho(str(e), fg=Colors.RED)

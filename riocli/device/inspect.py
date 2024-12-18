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
from rapyuta_io.clients import Device

from riocli.config import new_client
from riocli.constants import Colors
from riocli.device.util import name_to_guid
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
    type=click.Choice(["json", "yaml"], case_sensitive=False),
    default="yaml",
)
@click.argument("device-name", type=str)
@name_to_guid
def inspect_device(format_type: str, device_name: str, device_guid: str) -> None:
    """Print the details of a device.

    You can specify the format of the output using the --format flag.
    The default format is yaml. You can choose between json and yaml.
    """
    try:
        client = new_client()
        device = client.get_device(device_id=device_guid)
        data = make_device_inspectable(device)
        inspect_with_format(data, format_type)
    except Exception as e:
        click.secho(str(e), fg=Colors.RED)


def make_device_inspectable(device: Device) -> dict:
    data = {}
    for key, val in device.items():
        if key.startswith("_") or key in ["deviceId"]:
            continue
        data[key] = val

    return data

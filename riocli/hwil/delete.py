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
from yaspin.api import Yaspin

from riocli.config import new_hwil_client
from riocli.constants import Colors, Symbols
from riocli.utils.spinner import with_spinner


@click.command(
    "delete",
    cls=HelpColorsCommand,
    help_headers_color=Colors.YELLOW,
    help_options_color=Colors.GREEN,
)
@click.argument("devices", type=str, nargs=-1)
@click.option(
    "--force",
    "-f",
    "--silent",
    "force",
    is_flag=True,
    default=False,
    help="Skip confirmation",
)
@with_spinner(text="Deleting device(s)...")
def delete_device(
    devices: typing.List,
    force: bool,
    spinner: Yaspin = None,
) -> None:
    """Delete one or more devices.

    You can specify the device names to delete using the
    device names as arguments. If you want to delete multiple
    devices, you can specify multiple device names separated
    by spaces.

    You can skip confirmation by using the ``--force`` or ``-f``
    or the ``--silent`` flag.

    Usage Examples:

        Delete a single device by name

            $ rio hwil delete my-device

        Delete multiple devices by name

            $ rio hwil delete my-device1 my-device2 my-device3
    """
    if not devices:
        spinner.text = click.style("No device names provided", fg=Colors.RED)
        spinner.red.fail(Symbols.ERROR)
        raise SystemExit(1)

    client = new_hwil_client()
    fetched = []

    try:
        fetched = client.list_devices()
    except Exception as e:
        spinner.text = click.style(f"Error fetching device(s): {str(e)}", fg=Colors.RED)
        spinner.red.fail(Symbols.ERROR)

    device_name_map = {name: None for name in devices}

    final = {d["id"]: d["name"] for d in fetched if d["name"] in device_name_map}

    if not final:
        spinner.text = click.style(
            f'No devices found with name(s): {", ".join(devices)}', fg=Colors.RED
        )
        spinner.red.fail(Symbols.ERROR)
        raise SystemExit(1)

    with spinner.hidden():
        if not force:
            click.confirm(
                f'Do you want to delete {", ".join(final.values())}?', abort=True
            )

    try:
        for device_id, device_name in final.items():
            spinner.text = f"Deleting device {device_name}..."
            client.delete_device(device_id)
        spinner.text = click.style("Device(s) deleted successfully!", fg=Colors.GREEN)
        spinner.green.ok(Symbols.SUCCESS)
    except Exception as e:
        spinner.text = click.style(f"Error deleting device(s): {str(e)}", fg=Colors.RED)
        spinner.red.fail(Symbols.ERROR)
        raise SystemExit(1)

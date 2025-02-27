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
import functools
from queue import Queue

import click
import requests
from click_help_colors import HelpColorsCommand
from rapyuta_io import Client
from rapyuta_io.clients.device import Device
from yaspin.api import Yaspin

from riocli.config import new_client
from riocli.constants import Colors, Symbols
from riocli.device.util import fetch_devices
from riocli.utils import tabulate_data
from riocli.utils.execute import apply_func_with_result
from riocli.utils.spinner import with_spinner


@click.command(
    "delete",
    cls=HelpColorsCommand,
    help_headers_color=Colors.YELLOW,
    help_options_color=Colors.GREEN,
)
@click.option(
    "--force", "-f", "--silent", is_flag=True, default=False, help="Skip confirmation"
)
@click.option(
    "-a", "--all", "delete_all", is_flag=True, default=False, help="Delete all devices"
)
@click.option(
    "--workers",
    "-w",
    help="Number of parallel workers for deleting devices. Defaults to 10.",
    type=int,
    default=10,
)
@click.argument("device-name-or-regex", type=str, default="")
@with_spinner(text="Deleting device...")
def delete_device(
    force: bool,
    workers: int,
    device_name_or_regex: str,
    delete_all: bool = False,
    spinner: Yaspin = None,
) -> None:
    """Delete one or more devices with a name or a regex pattern.

    You can specify a name or a regex pattern to delete one
    or more devices.

    If you want to delete all the device, then
    simply use the --all flag.

    If you want to delete devices without confirmation, then
    use the --force or --silent or -f

    Usage Examples:

      Delete a device by name

      $ rio device delete DEVICE_NAME

      Delete a device without confirmation

      $ rio device delete DEVICE_NAME --force

      Delete all device in the project

      $ rio device delete --all

      Delete devices using regex pattern

      $ rio device delete "DEVICE.*"
    """
    client = new_client()
    if not (device_name_or_regex or delete_all):
        spinner.text = "Nothing to delete"
        spinner.green.ok(Symbols.SUCCESS)
        return

    try:
        devices = fetch_devices(client, device_name_or_regex, delete_all)
    except Exception as e:
        spinner.text = click.style("Failed to delete device(s): {}".format(e), Colors.RED)
        spinner.red.fail(Symbols.ERROR)
        raise SystemExit(1) from e

    if not devices:
        spinner.text = "Device(s) not found"
        spinner.green.ok(Symbols.SUCCESS)
        return

    headers = ["Name", "Device ID", "Status"]
    data = [[d.name, d.uuid, d.status] for d in devices]

    with spinner.hidden():
        tabulate_data(data, headers)

    spinner.write("")

    if not force:
        with spinner.hidden():
            click.confirm("Do you want to delete above device(s)?", abort=True)
        spinner.write("")

    try:
        f = functools.partial(_delete_deivce, client)
        result = apply_func_with_result(
            f=f, items=devices, workers=workers, key=lambda x: x[0]
        )

        data, fg = [], Colors.GREEN
        success_count, failed_count = 0, 0

        for name, response in result:
            if response.status_code and response.status_code < 400:
                fg = Colors.GREEN
                icon = Symbols.SUCCESS
                success_count += 1
                msg = ""
            else:
                fg = Colors.RED
                icon = Symbols.ERROR
                failed_count += 1
                msg = get_error_message(response, name)

            data.append(
                [click.style(name, fg), click.style(icon, fg), click.style(msg, fg)]
            )

        with spinner.hidden():
            tabulate_data(data, headers=["Name", "Status", "Message"])

        spinner.write("")

        if failed_count == 0 and success_count == len(devices):
            spinner_text = click.style(
                "{} device(s) deleted successfully.".format(len(devices)), Colors.GREEN
            )
            spinner_char = click.style(Symbols.SUCCESS, Colors.GREEN)
        elif success_count == 0 and failed_count == len(devices):
            spinner_text = click.style("Failed to delete devices", Colors.YELLOW)
            spinner_char = click.style(Symbols.WARNING, Colors.YELLOW)
        else:
            spinner_text = click.style(
                "{}/{} devices deleted successfully".format(success_count, len(devices)),
                Colors.YELLOW,
            )
            spinner_char = click.style(Symbols.WARNING, Colors.YELLOW)

        spinner.text = spinner_text
        spinner.ok(spinner_char)
        raise SystemExit(failed_count)
    except Exception as e:
        spinner.text = click.style("Failed to delete devices: {}".format(e), Colors.RED)
        spinner.red.fail(Symbols.ERROR)
        raise SystemExit(1) from e


def _delete_deivce(
    client: Client,
    result: Queue,
    device: Device = None,
) -> None:
    response = requests.models.Response()
    try:
        response = client.delete_device(device_id=device.uuid)
        result.put((device["name"], response))
    except Exception:
        result.put((device["name"], response))


def get_error_message(response: requests.models.Response, name: str) -> str:
    if response.status_code:
        r = response.json()
        error = r.get("response", {}).get("error")

        if "deployments" in error:
            return "Device {0} has running deployments.".format(name)

    return ""

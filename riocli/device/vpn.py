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
import typing

import click
from click_help_colors import HelpColorsCommand

if sys.stdout.isatty():
    from yaspin import kbi_safe_yaspin as Spinner
else:
    from riocli.utils.spinner import DummySpinner as Spinner

from riocli.config import new_client
from riocli.constants import Colors, Symbols
from riocli.utils import tabulate_data


@click.command(
    "vpn",
    cls=HelpColorsCommand,
    help_headers_color=Colors.YELLOW,
    help_options_color=Colors.GREEN,
)
@click.option(
    "--devices",
    type=click.STRING,
    multiple=True,
    default=(),
    help="Device names to toggle VPN client",
)
@click.argument("enable", type=click.BOOL)
@click.option(
    "-f",
    "--force",
    "--silent",
    "silent",
    is_flag=True,
    type=click.BOOL,
    default=False,
    help="Skip confirmation",
)
@click.option(
    "--advertise-routes",
    is_flag=True,
    type=click.BOOL,
    default=False,
    help="Advertise subnets configured in project to VPN peers",
)
def toggle_vpn(
    devices: typing.List,
    enable: bool,
    silent: bool = False,
    advertise_routes: bool = False,
) -> None:
    """Enable or disable VPN client on the device.

    Optionally, you can configure the device to advertise a subnet
    if the project is configured with a subnet range. Please note
    that --advertise-routes is only a flag and does not provide you
    an option to specify the subnet range.

    You can specify the devices using their names or UUIDs using the
    --devices flag. If you do not specify any devices, the state will
    be applied to all online devices in the project.

    If you want to skip the confirmation prompt, use the --silent or
    --force or -f flag.

    Examples:

        1. Enable VPN on specific devices

            rio device vpn true --devices=amr01 --devices=edge01

        2. Enable VPN on all devices in the project

            rio device vpn true

        3. Disable VPN

            rio device vpn false

        4. Skip confirmation

            rio device vpn false --silent true
    """
    try:
        client = new_client()

        all_devices = client.get_all_devices()

        final = process_devices(all_devices, devices)

        click.secho(
            "\nSetting the state of VPN client = {} on "
            "the following devices\n".format(enable),
            fg="yellow",
        )

        print_final_devices(final)

        if not silent:
            if advertise_routes and len(final) > 1:
                msg = (
                    "\n{} More than one device in the project will advertise routes. "
                    "You may not want to do that. Please review the devices.".format(
                        Symbols.WARNING
                    )
                )
                click.secho(msg, fg="yellow")

            click.confirm("\nDo you want to proceed?", default=True, abort=True)

        click.echo("")  # Echo an empty line

        result = []
        with Spinner() as spinner:
            for device in final:
                spinner.text = "Updating VPN state on device {}".format(
                    click.style(device.name, bold=True, fg=Colors.CYAN)
                )
                r = client.toggle_features(
                    device.uuid,
                    [("vpn", enable)],
                    config={"vpn": {"advertise_routes": advertise_routes}},
                )
                result.append([device.name, r.get("status")])

        click.echo("")  # Echo an empty line

        tabulate_data(result, headers=["Device", "Status"])
    except Exception as e:
        click.secho(str(e), fg="red")
        raise SystemExit(1) from e


def process_devices(all_devices, devices) -> typing.List:
    if len(devices) == 0:
        click.secho(
            "\n(No devices specified. State will be applied"
            " to all online devices in the project)",
            fg="cyan",
        )
        return all_devices

    name_map, uuid_map = {}, {}
    for device in all_devices:
        name_map[device.name] = device
        uuid_map[device.uuid] = device

    final = []
    for device in devices:
        if device in name_map:
            final.append(name_map[device])
            continue
        if device in uuid_map:
            final.append(uuid_map[device])

    return final

def print_final_devices(final) -> None:
    data = [[device.uuid, device.name, device.status] for device in final]
    tabulate_data(data, headers=["UUID", "Name", "Status"])

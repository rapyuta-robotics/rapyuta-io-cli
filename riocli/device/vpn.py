# Copyright 2023 Rapyuta Robotics
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

from riocli.config import new_client
from riocli.utils import tabulate_data


@click.command(
    'vpn',
    cls=HelpColorsCommand,
    help_headers_color='yellow',
    help_options_color='green'
)
@click.option('--devices', type=click.STRING, multiple=True, default=(),
              help='Device names to toggle VPN client')
@click.argument('enable', type=click.BOOL)
@click.option('-f', '--force', '--silent', 'silent', is_flag=True, type=click.BOOL, default=False,
              help="Skip confirmation")
def toggle_vpn(devices: typing.List, enable: bool, silent: bool = False) -> None:
    """
    Enable or disable VPN client on the device

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

        online_devices = client.get_all_devices(online_device=True)

        final = process_devices(online_devices, devices)

        click.secho(
            "\nSetting the state of VPN client = {} on "
            "the following online devices\n".format(enable), fg='yellow')

        print_final_devices(final)

        if not silent:
            click.confirm(
                "\nDo you want to proceed?",
                default=True, abort=True)

        result = []
        for device in final:
            r = client.toggle_features(device.uuid, [('vpn', enable)])
            result.append([device.name, r.get('status')])

        click.echo("")  # Echo an empty line

        tabulate_data(result, headers=["Device", "Status"])
    except Exception as e:
        click.secho(str(e), fg='red')
        raise SystemExit(1) from e


def process_devices(online_devices, devices) -> typing.List:
    if len(devices) == 0:
        click.secho("\n(No devices specified. State will be applied"
                    " to all online devices in the project)", fg='cyan')
        return online_devices

    name_map, uuid_map = {}, {}
    for device in online_devices:
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

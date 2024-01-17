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
import sys
import typing

import click
from click_help_colors import HelpColorsCommand

if sys.stdout.isatty():
    from yaspin import kbi_safe_yaspin as Spinner
else:
    from riocli.utils.spinner import DummySpinner as Spinner

from riocli.config import new_client, new_v2_client
from riocli.constants import Colors, Symbols
from riocli.utils import tabulate_data

ALL = 'all'


@click.command(
    'vpn',
    cls=HelpColorsCommand,
    help_headers_color=Colors.YELLOW,
    help_options_color=Colors.GREEN
)
@click.option('--devices', type=click.STRING, multiple=True, default=(),
              help='Device names to toggle VPN client')
@click.argument('enable', type=click.BOOL)
@click.option('-f', '--force', '--silent', 'silent', is_flag=True,
              type=click.BOOL, default=False,
              help="Skip confirmation")
@click.option('--advertise-routes', type=click.STRING, default=ALL,
              help="Advertise subnets configured in project to VPN peers")
@click.pass_context
def toggle_vpn(
        ctx: click.Context,
        devices: typing.List,
        enable: bool,
        silent: bool = False,
        advertise_routes: str = 'all',
) -> None:
    """
    Enable or disable VPN client on the device

    Examples:

        1. Enable VPN on specific devices

            rio device vpn true --devices=amr01 --devices=edge01

        2. Enable VPN on all devices in the project

            rio device vpn true

        3. Enable VPN on a device and advertise all configured routes

            rio device vpn true --devices=edge01 --advertise-routes=all

        4. Enable VPN on a device and advertise a subset of routes

            rio device vpn true --devices=edge01 --advertise-routes='10.81.0.0/16,10.82.0.0/16'

        5. Disable VPN

            rio device vpn false

        6. Skip confirmation

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

        advertise_routes = get_advertise_routes(ctx, advertise_routes)

        if not silent:
            if advertise_routes and len(final) > 1:
                msg = ("\n{} More than one device in the project will advertise routes. "
                       "You may not want to do that. Please review the devices.".format(Symbols.WARNING))
                click.secho(msg, fg='yellow')

            click.confirm(
                "\nDo you want to proceed?",
                default=True, abort=True)

        click.echo("")  # Echo an empty line

        result = []
        with Spinner() as spinner:
            for device in final:
                spinner.text = 'Updating VPN state on device {}'.format(
                    click.style(device.name, bold=True, fg=Colors.CYAN))
                r = client.toggle_features(
                    device.uuid, [('vpn', enable)],
                    config={'vpn': {'advertise_routes': advertise_routes}}
                )
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


def get_advertise_routes(ctx: click.Context, advertise_routes: str) -> typing.List[str]:
    if advertise_routes != ALL:
        return advertise_routes.split(',')

    v2_client = new_v2_client()
    project = v2_client.get_project(ctx.obj.get('project_id'))

    return project['spec']['features']['vpn']['subnets']

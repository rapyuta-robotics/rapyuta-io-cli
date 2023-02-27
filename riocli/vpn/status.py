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

import click

from riocli.config import new_v2_client
from riocli.utils import tabulate_data
from riocli.vpn.util import (
    install_vpn_tools,
    is_tailscale_installed,
    is_tailscale_up,
    get_tailscale_status,
    is_vpn_enabled_in_project,
)


@click.command('status')
@click.option('--wide', '-w', is_flag=True, default=False,
              help='Print more details', type=bool)
@click.pass_context
def status(ctx: click.Context, wide: bool = False):
    """
    Check VPN status
    """
    try:
        if not is_tailscale_installed():
            click.confirm(click.style(
                'VPN tools are not installed. '
                'Do you want to install them now?',
                fg='yellow'), default=True, abort=True)
            install_vpn_tools()

        client = new_v2_client()

        if not is_vpn_enabled_in_project(
                client, ctx.obj.data.get('project_id')):
            click.secho('⚠ VPN is not enabled in the project. '
                        'Please ask the organization or project '
                        'creator to enable VPN', fg='yellow')
            raise SystemExit(1)

        click.secho('🛈 VPN is enabled in the project ({})'.format(
            ctx.obj.data.get('project_name')), fg='cyan')
        click.echo()

        if not is_tailscale_up():
            click.secho('You are not connected to the VPN', fg='green')
            return

        display_vpn_status(wide)

        click.secho('🛈 You are connected to the VPN.', fg='green')
    except Exception as e:
        click.secho(str(e), fg='red')
        raise SystemExit(1) from e


def display_vpn_status(wide: bool = False):
    s = get_tailscale_status()

    nodes = s.get('Peer', {})
    nodes.update({"me": s.get('Self')})

    headers = ['IP', 'Host Name', 'OS', 'Online', 'Active']

    if wide:
        headers.extend(['Relay', 'Joined', 'Last Active'])

    data = []
    for k, v in nodes.items():
        row = [
            ",".join(v.get('TailscaleIPs')),
            v.get('HostName'),
            v.get('OS'),
            v.get('Online'),
            v.get('Active'),
        ]

        if wide:
            row.extend([
                v.get('Relay'),
                v.get('Created'),
                v.get('LastSeen'),
            ])

        if k == 'me':
            row = [click.style(i, fg='bright_blue') for i in row]

        data.append(row)

    tabulate_data(data, headers)
    click.echo()
    click.secho('DNS Suffix: {}'.format(s.get('MagicDNSSuffix')))
    click.echo()

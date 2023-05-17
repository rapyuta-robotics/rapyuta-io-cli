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

from riocli.vpn.util import (
    is_tailscale_installed,
    install_vpn_tools,
    is_tailscale_up,
    get_tailscale_status,
    tailscale_ping
)


@click.command('ping-all')
@click.pass_context
def ping_all(ctx: click.Context):
    """
    Ping all the peers in the network
    """
    try:
        if not is_tailscale_installed():
            click.confirm(
                click.style('VPN tools are not installed. Do you want '
                            'to install them now?', fg='yellow'),
                default=True, abort=True)
            install_vpn_tools()

        if not is_tailscale_up():
            click.secho('You are not connected to the VPN', fg='green')
            return

        ping_all_peers()

        click.secho('✅ Ping complete.', fg='green')
    except Exception as e:
        click.secho(str(e), fg='red')
        raise SystemExit(1) from e


def ping_all_peers():
    s = get_tailscale_status()

    peers = s.get('Peer', {})

    for _, v in peers.items():
        click.secho("⌛ Pinging: {}...".format(v.get('HostName')), fg='blue')
        ips = v.get('TailscaleIPs')
        for ip in ips:
            tailscale_ping(ip)

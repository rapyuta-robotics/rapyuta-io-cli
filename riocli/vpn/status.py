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

from riocli.config import new_v2_client
from riocli.constants import Colors, Symbols
from riocli.utils import tabulate_data
from riocli.vpn.util import (
    get_tailscale_status,
    install_vpn_tools,
    is_tailscale_up,
    is_vpn_enabled_in_project,
)


@click.command(
    "status",
    cls=HelpColorsCommand,
    help_headers_color=Colors.YELLOW,
    help_options_color=Colors.GREEN,
)
@click.option(
    "--wide", "-w", is_flag=True, default=False, help="Print more details", type=bool
)
@click.pass_context
def status(ctx: click.Context, wide: bool = False):
    """Check VPN network status.

    You can view all the connected peers in the VPN network.

    User the ``--wide`` flag to view more details about the peers.
    """
    try:
        install_vpn_tools()

        client = new_v2_client()

        if not is_vpn_enabled_in_project(client, ctx.obj.data.get("project_id")):
            click.secho(
                "{} VPN is not enabled in the project. "
                "Please ask the organization or project "
                "creator to enable VPN".format(Symbols.WARNING),
                fg=Colors.YELLOW,
            )
            raise SystemExit(1)

        click.secho(
            "{} VPN is enabled in the project ({})".format(
                Symbols.INFO, ctx.obj.data.get("project_name")
            ),
            fg=Colors.CYAN,
        )
        click.echo()

        if not is_tailscale_up():
            click.secho(
                "{} You are not connected to the VPN".format(Symbols.WARNING),
                fg=Colors.YELLOW,
            )
            return

        display_vpn_status(wide)

        click.secho(
            "{} You are connected to the VPN.".format(Symbols.INFO), fg=Colors.GREEN
        )
    except Exception as e:
        click.secho(str(e), fg=Colors.RED)
        raise SystemExit(1) from e


def display_vpn_status(wide: bool = False):
    s = get_tailscale_status()

    nodes = s.get("Peer", {})
    nodes.update({"me": s.get("Self")})

    headers = ["IP", "DNS Name", "OS", "Online", "Active"]

    if wide:
        headers.extend(["Relay", "Joined", "Last Active"])

    data = []
    for k, v in nodes.items():
        row = [
            ",".join(v.get("TailscaleIPs")),
            # removesuffix() is available starting Python 3.9
            v.get("DNSName", "").replace("." + s.get("MagicDNSSuffix"), ""),
            v.get("OS"),
            v.get("Online"),
            v.get("Active"),
        ]

        if wide:
            row.extend(
                [
                    v.get("Relay"),
                    v.get("Created"),
                    v.get("LastSeen"),
                ]
            )

        if k == "me":
            row = [click.style(i, fg=Colors.BRIGHT_BLUE) for i in row]

        data.append(row)

    tabulate_data(data, headers)
    click.echo()
    click.secho("DNS Suffix: {}".format(s.get("MagicDNSSuffix")))
    click.echo()

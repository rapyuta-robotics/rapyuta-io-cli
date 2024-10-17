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
from yaspin.api import Yaspin

from riocli.constants import Colors, Symbols
from riocli.utils.spinner import with_spinner
from riocli.vpn.util import (
    get_tailscale_status,
    install_vpn_tools,
    is_tailscale_up,
    tailscale_ping,
)


@click.command(
    "ping-all",
    cls=HelpColorsCommand,
    help_headers_color=Colors.YELLOW,
    help_options_color=Colors.GREEN,
)
@click.pass_context
@with_spinner(text="Pinging all peers...")
def ping_all(ctx: click.Context, spinner: Yaspin = None):
    """Ping all the peers in the network.

    This command will ping all the peers in the network. It is
    convenient to check the connectivity of all the peers in the
    network. Also, it helps establish a direct connection with
    the peers.
    """
    try:
        with spinner.hidden():
            install_vpn_tools()

        if not is_tailscale_up():
            spinner.text = click.style(
                "You are not connected to the VPN", fg=Colors.YELLOW
            )
            spinner.yellow.ok(Symbols.WARNING)
            return

        ping_all_peers(spinner)

        spinner.text = click.style("Ping complete", fg=Colors.GREEN)
        spinner.green.ok(Symbols.SUCCESS)
    except Exception as e:
        spinner.text = click.style(str(e), fg=Colors.RED)
        spinner.red.fail(Symbols.ERROR)
        raise SystemExit(1) from e


def ping_all_peers(spinner: Yaspin):
    s = get_tailscale_status()

    peers = s.get("Peer", {})

    for _, v in peers.items():
        # Do not waste time pinging
        # offline nodes
        if not v.get("Online"):
            continue

        spinner.text = "Pinging: {}...".format(
            click.style(v.get("HostName"), italic=True)
        )
        ips = v.get("TailscaleIPs")
        for ip in ips:
            tailscale_ping(ip)

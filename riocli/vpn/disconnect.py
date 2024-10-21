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

from riocli.constants import Colors, Symbols
from riocli.vpn.util import (
    install_vpn_tools,
    is_tailscale_up,
    stop_tailscale,
    cleanup_hosts_file,
)


@click.command(
    "disconnect",
    cls=HelpColorsCommand,
    help_headers_color=Colors.YELLOW,
    help_options_color=Colors.GREEN,
)
@click.pass_context
def disconnect(ctx: click.Context):
    """Disconnect from the project's VPN network.

    Simply run the command to disconnect from the VPN network.

    If ``tailscale`` isn't found on the system then the command will
    prompt to install the required tools. While it may seem unnecessary
    to install the tools to disconnect, it is works as a safety measure
    to ensure that the user has the required tools to connect to the VPN.
    """
    try:
        install_vpn_tools()

        if is_tailscale_up() and not stop_tailscale():
            click.secho(
                "{} Failed to disconnect from VPN. "
                "Although, trying again may work.".format(Symbols.ERROR),
                fg=Colors.RED,
            )
            raise SystemExit(1)

        try:
            cleanup_hosts_file()
        except Exception as e:
            click.secho(
                f"{Symbols.WARNING} Could not clean " f"up hosts file: {str(e)}",
                fg=Colors.YELLOW,
            )

        click.secho(
            "{} You have been disconnected from the project's VPN".format(
                Symbols.SUCCESS
            ),
            fg=Colors.GREEN,
        )
    except Exception as e:
        click.secho(str(e), fg=Colors.RED)
        raise SystemExit(1) from e

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

from datetime import timedelta

import click
from click_help_colors import HelpColorsCommand

from riocli.config import get_config_from_context
from riocli.constants import Colors, Symbols
from riocli.vpn.util import create_binding, is_vpn_enabled_in_project


@click.command(
    "preauthkey",
    cls=HelpColorsCommand,
    help_headers_color=Colors.YELLOW,
    help_options_color=Colors.GREEN,
)
@click.option(
    "--expiry",
    "expiry_hours",
    type=int,
    default=24 * 90,
    show_default=True,
    help="Key validity in hours.",
)
@click.option(
    "--ephemeral",
    "ephemeral",
    is_flag=True,
    default=False,
    help="Issue an ephemeral key (node is removed from the network on disconnect).",
)
@click.option(
    "--print-all",
    "print_all",
    is_flag=True,
    default=False,
    help="Print the login server URL and ACL tag in addition to the key.",
)
@click.pass_context
def preauthkey(
    ctx: click.Context,
    expiry_hours: int,
    ephemeral: bool,
    print_all: bool,
) -> None:
    """Generate a pre-auth key for the current project's VPN.

    The key can be used to pre-configure the Tailscale client on a device
    via MDM without requiring interactive authentication. By default the key
    is non-ephemeral (the node persists in the network after disconnecting)
    and valid for 90 days.

    \b
    Example MDM tailscale up arguments:
      --auth-key=<key> --login-server=<url> --advertise-tags=<tag>

    Use --print-all to obtain all three values at once.
    """
    config = get_config_from_context(ctx)

    try:
        client = config.new_v2_client()

        if not is_vpn_enabled_in_project(client, config.project_guid):
            click.secho(
                f"{Symbols.WAITING} VPN is not enabled in the project. "
                "Please ask the organization or project creator to enable VPN.",
                fg=Colors.YELLOW,
            )
            raise SystemExit(1)

        binding = create_binding(
            ctx,
            delta=timedelta(hours=expiry_hours),
            ephemeral=ephemeral,
        )

        key = binding.get("HEADSCALE_PRE_AUTH_KEY")
        if not key:
            click.secho(
                f"{Symbols.ERROR} Failed to obtain a pre-auth key from the binding.",
                fg=Colors.RED,
            )
            raise SystemExit(1)

        if print_all:
            click.echo(f"Key:          {key}")
            click.echo(f"Login server: {binding.get('HEADSCALE_URL', '')}")
            click.echo(f"ACL tag:      {binding.get('HEADSCALE_ACL_TAG', '')}")
        else:
            click.echo(key)

    except SystemExit:
        raise
    except Exception as e:
        click.secho(f"{Symbols.ERROR} {e}", fg=Colors.RED)
        raise SystemExit(1) from e

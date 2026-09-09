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
from riocli.project.util import name_to_guid
from riocli.utils.context import get_root_context
from riocli.vpn.util import disconnect_vpn_for_switch


@click.command(
    "select",
    cls=HelpColorsCommand,
    help_headers_color=Colors.YELLOW,
    help_options_color=Colors.GREEN,
)
@click.argument("project-name", type=str)
@click.option(
    "--keep-vpn",
    is_flag=True,
    default=False,
    help="Keep the VPN connected after switching projects. Skips both "
    "VPN disconnect and hosts file cleanup.",
)
@name_to_guid
@click.pass_context
def select_project(
    ctx: click.Context,
    project_name: str,
    project_guid: str,
    keep_vpn: bool,
) -> None:
    """Switch to a different project in the current organization.

    The project will be set in the CLI's context and will be used
    for all the subsequent commands.

    By default, if a VPN is active it will be disconnected and the
    hosts file will be cleaned up. Use --keep-vpn to suppress this,
    for example when you have an active SSH session into a device on
    the previous project. You can also set ``auto_disconnect_vpn: false``
    in the CLI config file (``~/.config/rio-cli/config.json`` on Linux,
    ``~/Library/Application Support/rio-cli/config.json`` on macOS)
    to permanently suppress auto-disconnect.
    """
    ctx = get_root_context(ctx)

    previous_project_id = ctx.obj.current_project_id
    ctx.obj.data["project_id"] = project_guid
    ctx.obj.data["project_name"] = project_name
    ctx.obj.save()

    if project_guid != previous_project_id:
        disconnect_vpn_for_switch(ctx.obj, keep_vpn)

    click.secho(
        f"{Symbols.SUCCESS} Project {project_name} ({project_guid}) is selected!",
        fg=Colors.GREEN,
    )

    from riocli.ssh import refresh_ssh_cert

    refresh_ssh_cert(ctx)

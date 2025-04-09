# Copyright 2025 Rapyuta Robotics
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

import click
from click_help_colors import HelpColorsCommand

from riocli.auth.util import select_project
from riocli.constants import Colors, Symbols
from riocli.organization.util import name_to_guid
from riocli.utils.context import get_root_context
from riocli.vpn.util import cleanup_hosts_file


@click.command(
    "select",
    cls=HelpColorsCommand,
    help_headers_color=Colors.YELLOW,
    help_options_color=Colors.GREEN,
)
@click.argument("organization-name", type=str)
@click.option(
    "--interactive/--no-interactive",
    "--interactive/--silent",
    is_flag=True,
    type=bool,
    default=True,
    help="Make the selection interactive",
)
@click.pass_context
@name_to_guid
def select_organization(
    ctx: click.Context,
    organization_name: str,
    organization_guid: str,
    organization_short_id: str,
    interactive: bool,
) -> None:
    """Set the current organization.

    You can set the current organization using the name
    or the guid of the organization. You will be prompted
    to select a project if you are running the command in
    an interactive mode.

    To simply set the organization without selecting a project,
    use the `--no-interactive` or `--silent` flag.

    If your organization name has spaces, use quotes around the name.

    Usage Examples:

        Set the current organization to 'Platform JP Staging'

        $ rio organization select 'Platform JP Staging'

        Set the current organization to 'Platform JP Staging' without selecting a project

        $ rio organization select 'Platform JP Staging' --silent
    """
    ctx = get_root_context(ctx)

    if ctx.obj.data.get("organization_id") == organization_guid:
        click.secho(
            "You are already in the '{}' organization".format(organization_name),
            fg=Colors.GREEN,
        )
        return

    ctx.obj.data["organization_id"] = organization_guid
    ctx.obj.data["organization_name"] = organization_name
    ctx.obj.data["organization_short_id"] = organization_short_id

    if sys.stdout.isatty() and interactive:
        select_project(ctx.obj, organization=organization_guid)
    else:
        ctx.obj.data["project_id"] = ""
        ctx.obj.data["project_name"] = ""
        click.secho(
            "Your organization has been set to '{}'\n"
            "Please set your project with `rio project select PROJECT_NAME`".format(
                organization_name
            ),
            fg=Colors.GREEN,
        )

    ctx.obj.save()

    try:
        cleanup_hosts_file()
    except Exception as e:
        click.secho(
            f"{Symbols.WARNING} Failed to clean up hosts file: {str(e)}",
            fg=Colors.YELLOW,
        )

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

import click
from click_help_colors import HelpColorsCommand

from riocli.auth.util import select_project
from riocli.constants import Colors
from riocli.project.util import name_to_organization_guid
from riocli.utils.context import get_root_context


@click.command(
    'select',
    cls=HelpColorsCommand,
    help_headers_color=Colors.YELLOW,
    help_options_color=Colors.GREEN,
)
@click.argument('organization-name', type=str)
@click.option('--interactive/--no-interactive', '--interactive/--silent',
              is_flag=True, type=bool, default=True,
              help='Make the selection interactive')
@click.pass_context
@name_to_organization_guid
def select_organization(
        ctx: click.Context,
        organization_name: str,
        organization_guid: str,
        interactive: bool,
) -> None:
    """
    Sets the current organization to the one provided
    in the argument and prompts you to select a new project
    in the changed organization

    Example:

        rio organization select other-org
    """
    ctx = get_root_context(ctx)

    if ctx.obj.data['organization_id'] == organization_guid:
        click.secho("You are already in the '{}' organization".format(
            organization_name), fg=Colors.GREEN)
        return

    ctx.obj.data['organization_id'] = organization_guid
    ctx.obj.data['organization_name'] = organization_name

    if sys.stdout.isatty() and interactive:
        select_project(ctx.obj, organization=organization_guid)
    else:
        click.secho(
            "Your organization has been set to '{}'".format(organization_name),
            fg=Colors.GREEN)

    ctx.obj.save()

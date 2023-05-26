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
from click_help_colors import HelpColorsCommand

from riocli.constants import Colors, Symbols
from riocli.project.util import name_to_guid
from riocli.utils.context import get_root_context


@click.command(
    'select',
    cls=HelpColorsCommand,
    help_headers_color=Colors.YELLOW,
    help_options_color=Colors.GREEN,
)
@click.argument('project-name', type=str)
@name_to_guid
@click.pass_context
def select_project(
        ctx: click.Context,
        project_name: str,
        project_guid: str,
) -> None:
    """
    Sets the given project in the CLI context. All other resources use this project to act upon.
    """
    ctx = get_root_context(ctx)

    ctx.obj.data['project_id'] = project_guid
    ctx.obj.data['project_name'] = project_name
    ctx.obj.save()

    click.secho('{} Project {} ({}) is selected!'.format(
        Symbols.SUCCESS,
        project_name,
        project_guid),
        fg=Colors.GREEN)

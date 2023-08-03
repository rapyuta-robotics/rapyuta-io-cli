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
from riocli.organization.utils import get_organization_details
from riocli.utils import tabulate_data
from riocli.utils.context import get_root_context


@click.command(
    'users',
    cls=HelpColorsCommand,
    help_headers_color=Colors.YELLOW,
    help_options_color=Colors.GREEN,
)
@click.pass_context
def list_users(ctx: click.Context) -> None:
    """
    Lists all users in the organization.
    """
    ctx = get_root_context(ctx)

    try:
        organization = get_organization_details(ctx.obj.data['organization_id'])
    except Exception as e:
        click.secho('{} Failed to get organization details'.format(Symbols.ERROR), fg=Colors.RED)
        raise SystemExit(1) from e

    users = organization.get('users')
    users.sort(key=lambda u: u['emailID'])

    data = [[
        u['guid'],
        '{} {}'.format(u.get('firstName', '-'), u.get('lastName', '-')),
        u['emailID'],
        u['state'],
    ] for u in users]

    tabulate_data(data, headers=['GUID', 'Name', 'EmailID', 'Status'])

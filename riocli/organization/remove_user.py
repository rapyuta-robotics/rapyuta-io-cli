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
from email_validator import EmailNotValidError, validate_email

from riocli.constants import Colors, Symbols
from riocli.organization.utils import remove_user_from_org
from riocli.utils.context import get_root_context


@click.command(
    'remove-user',
    cls=HelpColorsCommand,
    help_headers_color=Colors.YELLOW,
    help_options_color=Colors.GREEN,
)
@click.argument('user-email', type=str)
@click.pass_context
def remove_user(ctx: click.Context, user_email: str) -> None:
    """
    Remove a user from the current organization
    """
    ctx = get_root_context(ctx)

    try:
        validate_email(user_email)
    except EmailNotValidError as e:
        click.secho('{} {} is not a valid email address'.format(Symbols.ERROR, user_email), fg=Colors.RED)
        raise SystemExit(1) from e

    try:
        remove_user_from_org(ctx.obj.data['organization_id'], user_email)
        click.secho('{} User removed successfully.'.format(Symbols.SUCCESS), fg=Colors.GREEN)
    except Exception as e:
        click.secho('{} Failed to remove user: {}'.format(Symbols.ERROR, e), fg=Colors.RED)
        raise SystemExit(1) from e

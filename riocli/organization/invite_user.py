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
from email_validator import EmailNotValidError, validate_email

from riocli.constants import Colors, Symbols
from riocli.organization.utils import invite_user_to_org
from riocli.utils.context import get_root_context


@click.command(
    "invite-user",
    cls=HelpColorsCommand,
    help_headers_color=Colors.YELLOW,
    help_options_color=Colors.GREEN,
)
@click.argument("user-email", type=str)
@click.pass_context
def invite_user(ctx: click.Context, user_email: str) -> None:
    """Invite a new user to the current organization.

    If the user does not have a rapyuta.io account, they will
    receive an email with an invitation to join the organization.
    If the user already has an account, they will be added to
    the organization.

    Usage Examples:

      Add a new user to the organization

      $ rio organization invite-user user@email.com
    """
    ctx = get_root_context(ctx)

    try:
        validate_email(user_email)
    except EmailNotValidError as e:
        click.secho(
            "{} {} is not a valid email address".format(Symbols.ERROR, user_email),
            fg=Colors.RED,
        )
        raise SystemExit(1) from e

    try:
        invite_user_to_org(ctx.obj.data["organization_id"], user_email)
        click.secho(
            "{} User invited successfully.".format(Symbols.SUCCESS), fg=Colors.GREEN
        )
    except Exception as e:
        click.secho(
            "{} Failed to invite user: {}".format(Symbols.ERROR, e), fg=Colors.RED
        )
        raise SystemExit(1) from e

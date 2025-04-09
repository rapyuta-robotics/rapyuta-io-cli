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

from typing import List
import click
from click_help_colors import HelpColorsCommand
from email_validator import EmailNotValidError, validate_email
from munch import Munch
from yaspin.core import Yaspin

from riocli.config import get_config_from_context, new_v2_client
from riocli.constants import Colors, Symbols
from riocli.utils.context import get_root_context
from riocli.utils.spinner import with_spinner


@click.command(
    "add-user",
    cls=HelpColorsCommand,
    help_headers_color=Colors.YELLOW,
    help_options_color=Colors.GREEN,
)
@click.option(
    "--role",
    type=click.Choice(["admin", "viewer"]),
    default="viewer",
    help="Password for the rapyuta.io account",
)
@click.argument("user-email", type=str, nargs=-1)
@click.pass_context
@with_spinner(text="Adding users...")
def add_user(
    ctx: click.Context,
    user_email: List[str],
    role: str,
    spinner: Yaspin,
) -> None:
    """Add a user to the current organization.

    After the user signs-up, admins can add them to the organization.

    Usage Examples:

      Add a new user to the organization

      $ rio organization add-user user@email.com

      Add multiple users to the organization

      $ rio organization add-user user1@email.com user2@email.com

      Add a new user with admin role to the organization

      $ rio organization add-user --role admin user@email.com

    """
    add_user_to_organization(ctx, user_email, role, spinner)


@click.command(
    "invite-user",
    cls=HelpColorsCommand,
    help_headers_color=Colors.YELLOW,
    help_options_color=Colors.GREEN,
    hidden=True,
)
@click.option(
    "--role",
    type=click.Choice(["admin", "viewer"]),
    default="viewer",
    help="Password for the rapyuta.io account",
)
@click.argument("user-email", type=str, nargs=-1)
@click.pass_context
@with_spinner(text="Adding users...")
def invite_user(
    ctx: click.Context,
    user_email: List[str],
    role: str,
    spinner: Yaspin,
) -> None:
    """Add a user to the current organization.

    After the user signs-up, admins can add them to the organization.

    Usage Examples:

      Add a new user to the organization

      $ rio organization invite-user user@email.com

      Add multiple users to the organization

      $ rio organization invite-user user1@email.com user2@email.com

      Add a new user with admin role to the organization

      $ rio organization invite-user --role admin user@email.com

    """
    add_user_to_organization(ctx, user_email, role, spinner)


def add_user_to_organization(
    ctx: click.Context,
    user_emails: List[str],
    role: str,
    spinner: Yaspin,
) -> None:
    if len(user_emails) == 0:
        spinner.text = click.style(
            "No user specified.", fg=Colors.RED
        )
        spinner.red.fail(Symbols.ERROR)
        raise SystemExit(1)

    for user_email in user_emails:
        try:
            validate_email(user_email)
        except EmailNotValidError as e:
            spinner.text = click.style(
                "{} is not a valid email address".format(user_email), fg=Colors.RED
            )
            spinner.red.fail(Symbols.ERROR)
            raise SystemExit(1) from e

    ctx = get_root_context(ctx)
    config = get_config_from_context(ctx)

    try:
        client = new_v2_client(config_inst=config)
        organization = client.get_organization(organization_guid=config.organization_guid)
        update = add_user_emails(organization, user_emails, role)
        if not update:
            spinner.text = click.style(
                "Users are already part of the organization.", fg=Colors.YELLOW
            )
            spinner.yellow.ok(Symbols.INFO)
            return

        client.update_organization(
            organization_guid=config.organization_guid,
            data=organization,
        )

        spinner.text = click.style("Users added successfully.", fg=Colors.GREEN)
        spinner.green.ok(Symbols.SUCCESS)
    except Exception as e:
        spinner.text = click.style("Failed to add users: {}".format(e), fg=Colors.RED)
        spinner.red.fail(Symbols.ERROR)
        raise SystemExit(1) from e


def add_user_emails(organization: Munch, user_emails: List[str], role: str) -> bool:
    update = False
    existing_emails = map(lambda x: x.emailID, organization.spec.users)

    for email in user_emails:
        if email not in existing_emails:
            update = True
            organization.spec.users.append(
                {
                    "emailID": email,
                    "roleInOrganization": role,
                }
            )

    return update

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
    "remove-user",
    cls=HelpColorsCommand,
    help_headers_color=Colors.YELLOW,
    help_options_color=Colors.GREEN,
)
@click.argument("user-email", type=str, nargs=-1)
@click.pass_context
@with_spinner(text="Removing users...")
def remove_user(
    ctx: click.Context,
    user_email: List[str],
    spinner: Yaspin,
) -> None:
    """Remove a user from the current organization."""
    if len(user_email) == 0:
        spinner.text = click.style(
            "No user specified.", fg=Colors.RED
        )
        spinner.red.fail(Symbols.ERROR)
        raise SystemExit(1)


    for email in user_email:
        try:
            validate_email(email)
        except EmailNotValidError as e:
            spinner.text = click.style(
                "{} is not a valid email address".format(email), fg=Colors.RED
            )
            spinner.red.fail(Symbols.ERROR)
            raise SystemExit(1) from e

    ctx = get_root_context(ctx)
    config = get_config_from_context(ctx)

    try:
        client = new_v2_client(config_inst=config)
        organization = client.get_organization(organization_guid=config.organization_guid)
        update = remove_user_emails(organization, user_email)
        if not update:
            spinner.text = click.style(
                "Users are not part of the organization.", fg=Colors.YELLOW
            )
            spinner.yellow.ok(Symbols.INFO)
            return

        client.update_organization(
            organization_guid=config.organization_guid,
            data=organization,
        )
        spinner.text = click.style("Users removed successfully.", fg=Colors.GREEN)
        spinner.green.ok(Symbols.SUCCESS)
    except Exception as e:
        spinner.text = click.style("Failed to remove users: {}".format(e), fg=Colors.RED)
        spinner.red.fail(Symbols.ERROR)
        raise SystemExit(1) from e


def remove_user_emails(organization: Munch, user_emails: List[str]) -> bool:
    update = False
    updated_users = []

    for user in organization.spec.users:
        if user.emailID in user_emails:
            update = True
            continue

        updated_users.append(user)

    organization.spec.users = updated_users

    return update

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

from riocli.config import get_config_from_context
from riocli.constants import Colors, Symbols
from riocli.project.util import name_to_guid
from riocli.utils.selector import show_selection


@click.command(
    "update-owner",
    cls=HelpColorsCommand,
    help_headers_color=Colors.YELLOW,
    help_options_color=Colors.GREEN,
)
@click.argument("project-name", type=str, required=True)
@click.option("--user-email", type=str, help="Email of the new owner")
@name_to_guid
@click.pass_context
def update_owner(
    ctx: click.Context,
    project_name: str,
    project_guid: str,
    user_email: str,
) -> None:
    """
    Update the owner of the project.

    The command will show an interactive list of users in the project if
    you do not specify ``--user-email.`` You can select the new owner from the list.

    Usage Examples:

        Update the owner of the project to a specific user

            $ rio project update-owner PROJECT --user-email user@email.com
    """
    config = get_config_from_context(ctx)
    client = config.new_v2_client(with_project=False)

    try:
        project = client.get_project(project_guid)
    except Exception as e:
        click.secho(
            "{} Failed to fetch project: {}".format(Symbols.ERROR, e), fg=Colors.RED
        )
        raise SystemExit(1)

    project_users = project.spec.users

    user_guid = None

    if user_email:
        try:
            validate_email(user_email)
        except EmailNotValidError as e:
            click.secho(
                "{} {} is not a valid email address".format(Symbols.ERROR, user_email),
                fg=Colors.RED,
            )
            raise SystemExit(1) from e

        for u in project_users:
            if u["emailID"] == user_email:
                user_guid = u["userGUID"]
                break
    else:
        ranger = {
            u["userGUID"]: "{} {} ({})".format(
                u["firstName"], u["lastName"], u["emailID"]
            )
            for u in project_users
        }
        user_guid = show_selection(
            ranger,
            header="Select a new project owner:",
            prompt="Select",
            show_keys=False,
            highlight_item=project.metadata.creatorGUID,
        )

    if user_guid is None:
        click.secho("{} User not found in project".format(Symbols.ERROR), fg=Colors.RED)
        raise SystemExit(1)

    try:
        client.update_project_owner(project_guid, user_guid)
        click.secho(
            "{} Owner updated successfully".format(Symbols.SUCCESS), fg=Colors.GREEN
        )
    except Exception as e:
        click.secho(
            "{} Failed to update owner: {}".format(Symbols.ERROR, e), fg=Colors.RED
        )
        raise SystemExit(1)

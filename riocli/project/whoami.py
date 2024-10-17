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

from riocli.config import Configuration
from riocli.constants import Colors
from riocli.exceptions import LoggedOut
from riocli.project.util import name_to_guid

ADMIN_ROLE = "admin"


@click.command(
    "whoami",
    cls=HelpColorsCommand,
    help_headers_color=Colors.YELLOW,
    help_options_color=Colors.GREEN,
)
@click.option("-p", "--project-name", type=str)
@name_to_guid
@click.pass_context
def whoami(ctx: click.Context, project_name: str, project_guid: str) -> None:
    """Find your role in a project.

    If you do not specify the project name, the command will use the project
    set in the CLI context.
    """
    if not ctx.obj.data.get("email_id"):
        raise LoggedOut

    try:
        role = find_role(ctx.obj, project_guid)
        click.echo(role)
    except SystemExit as e:
        click.secho(str(e), fg=Colors.RED)
        raise SystemExit(1) from e


def find_role(
    config: Configuration,
    project_guid: str = None,
) -> str:
    """
    Find the role of the user in the project.

    :param config: Configuration object
    :param project_guid: GUID of the project

    :return: Role of the user in the project
    :raises: SystemExit
    """
    v1_client = config.new_client()
    v2_client = config.new_v2_client()

    # The user email comes from the config
    user_email = config.data.get("email_id")
    if not user_email:
        raise ValueError("User email cannot be found in the config.")

    # Default to the config values if not provided
    if not project_guid:
        project_guid = config.data.get("project_id")

    if not project_guid:
        raise ValueError("Project GUID cannot be found.")

    try:
        project = v2_client.get_project(project_guid)
    except Exception as e:
        raise e

    role = None

    # If user is present in the users list, check if they are and admin
    for user in project.spec.get("users", []):
        if user["emailID"] == user_email:
            role = user["role"]
            break

    if role and role == ADMIN_ROLE:
        return role

    # Else, the membership may be via a group. Lookup the groups the user
    # has access to and compare them with the list of groups where the project
    # is included.
    try:
        user_groups = v1_client.list_usergroups(project.metadata.get("organizationGUID"))
        user_groups = {g.name: True for g in user_groups}
    except Exception as e:
        raise e

    for group in project.spec.get("userGroups", []):
        if group["name"] not in user_groups:
            continue

        # If the user is part of a group that has admin access then no
        # need to check further.
        if role != ADMIN_ROLE and group["role"] == ADMIN_ROLE:
            return ADMIN_ROLE

        role = group["role"]

    if not role:
        raise Exception("User does not have access to the project")

    return role

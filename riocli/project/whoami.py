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

from riocli.config import Configuration, get_config_from_context
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
    config = get_config_from_context(ctx)

    if not config.data.get("email_id"):
        raise LoggedOut

    try:
        role = find_role(config, project_guid)
        click.echo(role)
    except SystemExit as e:
        click.secho(str(e), fg=Colors.RED)
        raise SystemExit(1) from e


def find_role(
    config: Configuration,
    project_guid: str | None = None,
) -> list[str]:
    """
    Find the role of the user in the project.

    :param config: Configuration object
    :param project_guid: GUID of the project

    :return: Role of the user in the project
    :raises: SystemExit
    """
    v2_client = config.new_v2_client()

    # Default to the config values if not provided
    if project_guid is None:
        project_guid = config.data.get("project_id")

    user = v2_client.get_myself()

    for project in user.spec.projects:
        if project.guid == project_guid:
            return project.role_names

    raise Exception("User does not have access to the project")

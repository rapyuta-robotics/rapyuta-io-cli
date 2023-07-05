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
import os

import click
from rapyuta_io import Client
from rapyuta_io.clients.rip_client import AuthTokenLevel
from rapyuta_io.utils import UnauthorizedError

from riocli.config import Configuration
from riocli.constants import Colors, Symbols
from riocli.project.util import find_project_guid, find_organization_guid
from riocli.utils.selector import show_selection
from riocli.utils.spinner import with_spinner

TOKEN_LEVELS = {
    0: AuthTokenLevel.LOW,
    1: AuthTokenLevel.MED,
    2: AuthTokenLevel.HIGH
}


def select_organization(
        config: Configuration,
        organization: str = None,
) -> str:
    """
    Launches the org selection prompt by listing all the orgs that the user is a part of.

    Sets the choice in the given configuration.
    """
    client = config.new_client(with_project=False)

    org_guid = None

    if organization:
        org_guid = organization if organization.startswith(
            'org-') else find_organization_guid(client, name=organization)

    # fetch user organizations and sort them on their name
    organizations = client.get_user_organizations()
    organizations = sorted(organizations, key=lambda org: org.name.lower())

    org_map = {o.guid: o.name for o in organizations}

    if not org_guid:
        org_guid = show_selection(org_map, "Select an organization:")

    if org_guid and org_guid not in org_map:
        click.secho('invalid organization guid', fg=Colors.RED)
        raise SystemExit(1)

    config.data['organization_id'] = org_guid
    config.data['organization_name'] = org_map[org_guid]

    return org_guid


def select_project(
        config: Configuration,
        project: str = None,
        organization: str = None,
) -> None:
    """
    Launches the project selection prompt by listing all the projects.

    Sets the choice in the given configuration.
    """
    client = config.new_v2_client(with_project=False)

    project_guid = None
    if project:
        project_guid = (project if project.startswith('project-') else
                        find_project_guid(client, project,
                                          organization=organization))

    projects = client.list_projects(organization_guid=organization)
    if len(projects) == 0:
        config.data['project_id'] = ""
        config.data['project_name'] = ""
        click.secho("There are no projects in this organization",
                    fg=Colors.BLACK, bg=Colors.WHITE)
        return

    # Sort projects based on their names for an easier selection
    projects = sorted(projects, key=lambda p: p.metadata.name.lower())
    project_map = dict()

    for project in projects:
        project_map[project.metadata.guid] = project.metadata.name

    if not project_guid:
        project_guid = show_selection(
            project_map, header='Select the project to activate')

    config.data['project_id'] = project_guid
    config.data['project_name'] = project_map[project_guid]

    confirmation = "Your project has been set to '{}' in the organization '{}'".format(
        config.data['project_name'], config.data['organization_name'],
    )

    click.secho(confirmation, fg=Colors.GREEN)


@with_spinner(text='Fetching token...')
def get_token(
        email: str,
        password: str,
        level: int = 1,
        spinner=None,
) -> str:
    """
    Generates a new token using email and password.
    """
    config = Configuration()
    if 'environment' in config.data:
        os.environ['RIO_CONFIG'] = config.filepath

    try:
        token = Client.get_auth_token(
            email, password, TOKEN_LEVELS[level])
        return token
    except UnauthorizedError as e:
        spinner.text = click.style("incorrect email/password", fg=Colors.RED)
        spinner.red.fail(Symbols.ERROR)
        raise SystemExit(1) from e
    except Exception as e:
        click.style(str(e), fg=Colors.RED)
        spinner.red.fail(Symbols.ERROR)
        raise SystemExit(1) from e


@with_spinner(text='Validating token...')
def validate_token(token: str, spinner=None) -> bool:
    """Validates an auth token."""
    config = Configuration()
    if 'environment' in config.data:
        os.environ['RIO_CONFIG'] = config.filepath

    client = Client(auth_token=token)

    try:
        user = client.get_authenticated_user()
        spinner.text = click.style(
            'Token belongs to user {}'.format(user.email_id),
            fg=Colors.CYAN)
        spinner.ok(Symbols.INFO)
        return True
    except UnauthorizedError:
        spinner.text = click.style("incorrect auth token", fg=Colors.RED)
        spinner.red.fail(Symbols.ERROR)
        return False
    except Exception as e:
        spinner.text = click.style(str(e), fg=Colors.RED)
        spinner.red.fail(Symbols.ERROR)
        return False

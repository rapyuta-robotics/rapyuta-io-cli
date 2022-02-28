# Copyright 2021 Rapyuta Robotics
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
from click_spinner import spinner
from rapyuta_io import Client
from rapyuta_io.utils import UnauthorizedError

from riocli.config import Configuration
from riocli.utils.selector import show_selection


def select_project(config: Configuration) -> str:
    """
    Launches the project selection prompt by listing all the projects.
    Sets the choice in the given configuration.
    """
    client = config.new_client(with_project=False)
    projects = client.list_projects()

    project_map = dict()
    for project in projects:
        project_map[project.guid] = project.name

    choice = show_selection(project_map, header='Select the project to activate')
    config.data['project_id'] = choice


def get_token(email: str, password: str) -> str:
    """
    Generates a new token using email and password.
    """
    config = Configuration()
    if 'environment' in config.data:
        os.environ['RIO_CONFIG'] = config.filepath

    try:
        with spinner():
            token = Client.get_auth_token(email, password)
        return token
    except UnauthorizedError:
        click.secho("incorrect email/password", fg='red')
        exit(1)
    except Exception as e:
        click.secho(e, fg='red')
        exit(1)

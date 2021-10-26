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
import click
from click_spinner import spinner
from rapyuta_io.clients.project import Project

from riocli.config import new_client


@click.command('create')
@click.argument('project-name', type=str)
def create_project(project_name: str) -> None:
    """
    Creates a new project
    """
    try:
        client = new_client(with_project=False)
        with spinner():
            project_obj = Project(project_name)
            project = client.create_project(project_obj)
        click.secho('Project {} ({}) created successfully!'.
                    format(project.name, project.guid),
                    fg='green')
    except Exception as e:
        click.secho(str(e), fg='red')
        exit(1)

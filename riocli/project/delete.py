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

from riocli.config import new_client
from riocli.project.util import name_to_guid


@click.command('delete')
@click.option('--force', '-f', 'force', is_flag=True, help='Skip confirmation')
@click.argument('project-name', type=str)
@name_to_guid
def delete_project(force: bool, project_name: str, project_guid: str) -> None:
    """
    Deletes the project from the Platform
    """
    if not force:
        click.confirm('Deleting project {} ({})'.format(project_name, project_guid), abort=True)

    try:
        client = new_client(with_project=False)
        with spinner():
            client.delete_project(project_guid)
        click.secho('Project deleted successfully!', fg='green')
    except Exception as e:
        click.secho(str(e), fg='red')
        exit(1)

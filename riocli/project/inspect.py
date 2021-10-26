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
from rapyuta_io import Project
from rapyuta_io.clients.project import User

from riocli.config import new_client
from riocli.project.util import name_to_guid
from riocli.utils import inspect_with_format


@click.command('inspect')
@click.option('--format', '-f', 'format_type', default='yaml',
              type=click.Choice(['json', 'yaml'], case_sensitive=False))
@click.argument('project-name', type=str)
@name_to_guid
def inspect_project(format_type: str, project_name: str, project_guid: str) -> None:
    """
    Inspect the project resource
    """
    try:
        client = new_client(with_project=False)
        project = client.get_project(project_guid)
        data = make_project_inspectable(project)
        inspect_with_format(data, format_type)
    except Exception as e:
        click.secho(str(e), fg='red')
        exit(1)


def make_project_inspectable(obj: Project) -> dict:
    user_data = []
    for user in obj.users:
        user_data.append(make_user_inspectable(user))

    return {
        'created_at': obj.created_at,
        'updated_at': obj.updated_at,
        'creator': obj.creator,
        'deleted_at': obj.deleted_at,
        'guid': obj.guid,
        'name': obj.name,
        'users': user_data,
    }


def make_user_inspectable(obj: User) -> dict:
    return {
        'guid': obj.guid,
        'email_id': obj.email_id,
        'first_name': obj.first_name,
        'last_name': obj.last_name,
        'state': obj.state,
    }

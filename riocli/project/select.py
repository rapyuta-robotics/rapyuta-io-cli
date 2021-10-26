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

from riocli.config import Configuration
from riocli.project.util import name_to_guid


@click.command('select')
@click.argument('project-name', type=str)
@name_to_guid
def select_project(project_name: str, project_guid: str) -> None:
    """
    Sets the given project in the CLI context. All other resources use this project to act upon.
    """
    config = Configuration()
    config.data['project_id'] = project_guid
    config.save()
    click.secho('Project {} ({}) is selected!'.format(project_name, project_guid), fg='green')

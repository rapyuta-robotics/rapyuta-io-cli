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
from munch import unmunchify

from riocli.config import new_v2_client
from riocli.project.util import name_to_guid
from riocli.utils import inspect_with_format


@click.command('inspect')
@click.option('--format', '-f', 'format_type', default='yaml',
              type=click.Choice(['json', 'yaml'], case_sensitive=False))
@click.argument('project-name', type=str)
@name_to_guid
def inspect_project(format_type: str, project_name: str,
                    project_guid: str) -> None:
    """
    Inspect the project resource
    """
    try:
        client = new_v2_client(with_project=False)
        project = client.get_project(project_guid)
        inspect_with_format(unmunchify(project), format_type)
    except Exception as e:
        click.secho(str(e), fg='red')
        raise SystemExit(1)

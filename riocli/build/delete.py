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

from riocli.build.util import name_to_guid
from riocli.config import new_client


@click.command('delete')
@click.option('--force', '-f', 'force', is_flag=True, default=False, help='Skip confirmation')
@click.argument('build-name', required=True)
@name_to_guid
def delete_build(build_name: str, build_guid: str, force: bool):
    """
    Delete the build from the Platform
    """
    if not force:
        click.confirm('Deleting build {} ({})'.format(build_name, build_guid), abort=True)

    try:
        client = new_client()
        with spinner():
            client.delete_build(build_guid)
        click.echo(click.style('Build deleted successfully!', fg='green'))
    except Exception as e:
        click.secho(str(e), fg='red')
        exit(1)

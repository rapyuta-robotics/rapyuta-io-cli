# Copyright 2022 Rapyuta Robotics
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
from rapyuta_io.utils.rest_client import HttpMethod

from riocli.disk.util import name_to_guid, _api_call


@click.command('delete')
@click.option('--force', '-f', 'force', is_flag=True, default=False, help='Skip confirmation')
@click.argument('disk-name', required=True)
@name_to_guid
def delete_disk(disk_name: str, disk_guid: str, force: bool):
    """
    Delete the disk from the Platform
    """
    if not force:
        click.confirm('Deleting disk {} ({})'.format(disk_name, disk_guid), abort=True)

    try:
        with spinner():
            _api_call(HttpMethod.DELETE, guid=disk_guid, load_response=False)
        click.echo(click.style('Disk deleted successfully!', fg='green'))
    except Exception as e:
        click.secho(str(e), fg='red')
        raise SystemExit(1)

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
from riocli.static_route.util import name_to_guid


@click.command('delete')
@click.option('--force', '-f', is_flag=True, default=False, help='Skip confirmation')
@click.argument('static-route', type=str)
@name_to_guid
def delete_static_route(static_route: str, static_route_guid: str, force: bool) -> None:
    """
    Deletes the static route resource from the Platform
    """

    if not force:
        click.confirm('Deleting static route {} ({})'.format(static_route, static_route_guid),
                      abort=True)

    try:
        client = new_client()
        with spinner():
            client.delete_static_route(static_route_guid)
        click.secho('Static Route deleted successfully!', fg='green')
    except Exception as e:
        click.secho(str(e), fg='red')
        exit(1)

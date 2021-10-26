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

from riocli.config import new_client
from riocli.static_route.util import name_to_guid


@click.command('open')
@click.argument('static-route', type=str)
@name_to_guid
def open_static_route(static_route, static_route_guid) -> None:
    """
    Opens the static route in the default browser
    """
    try:
        client = new_client()
        route = client.get_static_route(static_route_guid)
        click.launch(url='https://{}'.format(route.urlString), wait=False)
    except Exception as e:
        click.secho(str(e), fg='red')
        exit(1)

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
from rapyuta_io.clients.static_route import StaticRoute

from riocli.config import new_client
from riocli.static_route.util import name_to_guid
from riocli.utils import inspect_with_format


@click.command('inspect')
@click.option('--format', '-f', 'format_type',
              type=click.Choice(['json', 'yaml'], case_sensitive=True), default='yaml')
@click.argument('static-route', type=str)
@name_to_guid
def inspect_static_route(format_type: str, static_route: str, static_route_guid: str) -> None:
    """
    Inspect the static route resource
    """
    try:
        client = new_client()
        route = client.get_static_route(static_route_guid)
        data = make_static_route_inspectable(route)
        inspect_with_format(data, format_type)
    except Exception as e:
        click.secho(str(e), fg='red')
        exit(1)


def make_static_route_inspectable(static_route_data: StaticRoute) -> dict:
    return {
        'created_at': static_route_data.CreatedAt,
        'updated_at': static_route_data.UpdatedAt,
        'deleted_at': static_route_data.DeletedAt,
        'guid': static_route_data.guid,
        'url_prefix': static_route_data.urlPrefix,
        'url': static_route_data.urlString,
        'creator': static_route_data.creator,
        'project': static_route_data.projectGUID,
        'metadata': static_route_data.metadata.__dict__,
    }



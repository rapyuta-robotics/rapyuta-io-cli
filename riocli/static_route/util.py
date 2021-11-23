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
import functools
import typing

import click
from rapyuta_io import Client
from rapyuta_io.clients.static_route import StaticRoute

from riocli.config import new_client


def name_to_guid(f: typing.Callable) -> typing.Callable:
    @functools.wraps(f)
    def decorated(**kwargs: typing.Any):
        client = new_client()
        name = kwargs.pop('static_route')
        guid = None

        if name.startswith('staticroute-'):
            guid = name
            name = None

        if name is None:
            name = get_static_route_name(client, guid)

        if guid is None:
            guid = find_static_route_guid(client, name)

        kwargs['static_route'] = name
        kwargs['static_route_guid'] = guid
        f(**kwargs)

    return decorated


def get_static_route_name(client: Client, guid: str) -> str:
    static_route = client.get_static_route(guid)
    return static_route.urlPrefix.split("-")[0]


def find_static_route_guid(client: Client, name: str) -> str:
    routes = client.get_all_static_routes()
    for route in routes:
        if route.urlPrefix == name or route.urlString == name:
            return route.guid

    click.secho("Static route not found", fg='red')
    exit(1)


def repr_static_routes(routes: typing.List[StaticRoute]) -> None:
    header = '{:<36} {:<25} {:36} {:36} {:32}'.format(
        'Static Route ID',
        'Name',
        'Full URL',
        'Creator',
        'Created At',
    )
    click.echo(click.style(header, fg='yellow'))
    for route in routes:
        click.secho(
            '{:<36} {:<25} {:36} {:36} {:32}'.
            format(route.guid, route.urlPrefix, route.urlString, route.creator,
                   route.CreatedAt))

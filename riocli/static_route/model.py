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
import typing

import click
from rapyuta_io import Client
from rapyuta_io.clients.static_route import StaticRoute as v1StaticRoute

from riocli.model import Model
from riocli.static_route.util import StaticRouteNotFound, find_static_route_guid
from riocli.static_route.validation import validate


class StaticRoute(Model):
    def __init__(self, *args, **kwargs):
        self.update(*args, **kwargs)

    def find_object(self, client: Client) -> bool:
        try:
            _find_static_route_guid(client, self.metadata.name)
            click.echo('{}/{} {} exists'.format(self.apiVersion, self.kind, self.metadata.name))
            return True
        except StaticRouteNotFound:
            return False

    def create_object(self, client: Client) -> v1StaticRoute:
        static_route = client.create_static_route(self.metadata.name)
        click.secho('{}/{} {} created'.format(self.apiVersion, self.kind, self.metadata.name), fg='green')
        return static_route

    def update_object(self, client: Client, obj: typing.Any) -> None:
        pass


    @classmethod
    def pre_process(cls, client: Client, d: typing.Dict) -> None:
        pass

    @staticmethod
    def validate(data) -> None:
        validate(data)


def _find_static_route_guid(client: Client, name: str) -> str:
    """
    This method is re-implemented because the default find method for name_to_guid decorator does direct match of the
    urlPrefix without splitting the Org Short GUID.
    """
    routes = client.get_all_static_routes()
    for route in routes:
        route_parts = route.urlPrefix.split("-")

        if "-".join(route_parts[:-1]) == name:
            return route.guid

    raise StaticRouteNotFound()

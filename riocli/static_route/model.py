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
from riocli.static_route.util import StaticRouteNotFound
from riocli.static_route.validation import validate


class StaticRoute(Model):
    def __init__(self, *args, **kwargs):
        self.update(*args, **kwargs)

    def find_object(self, client: Client) -> bool:
        _, static_route = self.rc.find_depends({"kind": "staticroute", "nameOrGUID": self.metadata.name})
        if not static_route:
            return False

        return static_route

    def create_object(self, client: Client) -> v1StaticRoute:
        static_route = client.create_static_route(self.metadata.name)
        return static_route

    def update_object(self, client: Client, obj: typing.Any) -> None:
        pass

    def delete_object(self, client: Client, obj: typing.Any):
        client.delete_static_route(obj.guid)

    @classmethod
    def pre_process(cls, client: Client, d: typing.Dict) -> None:
        pass

    @staticmethod
    def validate(data) -> None:
        validate(data)

# Copyright 2023 Rapyuta Robotics
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
from munch import unmunchify

from rapyuta_io import Client

from riocli.config import new_v2_client
from riocli.jsonschema.validate import load_schema
from riocli.model import Model


class StaticRoute(Model):
    def __init__(self, *args, **kwargs):
        self.update(*args, **kwargs)

    def find_object(self, client: Client) -> bool:
        _, static_route = self.rc.find_depends({
            'kind': 'staticroute',
            'nameOrGUID': self.metadata.name
        })
        if not static_route:
            return False

        return static_route

    def create_object(self, client: Client, **kwargs) -> typing.Any:
        client = new_v2_client()

        # convert to a dict and remove the ResolverCache
        # field since it's not JSON serializable
        self.pop("rc", None)
        static_route = unmunchify(self)
        r = client.create_static_route(static_route)
        return unmunchify(r)

    def update_object(self, client: Client, obj: typing.Any) -> None:
        pass

    def delete_object(self, client: Client, obj: typing.Any):
        client = new_v2_client()
        client.delete_static_route(obj.metadata.name)

    @classmethod
    def pre_process(cls, client: Client, d: typing.Dict) -> None:
        pass

    @staticmethod
    def validate(data):
        """
        Validates if static route data is matching with its corresponding schema
        """
        schema = load_schema('static_route')
        schema.validate(data)

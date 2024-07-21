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
from typing import Any, Dict

import click
from munch import unmunchify

from riocli.config import new_v2_client
from riocli.constants import Colors, Symbols
from riocli.jsonschema.validate import load_schema
from riocli.model import Model
from riocli.v2client.client import NetworkNotFound, Client


class Network(Model):
    def __init__(self, *args, **kwargs):
        self.update(*args, **kwargs)

    def find_object(self, client: Client) -> bool:
        try:
            network, obj = self.rc.find_depends({"kind": self.kind.lower(),
                                                 "nameOrGUID": self.metadata.name}, self.spec.type)
            if not network:
                return False

            return obj
        except NetworkNotFound:
            return False

    def create_object(self, client: Client, **kwargs) -> typing.Any:
        client = new_v2_client()

        r = client.create_network(self._sanitize_network())

        retry_count = int(kwargs.get('retry_count'))
        retry_interval = int(kwargs.get('retry_interval'))

        try:
            r = client.poll_network(r.metadata.name, retry_count=retry_count, sleep_interval=retry_interval)
        except Exception as e:
            click.secho(">> {}: Error polling for network ({}:{})".format(
                Symbols.WARNING,
                self.kind.lower(),
                self.metadata.name), fg=Colors.YELLOW)
            click.secho(str(e), fg=Colors.YELLOW)

        return unmunchify(r)

    def update_object(self, client: Client, obj: typing.Any) -> Any:
        pass

    def delete_object(self, client: Client, obj: typing.Any) -> typing.Any:
        client = new_v2_client()
        client.delete_network(obj.metadata.name)

    @classmethod
    def pre_process(cls, client: Client, d: Dict) -> None:
        pass

    @staticmethod
    def validate(data):
        """
        Validates if network data is matching with its corresponding schema
        """
        schema = load_schema('network')
        schema.validate(data)

    def _sanitize_network(self) -> typing.Dict:
        # Unset createdAt and updatedAt to avoid timestamp parsing issue.
        self.metadata.createdAt = None
        self.metadata.updatedAt = None

        data = unmunchify(self)

        # convert to a dict and remove the ResolverCache
        # field since it's not JSON serializable
        data.pop("rc", None)

        return data

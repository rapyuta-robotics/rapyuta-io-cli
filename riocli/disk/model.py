# Copyright 2024 Rapyuta Robotics
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
from munch import unmunchify

from riocli.config import new_v2_client
from riocli.constants import Colors, Symbols
from riocli.jsonschema.validate import load_schema
from riocli.model import Model
from riocli.v2client import Client


class Disk(Model):
    def __init__(self, *args, **kwargs):
        self.update(*args, **kwargs)

    def find_object(self, client: Client) -> typing.Any:
        guid, disk = self.rc.find_depends({
            'kind': 'disk',
            'nameOrGUID': self.metadata.name
        })

        return disk if guid else False

    def create_object(self, client: Client, **kwargs) -> typing.Any:
        v2_client = new_v2_client()

        r = v2_client.create_disk(self._sanitize_disk())
        retry_count = int(kwargs.get('retry_count'))
        retry_interval = int(kwargs.get('retry_interval'))
        try:
            v2_client.poll_disk(r.metadata.name, retry_count=retry_count, sleep_interval=retry_interval)
        except Exception as e:
            click.secho(">> {}: Error polling for disk ({}:{})".format(
                Symbols.WARNING,
                self.kind.lower(),
                self.metadata.name), fg=Colors.YELLOW)
            click.secho(str(e), fg=Colors.YELLOW)

        return unmunchify(r)

    def update_object(self, client: Client, obj: typing.Any) -> typing.Any:
        pass

    def delete_object(self, client: Client, obj: typing.Any) -> typing.Any:
        v2_client = new_v2_client()
        v2_client.delete_disk(obj.metadata.name)

    @classmethod
    def pre_process(cls, client: Client, d: typing.Dict) -> None:
        pass

    @staticmethod
    def validate(d):
        schema = load_schema('disk')
        schema.validate(d)

    def _sanitize_disk(self) -> typing.Dict:
        # Unset createdAt and updatedAt to avoid timestamp parsing issue.
        self.metadata.createdAt = None
        self.metadata.updatedAt = None

        data = unmunchify(self)

        # convert to a dict and remove the ResolverCache
        # field since it's not JSON serializable
        data.pop("rc", None)

        return data

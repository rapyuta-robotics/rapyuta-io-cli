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
from os import stat
import typing
from time import sleep
from munch import unmunchify

import click
from munch import munchify
from rapyuta_io import Client
from rapyuta_io.utils.rest_client import HttpMethod

from riocli.config import new_v2_client
from riocli.constants import Colors, Symbols
from riocli.disk.util import _api_call
from riocli.jsonschema.validate import load_schema
from riocli.model import Model


class Disk(Model):
    def __init__(self, *args, **kwargs):
        self.update(*args, **kwargs)

    def find_object(self, client: Client) -> typing.Any:
        _, disk = self.rc.find_depends({
            'kind': 'disk',
            'nameOrGUID': self.metadata.name
        })

        if not disk:
            return False

        return disk

    def create_object(self, client: Client, **kwargs) -> typing.Any:
        v2_client = new_v2_client()

        # convert to a dict and remove the ResolverCache
        # field since it's not JSON serializable
        self.pop("rc", None)
        disk = unmunchify(self)
        r = v2_client.create_disk(disk)
        return unmunchify(r)

    def update_object(self, client: Client, obj: typing.Any) -> typing.Any:
        pass

    @staticmethod
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

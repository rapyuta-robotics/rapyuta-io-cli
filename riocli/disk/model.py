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
from rapyuta_io.utils.rest_client import HttpMethod

from riocli.disk.util import _api_call, find_disk_guid, DiskNotFound
from riocli.model import Model


class Disk(Model):
    def find_object(self, client: Client) -> typing.Any:
        try:
            return self.rc.cache.find_guid(self.metadata.name, self.kind.lower())
        except DiskNotFound:
            return False

    def create_object(self, client: Client) -> typing.Any:
        labels = self.metadata.get('labels', None)
        payload = {
            "labels": labels,
            "name": self.metadata.name,
            "diskType": "ssd",
            "runtime": self.spec.runtime,
            "capacity": self.spec.capacity,
        }
        return _api_call(HttpMethod.POST, payload=payload)

    def update_object(self, client: Client, obj: typing.Any) -> typing.Any:
        pass

    @classmethod
    def pre_process(cls, client: Client, d: typing.Dict) -> None:
        pass

    @staticmethod
    def validate(d):
        pass



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

from munch import munchify
from rapyuta_io import Client

from riocli.managedservice.util import ManagedServicesClient
from riocli.managedservice.validation import validate
from riocli.model import Model


class ManagedService(Model):
    def find_object(self, client: Client) -> typing.Any:
        name = self.metadata.name
        client = ManagedServicesClient()

        try:
            instance = client.get_instance(name)
            return munchify(instance)
        except Exception:
            return False

    def create_object(self, client: Client) -> typing.Any:
        client = ManagedServicesClient()
        result = client.create_instance(self)
        return munchify(result)

    def update_object(self, client: Client, obj: typing.Any) -> typing.Any:
        pass

    def delete_object(self, client: Client, obj: typing.Any) -> typing.Any:
        client = ManagedServicesClient()
        client.delete_instance(obj.metadata.name)

    @staticmethod
    def list_instances():
        client = ManagedServicesClient()
        return client.list_instances()

    @classmethod
    def pre_process(cls, client: Client, d: typing.Dict) -> None:
        pass

    @staticmethod
    def validate(d):
        validate(d)

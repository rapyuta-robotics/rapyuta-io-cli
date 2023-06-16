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

from munch import munchify, unmunchify
from rapyuta_io import Client

from riocli.config import new_v2_client
from riocli.jsonschema.validate import load_schema
from riocli.model import Model


class ManagedService(Model):
    def find_object(self, client: Client) -> typing.Any:
        name = self.metadata.name
        client = new_v2_client()

        try:
            instance = client.get_instance(name)
            return munchify(instance)
        except Exception:
            return False

    def create_object(self, client: Client, **kwargs) -> typing.Any:
        client = new_v2_client()

        ms = unmunchify(self)
        ms.pop('rc', None)
        result = client.create_instance(ms)
        return munchify(result)

    def update_object(self, client: Client, obj: typing.Any) -> typing.Any:
        pass

    def delete_object(self, client: Client, obj: typing.Any) -> typing.Any:
        client = new_v2_client()
        client.delete_instance(obj.metadata.name)

    @staticmethod
    def list_instances():
        client = new_v2_client()
        return client.list_instances()

    @classmethod
    def pre_process(cls, client: Client, d: typing.Dict) -> None:
        pass

    @staticmethod
    def validate(data):
        """
        Validates if managedservice data is matching with its corresponding schema
        """
        schema = load_schema('managedservice')
        schema.validate(data)

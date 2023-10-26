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

class Secret(Model):
    def __init__(self, *args, **kwargs):
        self.update(*args, **kwargs)

    def find_object(self, client: Client) -> bool:
        _, secret = self.rc.find_depends({
            'kind': 'secret',
            'nameOrGUID': self.metadata.name
        })

        if not secret:
            return False

        return secret

    def create_object(self, client: Client, **kwargs) -> typing.Any:
        client = new_v2_client()

        # convert to a dict and remove the ResolverCache
        # field since it's not JSON serializable
        secret = unmunchify(self)
        secret.pop("rc", None)
        r = client.create_secret(secret)
        return unmunchify(r)

    def update_object(self, client: Client, obj: typing.Any) -> typing.Any:
        client = new_v2_client()

        secret = unmunchify(self)
        secret.pop("rc", None)

        r = client.update_secret(obj.name, secret)
        return unmunchify(r)

    def delete_object(self, client: Client, obj: typing.Any) -> typing.Any:
        client = new_v2_client()
        client.delete_secret(obj.name)

    @classmethod
    def pre_process(cls, client: Client, d: typing.Dict) -> None:
        pass

    @staticmethod
    def validate(data):
        """
        Validates if secret data is matching with its corresponding schema
        """
        schema = load_schema('secret')
        schema.validate(data)

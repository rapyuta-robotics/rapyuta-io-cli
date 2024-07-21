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

from riocli.config import new_v2_client
from riocli.jsonschema.validate import load_schema
from riocli.model import Model
from riocli.v2client import Client


class Deployment(Model):
    def __init__(self, *args, **kwargs):
        self.update(*args, **kwargs)

    def find_object(self, client: Client) -> typing.Any:
        guid, obj = self.rc.find_depends({"kind": "deployment", "nameOrGUID": self.metadata.name})

        return obj if guid else False

    def create_object(self, client: Client, **kwargs) -> typing.Any:
        client = new_v2_client()

        r = client.create_deployment(self._sanitize_deployment())
        return unmunchify(r)

    def update_object(self, client: Client, obj: typing.Any) -> typing.Any:
        pass

    def delete_object(self, client: Client, obj: typing.Any) -> typing.Any:
        client = new_v2_client()
        client.delete_deployment(obj.metadata.name)

    @classmethod
    def pre_process(cls, client: Client, d: typing.Dict) -> None:
        pass

    @staticmethod
    def validate(data):
        """
        Validates if deployment data is matching with its corresponding schema
        """
        schema = load_schema('deployment')
        schema.validate(data)

    def _sanitize_deployment(self) -> typing.Dict:
        # Unset createdAt and updatedAt to avoid timestamp parsing issue.
        self.metadata.createdAt = None
        self.metadata.updatedAt = None

        data = unmunchify(self)

        # convert to a dict and remove the ResolverCache
        # field since it's not JSON serializable
        data.pop("rc", None)

        return data

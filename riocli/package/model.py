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

from munch import unmunchify

from riocli.config import new_v2_client
from riocli.jsonschema.validate import load_schema
from riocli.model import Model
from riocli.package.enum import RestartPolicy
from riocli.v2client import Client


class Package(Model):
    RESTART_POLICY = {
        'always': RestartPolicy.Always,
        'never': RestartPolicy.Never,
        'onfailure': RestartPolicy.OnFailure
    }

    def __init__(self, *args, **kwargs):
        self.update(*args, **kwargs)

    def find_object(self, client: Client):
        guid, obj = self.rc.find_depends({"kind": self.kind.lower(), "nameOrGUID": self.metadata.name},
                                         self.metadata.version)
        return obj if guid else False

    def create_object(self, client: Client, **kwargs) -> typing.Any:
        v2_client = new_v2_client()

        r = v2_client.create_package(self._sanitize_package())
        return unmunchify(r)

    def update_object(self, client: Client, obj: typing.Any) -> typing.Any:
        pass

    def delete_object(self, client: Client, obj: typing.Any) -> typing.Any:
        v2_client = new_v2_client()
        v2_client.delete_package(obj.metadata.name, query={"version": obj.metadata.version})

    @classmethod
    def pre_process(cls, client: Client, d: typing.Dict) -> None:
        pass

    def _sanitize_package(self) -> typing.Dict:
        # Unset createdAt and updatedAt to avoid timestamp parsing issue.
        self.metadata.createdAt = None
        self.metadata.updatedAt = None

        self._convert_command()

        data = unmunchify(self)

        # convert to a dict and remove the ResolverCache
        # field since it's not JSON serializable
        data.pop("rc", None)

        return data

    def _convert_command(self):
        for exec in self.spec.executables:
            if exec.get('command') is not None:
                c = []

                if exec.get('runAsBash'):
                    c = ['/bin/bash', '-c']

                if isinstance(exec.command, list):
                    c.extend(exec.command)
                else:
                    c.append(exec.command)

                exec.command = c

    @staticmethod
    def validate(data):
        """
        Validates if package data is matching with its corresponding schema
        """
        schema = load_schema('package')
        schema.validate(data)

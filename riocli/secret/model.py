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

from rapyuta_io import (
    Client,
    Secret as v1Secret,
    SecretConfigDocker,
    SecretConfigSourceBasicAuth,
    SecretConfigSourceSSHAuth,
)

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

    def create_object(self, client: Client, **kwargs) -> v1Secret:
        secret = client.create_secret(self.to_v1())
        return secret

    def update_object(self, client: Client, obj: typing.Any) -> None:
        pass

    def delete_object(self, client: Client, obj: typing.Any) -> typing.Any:
        client.delete_secret(obj.guid)

    def to_v1(self) -> v1Secret:
        if self.spec.type == 'Docker':
            return self._docker_secret_to_v1()
        else:
            return self._git_secret_to_v1()

    def _docker_secret_to_v1(self) -> v1Secret:
        config = SecretConfigDocker(
            self.spec.docker.username,
            self.spec.docker.password,
            self.spec.docker.email,
            self.spec.docker.registry,
        )
        return v1Secret(self.metadata.name, config)

    def _git_secret_to_v1(self) -> v1Secret:
        if self.spec.git.authMethod == 'SSH Auth':
            config = SecretConfigSourceSSHAuth(self.spec.git.privateKey)
        elif self.spec.git.authMethod == 'HTTP/S Basic Auth':
            ca_cert = self.spec.git.get('ca_cert', None)
            config = SecretConfigSourceBasicAuth(
                self.spec.git.username,
                self.spec.git.password,
                ca_cert=ca_cert
            )
        elif self.spec.git.authMethod == 'HTTP/S Token Auth':
            # TODO(ankit): Implement it once SDK has support for it.
            raise Exception('token-based secret is not supported yet!')
        else:
            raise Exception('invalid gitAuthMethod for secret!')

        return v1Secret(self.metadata.name, config)

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

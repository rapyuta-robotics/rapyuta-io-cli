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
from rapyuta_io import Secret as v1Secret, SecretConfigDocker, SecretConfigSourceBasicAuth, \
    SecretConfigSourceSSHAuth, Client

from riocli.model import Model
from riocli.secret.util import find_secret_guid, SecretNotFound
from riocli.secret.validation import validate


class Secret(Model):

    def __init__(self, *args, **kwargs):
        self.update(*args, **kwargs)

    def find_object(self, client: Client) -> bool:
        try:
            find_secret_guid(client, self.metadata.name)
            click.echo('{}/{} {} exists'.format(self.apiVersion, self.kind, self.metadata.name))
            return True
        except SecretNotFound:
            return False

    def create_object(self, client: Client) -> v1Secret:
        secret = client.create_secret(self.to_v1())
        click.secho('{}/{} {} created'.format(self.apiVersion, self.kind, self.metadata.name), fg='green')
        return secret

    def update_object(self, client: Client, obj: typing.Any) -> None:
        pass

    def to_v1(self) -> v1Secret:
        if self.spec.type == 'Docker':
            return self._docker_secret_to_v1()
        else:
            return self._git_secret_to_v1()

    def _docker_secret_to_v1(self) -> v1Secret:
        config = SecretConfigDocker(self.spec.username, self.spec.password, self.spec.email, self.spec.registry)
        return v1Secret(self.metadata.name, config)

    def _git_secret_to_v1(self) -> v1Secret:
        if self.spec.gitAuthMethod == 'SSH':
            config = SecretConfigSourceSSHAuth(self.spec.privateKey)
        elif self.spec.gitAuthMethod == 'Basic':
            ca_cert = self.spec.get('ca_cert', None)
            config = SecretConfigSourceBasicAuth(self.spec.username, self.spec.password, ca_cert=ca_cert)
        elif self.spec.gitAuthMethod == 'Token':
            # TODO(ankit): Implement it once SDK has support for it.
            raise Exception('token-based secret is not supported yet!')
        else:
            raise Exception('invalid gitAuthMethod for secret!')

        return v1Secret(self.metadata.name, config)

    @classmethod
    def pre_process(cls, client: Client, d: typing.Dict) -> None:
        pass

    @staticmethod
    def validate(data) -> None:
        validate(data)

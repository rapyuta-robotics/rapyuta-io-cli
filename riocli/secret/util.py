# Copyright 2021 Rapyuta Robotics
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
import functools
import typing

import click
from rapyuta_io import Client

from riocli.config import new_client


def name_to_guid(f: typing.Callable) -> typing.Callable:
    @functools.wraps(f)
    def decorated(**kwargs: typing.Any):
        try:
            client = new_client()
        except Exception as e:
            click.secho(str(e), fg='red')
            exit(1)

        name = kwargs.pop('secret_name')
        guid = None

        if name.startswith('secret-'):
            guid = name
            name = None

        if name is None:
            name = get_secret_name(client, guid)

        if guid is None:
            guid = find_secret_guid(client, name)

        kwargs['secret_name'] = name
        kwargs['secret_guid'] = guid
        f(**kwargs)

    return decorated


def find_secret_guid(client: Client, name: str) -> str:
    secrets = client.list_secrets()
    for secret in secrets:
        if secret.name == name:
            return secret.guid

    click.secho("secret not found", fg='red')
    exit(1)


def get_secret_name(client: Client, guid: str) -> str:
    secret = client.get_secret(guid)
    return secret.name

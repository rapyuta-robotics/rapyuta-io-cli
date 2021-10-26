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
import click
from click_spinner import spinner
from rapyuta_io import Secret, SecretConfigSourceSSHAuth, SecretConfigSourceBasicAuth

from riocli.config import new_client


def create_source_secret(
        secret_name: str,
        username: str = None,
        password: str = None,
        ca_cert: click.File = None,
        ssh_key: click.File = None,
) -> None:
    secret_type = click.prompt('Source secret type[basic-auth, ssh]')
    if secret_type == 'basic-auth':
        create_basic_auth_secret(secret_name, username=username, password=password, ca_cert=ca_cert)
    elif secret_type == 'ssh':
        create_ssh_secret(secret_name, ssh_key=ssh_key)
    else:
        click.secho('Invalid Source secret type. Try again!', fg='red')


def create_basic_auth_secret(
        secret_name: str,
        username: str,
        password: str,
        ca_cert: click.File = None,
) -> None:
    if not username:
        username = click.prompt('git username')

    if not password:
        password = click.prompt('git password', hide_input=True)

    ca_cert_data = None
    if ca_cert:
        ca_cert_data = ca_cert.read()

        if not ca_cert_data:
            click.secho("Empty CA Cert file. Try again with correct file", fg='red')
            exit(1)

    secret_config = SecretConfigSourceBasicAuth(username=username, password=password,
                                                ca_cert=ca_cert_data)

    client = new_client()
    with spinner():
        client.create_secret(Secret(secret_name, secret_config=secret_config))
    click.secho('Secret created successfully!', fg='green')


def create_ssh_secret(secret_name: str, ssh_key: click.File = None) -> None:
    if not ssh_key:
        ssh_key = click.prompt('ssh key path', type=click.File('r', lazy=True))

    data = ssh_key.read()
    if not data:
        click.secho("Empty key file. Try again with correct key file", fg='red')
        exit(1)

    secret_config = SecretConfigSourceSSHAuth(ssh_key=data)
    client = new_client()

    with spinner():
        client.create_secret(Secret(secret_name, secret_config=secret_config))
    click.secho('Secret created successfully!', fg='green')

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
from rapyuta_io.clients.secret import DOCKER_HUB_REGISTRY, SecretConfigDocker, Secret

from riocli.config import new_client


def create_docker_secret(
        secret_name: str,
        username: str = None,
        password: str = None,
        email: str = None,
        registry=DOCKER_HUB_REGISTRY,
) -> None:
    if not username:
        username = click.prompt('docker username')

    if not password:
        password = click.prompt('docker password', hide_input=True)

    if not email:
        email = click.prompt('docker email')

    secret_config = SecretConfigDocker(username=username, password=password, email=email,
                                       registry=registry)
    client = new_client()

    with spinner():
        client.create_secret(Secret(secret_name, secret_config=secret_config))

    click.secho('Secret created successfully!', fg='green')

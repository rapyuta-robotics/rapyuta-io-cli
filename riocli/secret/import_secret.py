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
import base64
import json
from pathlib import Path

import click
from click_help_colors import HelpColorsGroup
from click_spinner import spinner

from rapyuta_io import SecretConfigDocker, Secret, SecretConfigSourceSSHAuth
from riocli.config import new_client
from riocli.utils import random_string, run_bash
from riocli.utils.selector import show_selection


@click.group(
    'import',
    invoke_without_command=False,
    cls=HelpColorsGroup,
    help_headers_color='yellow',
    help_options_color='green',
)
def import_secret() -> None:
    """
    Imports the secrets from the user environment
    """
    pass


@import_secret.command('ssh')
def ssh_auto_import() -> None:
    """
    Imports the selected private SSH keys from the ~/.ssh directory
    """
    secret = secret_from_ssh_dir()
    create_secret(secret)


@import_secret.command('docker')
def docker_auto_import() -> None:
    """
    Imports the authentication tokens for the configured registries
    """
    secret = secret_from_docker_config()
    create_secret(secret)


def create_secret(secret: Secret) -> None:
    try:
        client = new_client()
        with spinner():
            client.create_secret(secret)
        click.secho("Secret created successfully!", fg='green')
    except Exception as e:
        click.secho(str(e), fg='red')
        exit(1)


def secret_from_docker_config() -> Secret:
    docker_config_path = Path.home().joinpath(".docker", "config.json")
    with open(docker_config_path, 'r') as file:
        config = json.load(file)

    if not config or 'auths' not in config:
        click.secho("docker config not found!", fg='red')
        exit(1)

    registries = list(filter(lambda x: 'rapyuta.io' not in x, config['auths'].keys()))
    choice = show_selection(registries, header='Found these registries in the docker config')
    encoded_auth = str(config['auths'][choice]['auth'])
    auth = base64.b64decode(encoded_auth).decode("utf-8")
    parts = auth.split(":")
    username = str(parts[0])
    password = str(parts[1])
    secret_config = SecretConfigDocker(username=username, password=password,
                                       email='example@example.com', registry=choice)

    return Secret(_generate_secret_name('docker'), secret_config=secret_config)


def secret_from_ssh_dir() -> Secret:
    cmd = '/bin/bash -c "file ~/.ssh/* | grep \'private key\' | awk -v FS=\':\' \'{print $1}\'"'
    files = run_bash(cmd).split('\n')
    choice = show_selection(files, header='Found these private SSH keys')
    with open(choice) as file:
        data = file.read()

    secret_config = SecretConfigSourceSSHAuth(ssh_key=data)
    return Secret(_generate_secret_name('ssh'), secret_config=secret_config)


def _generate_secret_name(prefix: str) -> str:
    return '{}-{}'.format(prefix, random_string(5, 0)).lower()

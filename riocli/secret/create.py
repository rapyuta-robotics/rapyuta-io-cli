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
from rapyuta_io.clients.secret import DOCKER_HUB_REGISTRY

from riocli.secret.docker_secret import create_docker_secret
from riocli.secret.source_secret import create_source_secret


@click.command('create')
@click.option('--secret-type', '-t', help='Type of Secret', type=click.Choice(['docker', 'source']))
@click.option('--username', type=str,
              help='Docker registry username for docker secret, Git username for source secret')
@click.option('--password', '-p', type=str,
              help='Password (only for docker and source with basic auth)')
@click.option('--email', type=str,
              help='Email ID for Docker registry')
@click.option('--registry', default=DOCKER_HUB_REGISTRY, type=str,
              help='Docker Registry URL for Docker secret [Default: Docker Hub]')
@click.option('--ca-cert', type=click.File(mode='r', lazy=True),
              help='Path of CA Certificate (only for source with basic auth)')
@click.option('--ssh-priv-key', type=click.File(mode='r', lazy=True),
              help='Path of SSH Key (only for source with ssh auth)')
@click.argument('secret-name', type=str)
def create_secret(secret_type: str, username: str, password: str, email: str, registry: str,
                  ca_cert: click.File, ssh_priv_key: click.File, secret_name: str) -> None:
    """
    Creates a new instance of secret
    """
    try:
        if secret_type == 'docker':
            create_docker_secret(secret_name, username=username, password=password, email=email,
                                 registry=registry)
        elif secret_type == 'source':
            create_source_secret(secret_name, username=username, password=password, ca_cert=ca_cert,
                                 ssh_key=ssh_priv_key)
    except Exception as e:
        click.secho(str(e), fg='red')
        exit(1)

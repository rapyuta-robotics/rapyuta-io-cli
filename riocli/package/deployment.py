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
from rapyuta_io.clients.deployment import Deployment

from riocli.config import new_client
from riocli.deployment.list import display_deployment_list
from riocli.package.util import name_to_guid


@click.command('deployments')
@click.option('--version', 'package_version', type=str,
              help='Semantic version of the Package, only used when name is used instead of GUID')
@click.argument('package-name')
@name_to_guid
def list_package_deployments(package_name: str, package_guid: str) -> None:
    """
    List the deployments of the package
    """
    try:
        client = new_client()
        package = client.get_package(package_guid)
        deployments = package.deployments()
        display_deployment_list(deployments, show_header=True)
    except Exception as e:
        click.secho(str(e), fg='red')
        exit(1)

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
import typing

import click
from rapyuta_io.clients.deployment import Deployment

from riocli.config import new_client
from riocli.utils import tabulate_data


@click.command('list')
@click.option('--device', prompt_required=False, default='', type=str,
              help='Filter the Deployment list by Device ID')
@click.option('--phase', prompt_required=False, multiple=True,
              type=click.Choice(['In progress', 'Provisioning', 'Succeeded', 'Failed to start',
                                 'Partially deprovisioned', 'Deployment stopped']),
              default=['In progress', 'Provisioning', 'Succeeded', 'Failed to start'],
              help='Filter the Deployment list by Phases')
def list_deployments(device: str, phase: typing.List[str]) -> None:
    """
    List the deployments in the selected project
    """
    try:
        client = new_client()
        deployments = client.get_all_deployments(device_id=device, phases=phase)
        deployments = sorted(deployments, key=lambda d: d.name.lower())
        display_deployment_list(deployments, show_header=True)
    except Exception as e:
        click.secho(str(e), fg='red')
        raise SystemExit(1)


def display_deployment_list(deployments: typing.List[Deployment], show_header: bool = True):
    headers = []
    if show_header:
        headers = ('Deployment ID', 'Name', 'Phase', 'Package')

    data = []
    for deployment in deployments:
        package_name_version = "{} ({})".format(deployment.packageName, deployment.packageVersion)
        data.append([deployment.deploymentId, deployment.name,
                     deployment.phase, package_name_version])

    tabulate_data(data, headers=headers)

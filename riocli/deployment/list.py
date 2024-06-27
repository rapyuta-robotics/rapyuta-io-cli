# Copyright 2024 Rapyuta Robotics
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
from click_help_colors import HelpColorsCommand
from rapyuta_io.clients.deployment import Deployment, DeploymentPhaseConstants

from riocli.config import new_v2_client
from riocli.constants import Colors
from riocli.utils import tabulate_data

ALL_PHASES = [
    'InProgress',
    'Provisioning',
    'Succeeded',
    'FailedToStart',
    'Stopped',
]

DEFAULT_PHASES = [
    'InProgress',
    'Provisioning',
    'Succeeded',
    'FailedToStart',
]


@click.command(
    'list',
    cls=HelpColorsCommand,
    help_headers_color=Colors.YELLOW,
    help_options_color=Colors.GREEN,
)
@click.option('--device', prompt_required=False, default='', type=str,
              help='Filter the Deployment list by Device ID')
@click.option('--phase', prompt_required=False, multiple=True,
              type=click.Choice(ALL_PHASES),
              default=DEFAULT_PHASES,
              help='Filter the Deployment list by Phases')
def list_deployments(device: str, phase: typing.List[str]) -> None:
    """
    List the deployments in the selected project
    """
    try:
        client = new_v2_client(with_project=True)
        deployments = client.list_deployments(query={'phases': phase})
        deployments = sorted(deployments, key=lambda d: d.metadata.name.lower())
        display_deployment_list(deployments, show_header=True)
    except Exception as e:
        click.secho(str(e), fg=Colors.RED)
        raise SystemExit(1)


def display_deployment_list(deployments: typing.List[Deployment], show_header: bool = True):
    headers = []
    if show_header:
        headers = ('Deployment ID', 'Name', 'Phase', 'Package')

    data = []
    for deployment in deployments:
        package_name_version = "{} ({})".format(deployment.metadata.depends.nameOrGUID, deployment.metadata.depends.version)
        phase = deployment.status.phase if deployment.status else ""
        data.append([deployment.metadata.guid, deployment.metadata.name,
                     phase, package_name_version])

    tabulate_data(data, headers=headers)

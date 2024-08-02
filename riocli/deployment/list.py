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

import click
from click_help_colors import HelpColorsCommand
from rapyuta_io.clients.deployment import Deployment, DeploymentPhaseConstants

from riocli.config import new_client
from riocli.constants import Colors
from riocli.deployment.util import process_deployment_errors
from riocli.utils import tabulate_data

ALL_PHASES = [
    DeploymentPhaseConstants.INPROGRESS,
    DeploymentPhaseConstants.PROVISIONING,
    DeploymentPhaseConstants.SUCCEEDED,
    DeploymentPhaseConstants.FAILED_TO_START,
    DeploymentPhaseConstants.PARTIALLY_DEPROVISIONED,
    DeploymentPhaseConstants.DEPLOYMENT_STOPPED,
]

DEFAULT_PHASES = [
    DeploymentPhaseConstants.INPROGRESS,
    DeploymentPhaseConstants.PROVISIONING,
    DeploymentPhaseConstants.SUCCEEDED,
    DeploymentPhaseConstants.FAILED_TO_START,
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
@click.option('--wide', '-w', is_flag=True, default=False,
              help='Print more details', type=bool)
def list_deployments(
        device: str,
        phase: typing.List[str],
        wide: bool = False,
) -> None:
    """
    List the deployments in the selected project
    """
    try:
        client = new_client()
        deployments = client.get_all_deployments(device_id=device, phases=phase)
        deployments = sorted(deployments, key=lambda d: d.name.lower())
        display_deployment_list(deployments, show_header=True, wide=wide)
    except Exception as e:
        click.secho(str(e), fg=Colors.RED)
        raise SystemExit(1)


def display_deployment_list(
        deployments: typing.List[Deployment],
        show_header: bool = True,
        wide: bool = False,
):
    headers = []
    if show_header:
        headers = ('Name', 'Status', 'Phase', 'Errors')
        if wide:
            headers += ('Package', 'Deployment ID',)

    data = []
    for deployment in deployments:
        package_name_version = "{} ({})".format(deployment.packageName, deployment.packageVersion)
        row = [
            deployment.name,
            deployment.status,
            deployment.phase,
            process_deployment_errors(deployment.get('errorCode', []), no_action=True)
        ]

        if wide:
            row += [package_name_version, deployment.deploymentId]

        data.append(row)

    tabulate_data(data, headers=headers)

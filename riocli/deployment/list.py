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

from riocli.deployment.model import Deployment
from riocli.deployment.util import ALL_PHASES, DEFAULT_PHASES

from riocli.config import new_v2_client
from riocli.constants import Colors
from riocli.deployment.util import process_deployment_errors
from riocli.utils import tabulate_data


@click.command(
    'list',
    cls=HelpColorsCommand,
    help_headers_color=Colors.YELLOW,
    help_options_color=Colors.GREEN,
)
@click.option('--device', prompt_required=False, default='', type=str,
              help='Filter the Deployment list by Device name')
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
        client = new_v2_client()
        deployments = client.list_deployments(query={"phases": phase, "deviceName": device})
        deployments = sorted(deployments, key=lambda d: d.metadata.name.lower())
        display_deployment_list(deployments, show_header=True)
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
        headers = ('Deployment ID', 'Name', 'Phase', 'Package', 'Creation Time (UTC)', 'Stopped Time (UTC)')

    data = []
    for deployment in deployments:
        package_name_version = "{} ({})".format(deployment.metadata.depends.nameOrGUID,
                                                deployment.metadata.depends.version)
        phase = deployment.status.phase if deployment.status else ""
        data.append([deployment.metadata.guid, deployment.metadata.name,
                     phase, package_name_version, deployment.metadata.createdAt, deployment.metadata.get('deletedAt')])

    tabulate_data(data, headers=headers)

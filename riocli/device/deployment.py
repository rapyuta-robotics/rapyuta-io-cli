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
import click
from click_help_colors import HelpColorsCommand
from rapyuta_io.clients.deployment import DeploymentPhaseConstants

from riocli.config import new_client
from riocli.constants import Colors
from riocli.deployment.list import display_deployment_list
from riocli.device.util import name_to_guid

PHASES = [
    DeploymentPhaseConstants.INPROGRESS,
    DeploymentPhaseConstants.PROVISIONING,
    DeploymentPhaseConstants.SUCCEEDED,
    DeploymentPhaseConstants.FAILED_TO_START,
    DeploymentPhaseConstants.PARTIALLY_DEPROVISIONED,
]


@click.command(
    'deployments',
    cls=HelpColorsCommand,
    help_headers_color=Colors.YELLOW,
    help_options_color=Colors.GREEN,
)
@click.argument('device-name', type=str)
@name_to_guid
def list_deployments(device_name: str, device_guid: str) -> None:
    """
    Lists all the deployments running on the Device
    """
    try:
        client = new_client()
        deployments = client.get_all_deployments(device_id=device_guid, phases=PHASES)
        display_deployment_list(deployments, show_header=True)
    except Exception as e:
        click.secho(str(e), fg=Colors.RED)
        raise SystemExit(1) from e

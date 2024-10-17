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
import click
from click_help_colors import HelpColorsCommand

from riocli.config import new_v2_client
from riocli.constants import Colors
from riocli.deployment.list import display_deployment_list
from riocli.device.util import name_to_guid

DEFAULT_PHASES = [
    "InProgress",
    "Provisioning",
    "Succeeded",
    "FailedToStart",
]


@click.command(
    "deployments",
    cls=HelpColorsCommand,
    help_headers_color=Colors.YELLOW,
    help_options_color=Colors.GREEN,
)
@click.argument("device-name", type=str)
@name_to_guid
def list_deployments(device_name: str, device_guid: str) -> None:
    """Lists all the deployments running on the device."""
    try:
        client = new_v2_client()
        deployments = client.list_deployments(
            query={"deviceName": device_name, "phases": DEFAULT_PHASES}
        )
        display_deployment_list(deployments, show_header=True)
    except Exception as e:
        click.secho(str(e), fg=Colors.RED)
        raise SystemExit(1) from e

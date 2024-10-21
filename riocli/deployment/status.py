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


@click.command(
    "status",
    cls=HelpColorsCommand,
    help_headers_color=Colors.YELLOW,
    help_options_color=Colors.GREEN,
)
@click.argument("deployment-name", type=str)
def status(deployment_name: str) -> None:
    """Print the current status of a deployment.

    The command simply prints the current status of the deployment.
    This is useful in scripts and automation where you need to check
    the status of a deployment.
    """
    try:
        client = new_v2_client()
        deployment = client.get_deployment(deployment_name)
        click.secho(deployment.status.status)
    except Exception as e:
        click.secho(str(e), fg=Colors.RED)
        raise SystemExit(1)

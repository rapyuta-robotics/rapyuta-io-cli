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
    "logs",
    cls=HelpColorsCommand,
    help_headers_color=Colors.YELLOW,
    help_options_color=Colors.GREEN,
)
@click.option(
    "--replica", "replica", default=0, help="Replica identifier of the deployment"
)
@click.option(
    "--exec", "exec_name", default=None, help="Name of a executable in the component"
)
@click.argument("deployment-name", type=str)
def deployment_logs(
    replica: int,
    exec_name: str,
    deployment_name: str,
) -> None:
    """Stream live logs from cloud deployments.

    You can stream logs from a deployment running on the cloud.
    In case there are more than one executable in the deployment,
    you can specify the executable name using the --exec option.

    If there are multiple replicas of the deployment, you can specify
    the replica number using the --replica option. The default replica
    number is 0.

    Note: The logs are streamed in real-time. Press Ctrl+C to stop the
    log streaming. Also, device deployments do not support log streaming.
    """
    try:
        # TODO(pallab): when no exec name is given, implement the logic to set default or prompt a selection.
        client = new_v2_client()
        client.stream_deployment_logs(deployment_name, exec_name, replica)
    except Exception as e:
        click.secho(e, fg=Colors.RED)
        raise SystemExit(1)

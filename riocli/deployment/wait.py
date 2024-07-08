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
import typing
import time

from click_help_colors import HelpColorsCommand
from rapyuta_io.utils import RetriesExhausted, DeploymentNotRunningException
from riocli.config import new_v2_client
from riocli.constants import Colors, Symbols, Status
from riocli.deployment.util import name_to_guid
from riocli.utils.spinner import with_spinner

from rapyuta_io import Client

def poll_deployment_till_ready(client: Client, deployment: typing.Any, retry_count=50, sleep_interval=6):
    for _ in range(retry_count):
        if deployment.status.status == Status.RUNNING:
            return deployment

        time.sleep(sleep_interval)
        deployment = client.get_deployment(deployment.metadata.name)
    return deployment

@click.command(
    'wait',
    cls=HelpColorsCommand,
    help_headers_color=Colors.YELLOW,
    help_options_color=Colors.GREEN,
)
@click.argument('deployment-name', type=str)
@with_spinner(text="Waiting for deployment...", timer=True)
def wait_for_deployment(
        deployment_name: str,
        spinner=None,
) -> None:
    """
    Wait until the deployment succeeds/fails
    """
    try:
        client = new_v2_client()
        deployment = client.get_deployment(deployment_name)

        retry_count = int(kwargs.get('retry_count'))
        retry_interval = int(kwargs.get('retry_interval'))
        deployment = poll_deployment_till_ready(client, deployment, retry_count, retry_interval)
        spinner.text = click.style('Deployment status: {}'.format(deployment.status.status), fg=Colors.GREEN)
        spinner.green.ok(Symbols.SUCCESS)
    except RetriesExhausted as e:
        spinner.write(click.style(str(e), fg=Colors.RED))
        spinner.text = click.style('Try again?', Colors.RED)
        spinner.red.fail(Symbols.ERROR)
    except DeploymentNotRunningException as e:
        if 'DEP_E151' in e.deployment_status.errors:
            spinner.text = click.style('Device is either offline or not reachable', fg=Colors.RED)
        else:
            spinner.text = click.style(str(e), fg=Colors.RED)
        spinner.red.fail(Symbols.ERROR)
        raise SystemExit(1)
    except Exception as e:
        spinner.text = click.style(str(e), fg=Colors.RED)
        spinner.red.fail(Symbols.ERROR)
        raise SystemExit(1)

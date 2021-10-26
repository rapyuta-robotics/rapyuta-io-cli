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
from click_spinner import spinner
from rapyuta_io.utils import RetriesExhausted, DeploymentNotRunningException

from riocli.config import new_client
from riocli.deployment.util import name_to_guid


@click.command('wait')
@click.argument('deployment-name', type=str)
@name_to_guid
def wait_for_deployment(deployment_name: str, deployment_guid: str) -> None:
    """
    Wait until the Deployment succeeds/fails
    """
    try:
        client = new_client()
        with spinner():
            deployment = client.get_deployment(deployment_guid)
            # TODO(ankit): Fix the poll_deployment_till_ready for Runtime Error
            status = deployment.poll_deployment_till_ready()
        click.secho('Deployment status: {}'.format(status.status))
    except RetriesExhausted as e:
        click.secho(str(e), fg='red')
        click.secho('Retry Again?', fg='red')
    except DeploymentNotRunningException as e:
        if 'DEP_E151' in e.deployment_status.errors:
            click.secho('Device is either offline or not reachable', fg='red')
        else:
            click.secho(str(e), fg='red')
        exit(1)
    except Exception as e:
        click.secho(str(e), fg='red')
        exit(1)

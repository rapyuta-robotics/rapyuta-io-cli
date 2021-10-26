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

from riocli.config import new_client
from riocli.deployment.util import name_to_guid


@click.command('status')
@click.argument('deployment-name', type=str)
@name_to_guid
def status(deployment_name: str, deployment_guid: str) -> None:
    """
    Current status of the deployment
    """
    try:
        client = new_client()
        deployment = client.get_deployment(deployment_guid)
        click.secho(deployment.status)
    except Exception as e:
        click.secho(str(e), fg='red')
        exit(1)

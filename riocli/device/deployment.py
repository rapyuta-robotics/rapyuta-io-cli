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
from riocli.deployment.list import display_deployment_list
from riocli.device.util import name_to_guid


@click.command('deployments')
@click.argument('device-name', type=str)
@name_to_guid
def list_deployments(device_name: str, device_guid: str) -> None:
    """
    Lists all the deployments running on the Device
    """
    try:
        client = new_client()
        device = client.get_device(device_guid)
        partials = device.get_deployments()  # Partials
        deployments = []
        for partial in partials:
            # FIXME: get_deployments call doesn't return Deployment partial and instead just returns generic
            # ObjDict object. PartialMixin methods are not available on it.
            # partial.refresh()
            deployment = client.get_deployment(partial.io_deployment_id)
            deployments.append(deployment)
        display_deployment_list(deployments, show_header=True)
    except Exception as e:
        click.secho(str(e), fg='red')
        exit(1)



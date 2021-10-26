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
from riocli.deployment.logs import stream_deployment_logs
from riocli.network.util import name_to_guid


@click.command('logs', hidden=True)
@click.option('--network', 'network_type', help='Type of Network', default=None,
              type=click.Choice(['routed', 'native']))
@click.argument('network-name')
@name_to_guid
def network_logs(network_name: str, network_guid: str, network_type: str) -> None:
    if network_type == 'routed':
        # FIXME: For routed network, it returns Pod not found error
        click.secho('Not implemented yet!', fg='red')
        exit(1)
    elif network_type == 'native':
        native_network_logs(network_name, network_guid)


def native_network_logs(network_name: str, network_guid: str) -> None:
    try:
        client = new_client()
        network = client.get_native_network(network_guid)
        deployment = client.get_deployment(network.internal_deployment_guid)
        comp_id = deployment.componentInfo[0].componentID
        exec_id = deployment.componentInfo[0].executablesStatusInfo[0].id
        pod_name = deployment.componentInfo[0].executablesStatusInfo[0].metadata[0].podName
        stream_deployment_logs(deployment.deploymentId, comp_id, exec_id, pod_name)
    except Exception as e:
        click.secho(str(e), fg='red')
        exit(1)

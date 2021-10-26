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

from riocli.config import new_client
from riocli.network.util import name_to_guid


@click.command('delete')
@click.option('--force', '-f', is_flag=True, default=False, help='Skip confirmation', type=bool)
@click.option('--network', 'network_type', help='Type of Network', default=None,
              type=click.Choice(['routed', 'native']))
@click.argument('network-name', type=str)
@name_to_guid
def delete_network(force: bool, network_name: str, network_guid: str, network_type: str) -> None:
    """
    Delete the network from the Platform
    """

    if not force:
        click.confirm('Deleting {} network {} ({})'.
                      format(network_type, network_name, network_guid), abort=True)

    try:
        client = new_client()
        with spinner():
            if network_type == 'routed':
                # TODO: Implement and use the delete_routed_network of client directly.
                rn = client.get_routed_network(network_guid)
                rn.delete()
            elif network_type == 'native':
                client.delete_native_network(network_guid)
        click.secho('{} Network deleted successfully!'.format(network_type.capitalize()), fg='green')
    except Exception as e:
        click.secho(str(e), fg='red')
        exit(1)

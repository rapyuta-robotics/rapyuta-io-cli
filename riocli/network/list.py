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
import typing

import click
from rapyuta_io import DeploymentPhaseConstants
from rapyuta_io.clients.native_network import NativeNetwork
from rapyuta_io.clients.routed_network import RoutedNetwork

from riocli.config import new_client


@click.command('list')
@click.option('--network', help='Type of Network',
              type=click.Choice(['routed', 'native', 'both']), default='both')
def list_networks(network: str) -> None:
    """
    List the networks in the selected project
    """
    try:
        client = new_client()
        networks = []
        if network in ['routed', 'both']:
            networks += client.get_all_routed_networks()

        if network in ['native', 'both']:
            networks += client.list_native_networks()

        _display_network_list(networks, show_header=True)
    except Exception as e:
        click.secho(str(e), fg='red')
        exit(1)


def _display_network_list(
        networks: typing.List[typing.Union[RoutedNetwork, NativeNetwork]],
        show_header: bool = True,
) -> None:
    if show_header:
        click.secho('{:29} {:<15} {:8} {:8} {:20}'.
                    format('Network ID', 'Network Name', 'Runtime', 'Type', 'Phase'),
                    fg='yellow')

    for network in networks:
        phase = None
        network_type = None
        if isinstance(network, RoutedNetwork):
            network_type = 'routed'
            phase = network.phase
        elif isinstance(network, NativeNetwork):
            network_type = 'native'
            phase = network.internal_deployment_status.phase

        if phase and phase == DeploymentPhaseConstants.DEPLOYMENT_STOPPED.value:
            continue
        click.secho('{:29} {:<15} {:8} {:8} {:20}'.
                    format(network.guid, network.name, network.runtime, network_type, phase))

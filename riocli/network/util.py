# Copyright 2023 Rapyuta Robotics
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
import functools
from typing import Optional, Union, Tuple, Callable, Any

import click
from rapyuta_io import DeploymentPhaseConstants, Client
from rapyuta_io.clients.native_network import NativeNetwork
from rapyuta_io.clients.routed_network import RoutedNetwork

from riocli.config import new_client
from riocli.constants import Colors
from riocli.utils.selector import show_selection


def name_to_guid(f: Callable) -> Callable:
    @functools.wraps(f)
    def decorated(**kwargs: Any):
        client = new_client()

        name = kwargs.pop('network_name')
        network_type = kwargs.pop('network', None)
        guid = None

        if name.startswith('net-'):
            guid = name
            name = None

        try:
            if guid:
                network, network_type = find_network_guid(
                    client, guid, network_type)
                name = network.name

            if name:
                network, network_type = find_network_name(
                    client, name, network_type)
                guid = network.guid
        except Exception as e:
            click.secho(str(e), fg=Colors.RED)
            raise SystemExit(1) from e

        kwargs['network_type'] = network_type
        kwargs['network_name'] = name
        kwargs['network_guid'] = guid
        f(**kwargs)

    return decorated


def find_network_guid(
        client: Client,
        guid: str,
        network_type: str,
) -> Tuple[Union[RoutedNetwork, NativeNetwork], str]:
    if network_type is None or network_type == 'routed':
        routed_networks = client.get_all_routed_networks()
        for network in routed_networks:
            if network.phase == DeploymentPhaseConstants.DEPLOYMENT_STOPPED.value:
                continue
            if network.guid == guid:
                return network, 'routed'

    if network_type is None or network_type == 'native':
        native_network = client.list_native_networks()
        for network in native_network:
            phase = network.internal_deployment_status.phase
            if phase == DeploymentPhaseConstants.DEPLOYMENT_STOPPED.value:
                continue
            if network.guid == guid:
                return network, 'native'

    raise NetworkNotFound()


def find_network_name(
        client: Client,
        name: str,
        network_type: Optional[str],
        is_resolve_conflict: bool = True
) -> Tuple[Optional[Union[RoutedNetwork, NativeNetwork]], str]:
    routed, native = None, None
    if network_type in [None, 'routed']:
        routed = find_routed_network_name(client, name)

    if network_type in [None, 'native']:
        native = find_native_network_name(client, name)

    return resolve_conflict(routed, native, network_type, is_resolve_conflict)


def find_native_network_name(client: Client, name: str) -> Optional[
    NativeNetwork]:
    native_networks = client.list_native_networks()
    for network in native_networks:
        phase = network.internal_deployment_status.phase
        if phase == DeploymentPhaseConstants.DEPLOYMENT_STOPPED.value:
            continue
        if network.name == name:
            return network


def find_routed_network_name(client: Client, name: str) -> Optional[
    RoutedNetwork]:
    routed_networks = client.get_all_routed_networks()
    for network in routed_networks:
        if network.phase == DeploymentPhaseConstants.DEPLOYMENT_STOPPED.value:
            continue
        if network.name == name:
            return network


def resolve_conflict(
        routed: Optional[RoutedNetwork],
        native: Optional[NativeNetwork],
        network_type: Optional[str],
        is_resolve_conflict: bool = True
) -> Tuple[Optional[Union[RoutedNetwork, NativeNetwork]], str]:
    if not routed and not native:
        raise NetworkNotFound()

    # If only routed, or only native network was found, there is no conflict to
    # resolve.
    if routed and not native:
        return routed, 'routed'
    elif native and not routed:
        return native, 'native'

    if not is_resolve_conflict:
        raise NetworkConflict()

    # Check if user already offered a choice in case of conflict
    if network_type:
        choice = network_type
    else:
        # Ask user to help us resolve conflict by selecting one network
        options = {
            'routed': '{} ({})'.format(routed.name, routed.guid),
            'native': '{} ({})'.format(native.name, native.guid),
        }
        choice = show_selection(options,
                                header='Both Routed and Native networks were found with '
                                       'the same name')

    if choice == 'routed':
        return routed, choice
    elif choice == 'native':
        return native, choice
    else:
        click.secho('Invalid choice. Try again', fg=Colors.RED)
        raise SystemExit(1)


def get_network(
        client: Client,
        network_guid: str,
        network_type: str,
) -> Optional[Union[RoutedNetwork, NativeNetwork]]:
    if network_type == 'routed':
        return client.get_routed_network(network_guid)
    elif network_type == 'native':
        return client.get_native_network(network_guid)


def get_network_internal_deployment(
        network: Union[RoutedNetwork, NativeNetwork],
        network_type: str,
) -> Optional[str]:
    if network_type == 'routed':
        return network.internalDeploymentGUID
    elif network_type == 'native':
        return network.internal_deployment_guid


class NetworkNotFound(Exception):
    def __init__(self, message='network not found!'):
        self.message = message
        super().__init__(self.message)


class NetworkConflict(Exception):
    def __init__(self,
                 message='both routed and native networks exist with the same name!'):
        self.message = message
        super().__init__(self.message)

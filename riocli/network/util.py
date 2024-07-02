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
from typing import Optional, Union, Tuple, Callable, Any, List
from munch import Munch
import click
import re

from rapyuta_io import DeploymentPhaseConstants, Client
from rapyuta_io.clients.native_network import NativeNetwork
from rapyuta_io.clients.routed_network import RoutedNetwork

from riocli.config import new_client
from riocli.constants import Colors
from riocli.utils import tabulate_data
from riocli.utils.selector import show_selection
from riocli.config import new_v2_client
from riocli.network.model import Network

def name_to_guid(f: Callable) -> Callable:
    @functools.wraps(f)
    def decorated(**kwargs: Any):
        client = new_v2_client()

        name = kwargs.pop('network_name')
        network_type = kwargs.pop('network', None)
        guid = None
        if name.startswith('net-'):
            guid = name
            name = None

        try:
            if guid:
                network = find_network_guid(
                    client, guid, network_type)
                name = network.metadata.name

            else:
                network = find_network_name(
                    client, name, network_type)
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
) -> Munch:

    if network_type:
        networks = client.list_networks(query={'network_type': network_type})
    else:
        networks = client.list_networks()

    for network in networks:
        if network.status and network.status.phase == DeploymentPhaseConstants.DEPLOYMENT_STOPPED.value:
            continue
        if guid == network.metadata.guid:
            return network

    raise NetworkNotFound()

def find_network_guid(client: Client, name: str, version: str = None) -> str:
    packages = client.get_all_packages(name=name, version=version)
    if len(packages) == 0:
        click.secho("package not found", fg='red')
        raise SystemExit(1)

    if len(packages) == 1:
        return packages[0].packageId

    options = {}
    for pkg in packages:
        options[pkg.packageId] = '{} ({})'.format(pkg.packageName, pkg.packageVersion)

    choice = show_selection(options, header='Following packages were found with the same name')
    return choice


def fetch_networks(
        client: Client,
        network_name_or_regex: str,
        network_type: str,
        include_all: bool,
) -> List[Network]:

    if network_type:
        networks = client.list_networks(query={'network_type': network_type})
    else:
        networks = client.list_networks()

    if include_all:
        return networks

    result = []
    for n in networks:
        if re.search(network_name_or_regex, n.metadata.name):
            result.append(n)

    return result

def print_networks_for_confirmation(networks: List[Munch]) -> None:
    headers = ['Name', 'Type']
    data = [[n.metadata.name, n.spec.type] for n in networks]
    tabulate_data(data, headers)
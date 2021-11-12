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
from click_spinner import spinner
from rapyuta_io.clients.native_network import NativeNetwork, Parameters, NativeNetworkLimits
from rapyuta_io.clients.package import Runtime, ROSDistro

from riocli.config import new_client


def create_native_network(name: str, ros: str, device_guid: str = None, network_interface: str = None,
                          limit: str = None, restart_policy: str = None, **kwargs: typing.Any) -> None:
    client = new_client()

    ros_distro = ROSDistro(ros)
    runtime = Runtime.CLOUD

    if limit is not None:
        limit = getattr(NativeNetworkLimits, limit.upper())

    device = None
    if device_guid:
        runtime = Runtime.DEVICE
        device = client.get_device(device_id=device_guid)

    parameters = Parameters(limits=limit, device=device, network_interface=network_interface,
                            restart_policy=restart_policy)
    with spinner():
        client.create_native_network(NativeNetwork(name, runtime=runtime,
                                                   ros_distro=ros_distro,
                                                   parameters=parameters))

    click.secho('Native Network created successfully!', fg='green')


def inspect_native_network(network_guid: str) -> dict:
    client = new_client()
    network = client.get_native_network(network_guid)

    return {
        'created_at': network.created_at,
        'updated_at': network.updated_at,
        'creator': network.creator,
        'guid': network.guid,
        'internal_deployment_guid': network.internal_deployment_guid,
        'internal_deployment_status': network.internal_deployment_status.__dict__,
        'name': network.name,
        'owner_project': network.owner_project,
        'parameters': {
            'limits': network.parameters.limits.__dict__,
        },
        'ros_distro': network.ros_distro.value,
        'runtime': network.runtime.value,
    }

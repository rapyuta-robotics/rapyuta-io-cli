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
from rapyuta_io import ROSDistro
from rapyuta_io.clients.common_models import Limits
from rapyuta_io.clients.package import RestartPolicy
from rapyuta_io.clients.routed_network import Parameters

from riocli.config import new_client


def create_routed_network(name: str, ros: str, device_guid: str = None,
                          network_interface: str = None,
                          cpu: float = 0, memory: int = 0,
                          restart_policy: str = None,
                          **kwargs: typing.Any) -> None:
    client = new_client()
    ros_distro = ROSDistro(ros)

    limit = None
    if cpu or memory:
        if device_guid:
            raise Exception(
                'Routed network for device does not support cpu or memory')
        limit = Limits(cpu, memory)

    if restart_policy:
        restart_policy = RestartPolicy(restart_policy)

    if device_guid:
        device = client.get_device(device_id=device_guid)
        client.create_device_routed_network(name=name, ros_distro=ros_distro,
                                            shared=False,
                                            device=device,
                                            network_interface=network_interface,
                                            restart_policy=restart_policy)
    else:
        parameters = None if not limit else Parameters(limit)
        client.create_cloud_routed_network(name, ros_distro=ros_distro,
                                           shared=False,
                                           parameters=parameters)

    click.secho('Routed Network created successfully!', fg='green')


def inspect_routed_network(network_guid: str) -> dict:
    client = new_client()
    network = client.get_routed_network(network_guid)

    # TODO: Validate if all fields are present (Keep it consistent with Native Network's Inspect)

    return {
        'created_at': network.CreatedAt,
        'updated_at': network.UpdatedAt,
        'creator': network.creator,
        'guid': network.guid,
        'internal_deployment_guid': network.internalDeploymentGUID,
        'internal_deployment_status': {
            'phase': network.internalDeploymentStatus.phase,
            'status': network.internalDeploymentStatus.status,
        },
        'name': network.name,
        'owner_project': network.ownerProject,
        'parameters': {
            'limits': {
                'memory': network.parameters.limits.memory,
                'cpu': network.parameters.limits.cpu,
            },
        },
        'ros_distro': network.rosDistro,
        'runtime': network.runtime,
        'status': network.status,
    }

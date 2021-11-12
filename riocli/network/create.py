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

from riocli.network.native_network import create_native_network
from riocli.network.routed_network import create_routed_network
from riocli.device.util import name_to_guid as device_name_to_guid


@click.command('create')
@click.argument('name', type=str)
@click.option('--network', help='Type of Network',
              type=click.Choice(['routed', 'native']), default='routed')
@click.option('--ros', help='Version of ROS',
              type=click.Choice(['kinetic', 'melodic', 'noetic']), default='melodic')
@click.option('--device', 'device_name', help='Device ID of the Device where Network will run (device only)')
@click.option('--limit', help='Resource Limit for Network (cloud only) '
                              '[x_small is only available for Native Network]',
              type=click.Choice(['x_small', 'small', 'medium', 'large']), default='small')
@click.option('--network-interface', '-nic', type=str,
              help='Network Interface on which Network will listen (device only)')
@click.option('--restart-policy', help='Restart policy for the Network (device only)',
              type=click.Choice(['always', 'no', 'on-failure']), default='always')
@device_name_to_guid
def create_network(name: str, network: str, **kwargs: typing.Any) -> None:
    """
    Create a new network
    """
    try:
        if network == 'routed':
            create_routed_network(name, **kwargs)
        else:
            create_native_network(name, **kwargs)
    except Exception as e:
        click.secho(str(e), fg='red')
        exit(1)

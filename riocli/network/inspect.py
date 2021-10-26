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

from riocli.network.native_network import inspect_native_network
from riocli.network.routed_network import inspect_routed_network
from riocli.network.util import name_to_guid
from riocli.utils import inspect_with_format


@click.command('inspect')
@click.option('--format', '-f', 'format_type',
              type=click.Choice(['json', 'yaml'], case_sensitive=False), default='yaml')
@click.argument('network-name', type=str)
@name_to_guid
def inspect_network(format_type: str, network_name: str, network_guid: str, network_type: str) -> None:
    """
    Inspect the network resource
    """
    try:
        if network_type == 'routed':
            data = inspect_routed_network(network_guid)
        else:
            data = inspect_native_network(network_guid)

        inspect_with_format(data, format_type)
    except Exception as e:
        click.secho(str(e), fg='red')
        exit(1)

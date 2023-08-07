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
import click
from click_help_colors import HelpColorsCommand
from yaspin.api import Yaspin

from riocli.config import new_client
from riocli.constants import Colors, Symbols
from riocli.network.util import name_to_guid
from riocli.utils.spinner import with_spinner


@click.command(
    'delete',
    cls=HelpColorsCommand,
    help_headers_color=Colors.YELLOW,
    help_options_color=Colors.GREEN,
)
@click.option('--force', '-f', is_flag=True, default=False,
              help='Skip confirmation', type=bool)
@click.option('--network', 'network_type', help='Type of Network',
              default=None,
              type=click.Choice(['routed', 'native']))
@click.argument('network-name', type=str)
@name_to_guid
@with_spinner(text='Deleting network...')
def delete_network(
        force: bool,
        network_name: str,
        network_guid: str,
        network_type: str,
        spinner: Yaspin = None
) -> None:
    """
    Deletes a network
    """
    if not force:
        with spinner.hidden():
            click.confirm(
                'Deleting {} network {} ({})'.
                format(network_type, network_name, network_guid),
                abort=True)

    try:
        client = new_client()

        if network_type == 'routed':
            client.delete_routed_network(network_guid)
        elif network_type == 'native':
            client.delete_native_network(network_guid)
        else:
            raise Exception('invalid network type')

        spinner.text = click.style(
            '{} network deleted successfully!'.format(network_type.capitalize()),
            fg=Colors.GREEN)
        spinner.green.ok(Symbols.SUCCESS)
    except Exception as e:
        spinner.text = click.style('Failed to delete network: {}'.format(e),
                                   fg=Colors.RED)
        spinner.red.fail(Symbols.ERROR)
        raise SystemExit(1) from e

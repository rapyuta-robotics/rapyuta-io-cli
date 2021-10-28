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
from click_help_colors import HelpColorsGroup

from riocli.network.create import create_network
from riocli.network.delete import delete_network
from riocli.network.inspect import inspect_network
from riocli.network.list import list_networks
from riocli.network.logs import network_logs


@click.group(
    invoke_without_command=False,
    cls=HelpColorsGroup,
    help_headers_color='yellow',
    help_options_color='green',
)
def network() -> None:
    """
    ROS Communication between the Deployments
    """
    pass

network.add_command(create_network)
network.add_command(delete_network)
network.add_command(list_networks)
network.add_command(inspect_network)
network.add_command(network_logs)

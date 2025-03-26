# Copyright 2024 Rapyuta Robotics
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

from riocli.vpn.connect import connect
from riocli.vpn.disconnect import disconnect
from riocli.vpn.flush import flush
from riocli.vpn.machines import machines
from riocli.vpn.ping import ping_all
from riocli.vpn.status import status


@click.group(
    invoke_without_command=False,
    cls=HelpColorsGroup,
    help_headers_color="yellow",
    help_options_color="green",
)
def vpn() -> None:
    """Connect to the rapyuta.io VPN

    You can connect to the rapyuta.io VPN from your system
    and access the machines in the VPN. You can view other
    machines in the VPN, ping them, and check the status of
    the VPN connection. You can also register a new machine
    that may not be able to run the CLI.
    """
    pass


vpn.add_command(connect)
vpn.add_command(disconnect)
vpn.add_command(status)
vpn.add_command(ping_all)
vpn.add_command(machines)
vpn.add_command(flush)

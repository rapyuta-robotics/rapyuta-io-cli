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

from riocli.device.tools.device_init import device_init
from riocli.device.tools.forward import port_forward
from riocli.device.tools.rapyuta_logs import rapyuta_agent_logs
from riocli.device.tools.ssh import device_ssh, ssh_authorize_key
from .scp import scp
from .service import service


@click.group(
    invoke_without_command=False,
    cls=HelpColorsGroup,
    help_headers_color="yellow",
    help_options_color="green",
)
def tools():
    """Tools for managing devices.

    A collection of commands that provide a way
    to conveniently interact with devices and services
    running on them. The commands also enable you to
    script and automate tasks on devices.
    """
    pass


tools.add_command(scp)
tools.add_command(device_ssh)
tools.add_command(device_init)
tools.add_command(ssh_authorize_key)
tools.add_command(service)
tools.add_command(port_forward)
tools.add_command(rapyuta_agent_logs)

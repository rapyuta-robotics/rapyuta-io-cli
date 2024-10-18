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

from riocli.constants import Colors
from riocli.hwil.create import create_device
from riocli.hwil.delete import delete_device
from riocli.hwil.execute import execute
from riocli.hwil.inspect import inspect_device
from riocli.hwil.list import list_devices
from riocli.hwil.login import login
from riocli.hwil.ssh import ssh


@click.group(
    name="hwil",
    invoke_without_command=False,
    cls=HelpColorsGroup,
    help_headers_color=Colors.YELLOW,
    help_options_color=Colors.GREEN,
)
def hwildevice():
    """Manage Hardware-in-the-Loop (HWIL) devices.

    Hardware-in-the-Loop (HWIL) devices are virtual devices that
    can be used to test devices on rapyuta.io. The set of commands
    provide a convenient way to manage these devices and access them.
    """
    pass


hwildevice.add_command(login)
hwildevice.add_command(create_device)
hwildevice.add_command(list_devices)
hwildevice.add_command(delete_device)
hwildevice.add_command(inspect_device)
hwildevice.add_command(execute)
hwildevice.add_command(ssh)

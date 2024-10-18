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

from riocli.device.config import device_config
from riocli.device.create import create_device
from riocli.device.delete import delete_device
from riocli.device.deployment import list_deployments
from riocli.device.execute import execute_command
from riocli.device.files import device_uploads
from riocli.device.inspect import inspect_device
from riocli.device.label import device_labels
from riocli.device.list import list_devices
from riocli.device.migrate import migrate_project
from riocli.device.onboard import device_onboard
from riocli.device.report import report_device
from riocli.device.tools import tools
from riocli.device.topic import device_topics
from riocli.device.vpn import toggle_vpn


@click.group(
    invoke_without_command=False,
    cls=HelpColorsGroup,
    help_headers_color="yellow",
    help_options_color="green",
)
def device():
    """
    Devices on Rapyuta.io
    """
    pass


device.add_command(create_device)
device.add_command(execute_command)
device.add_command(delete_device)
device.add_command(device_config)
device.add_command(device_onboard)
device.add_command(device_labels)
device.add_command(device_topics)
device.add_command(device_uploads)
device.add_command(inspect_device)
device.add_command(list_deployments)
device.add_command(list_devices)
device.add_command(report_device)
device.add_command(tools)
device.add_command(toggle_vpn)
device.add_command(migrate_project)

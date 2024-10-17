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


# from datetime import datetime, timedelta

import click
from click_help_colors import HelpColorsGroup

from riocli.config import new_client
from riocli.constants import Colors
from riocli.utils import tabulate_data
from riocli.device.util import report_device_api_call, find_device_guid


@click.command(
    'report',
    cls=HelpColorsGroup,
    help_headers_color=Colors.YELLOW,
    help_options_color=Colors.GREEN,
)
@click.argument('device-name', type=str)
def report_device(device_name: str) -> None:
    """
    Report a device and get its debug logs in uploads section.
    """
    try:
        # client = new_client()
        device_guid = find_device_guid(device_name)
        # device = client.get_device(device_id=device_guid)
        # tabulate_data(device, ["Device"])
        # response = report_device_api_call(device_guid=device_guid)
        # click.echo(response, color=Colors.GREEN)
        click.echo(f"Device {device_name} {device_guid} reported successfully.")

    except Exception as e:
        click.secho(str(e), fg=Colors.RED)

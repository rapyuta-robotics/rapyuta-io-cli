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
from rapyuta_io.clients.persistent_volumes import DiskCapacity

from riocli.constants import Colors, Symbols
from riocli.disk.util import create_cloud_disk
from riocli.utils.spinner import with_spinner

SUPPORTED_CAPACITIES = [
    DiskCapacity.GiB_4.value,
    DiskCapacity.GiB_8.value,
    DiskCapacity.GiB_16.value,
    DiskCapacity.GiB_32.value,
    DiskCapacity.GiB_64.value,
    DiskCapacity.GiB_128.value,
    DiskCapacity.GiB_256.value,
    DiskCapacity.GiB_512.value,
]


@click.command(
    'create',
    cls=HelpColorsCommand,
    help_headers_color=Colors.YELLOW,
    help_options_color=Colors.GREEN,
)
@click.argument('disk-name', type=str)
@click.option('--capacity', 'capacity', type=click.Choice(SUPPORTED_CAPACITIES),
              default=DiskCapacity.GiB_4.value, help='Disk size in GiB')
@with_spinner(text="Creating a new disk...")
def create_disk(
        disk_name: str,
        capacity: int = 4,
        spinner=None,
) -> None:
    """
    Creates a new disk
    """
    try:
        disk = create_cloud_disk(disk_name, capacity)

        spinner.text = click.style(
            'Disk {} ({}) created successfully.'.
            format(disk['name'], disk['guid']), fg=Colors.GREEN)
        spinner.green.ok(Symbols.SUCCESS)
    except Exception as e:
        spinner.text = click.style('Failed to create disk: {}'.format(e), fg=Colors.RED)
        spinner.red.fail(Symbols.ERROR)
        raise SystemExit(1)

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
from click_help_colors import HelpColorsCommand
from yaspin.api import Yaspin

from riocli.config import new_v2_client
from riocli.constants import Colors, Regions, Symbols
from riocli.disk.enum import DiskCapacity
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

SUPPORTED_REGIONS = [
    Regions.JP,
    Regions.US,
]


@click.command(
    "create",
    cls=HelpColorsCommand,
    help_headers_color=Colors.YELLOW,
    help_options_color=Colors.GREEN,
)
@click.argument("disk-name", type=str)
@click.option(
    "--capacity",
    "capacity",
    type=click.INT,
    default=DiskCapacity.GiB_4.value,
    help="Disk size in GiB. [4|8|16|32|64|128|256|512]",
)
@click.option(
    "--region",
    "region",
    type=click.Choice(SUPPORTED_REGIONS),
    default=Regions.JP,
    help="Region to create the disk in",
)
@with_spinner(text="Creating a new disk...")
def create_disk(
    disk_name: str, capacity: int = 4, region: str = "jp", spinner: Yaspin = None
) -> None:
    """Creates a new cloud disk.

    You can create a disk with a specific capacity and region.
    The command will create a disk and wait until it is ready
    to use.

    Usage Examples:

        Create a new 4GB disk in the JP region

            $ rio disk create DISK_NAME --capacity 4 --region jp
    """
    client = new_v2_client()
    payload = {
        "metadata": {"name": disk_name, "region": region},
        "spec": {"capacity": capacity, "runtime": "cloud"},
    }

    try:
        client.create_disk(payload)
        client.poll_disk(disk_name)
        spinner.text = click.style(
            "Disk {} created successfully.".format(disk_name), fg=Colors.GREEN
        )
        spinner.green.ok(Symbols.SUCCESS)
    except Exception as e:
        spinner.text = click.style("Failed to create disk: {}".format(e), fg=Colors.RED)
        spinner.red.fail(Symbols.ERROR)
        raise SystemExit(1)

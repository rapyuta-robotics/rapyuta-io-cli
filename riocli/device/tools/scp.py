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

from riocli.config import new_client
from riocli.constants import Colors, Symbols
from riocli.device.tools.util import copy_from_device, copy_to_device
from riocli.device.util import is_remote_path
from riocli.utils.spinner import with_spinner


@click.command(
    "scp",
    cls=HelpColorsCommand,
    help_headers_color=Colors.YELLOW,
    help_options_color=Colors.GREEN,
)
@click.argument("source", nargs=1)
@click.argument("destination", nargs=1)
@with_spinner(text="Copying files...")
def scp(source: str, destination: str, spinner: Yaspin = None) -> None:
    """SCP like interface to copy files to and from a device.

    Usage Examples:

        Copy a file from local filesystem to the device

        $ rio device tools scp /path/to/local/file <device-id|device-name>:/path/to/remote/file

        Copy a file from the device to the local filesystem

        $ rio device tools scp <device-id|device-name>:/path/to/remote/file /path/to/local/file
    """
    try:
        client = new_client()
        devices = client.get_all_devices()
        src_device_guid, src = is_remote_path(source, devices=devices)
        dest_device_guid, dest = is_remote_path(destination, devices=devices)

        if src_device_guid is None and dest_device_guid is None:
            raise Exception(
                "One of source or destination paths should be a remote "
                "path of the format <device-id|device-name>:path"
            )

        if src_device_guid is not None:
            with spinner.hidden():
                copy_from_device(src_device_guid, src, dest)

        if dest_device_guid is not None:
            with spinner.hidden():
                copy_to_device(dest_device_guid, src, dest)

        spinner.text = click.style("Files copied successfully", fg=Colors.GREEN)
        spinner.green.ok(Symbols.SUCCESS)
    except Exception as e:
        spinner.text = click.style("Failed to copy files: {}".format(e), fg=Colors.RED)
        spinner.red.fail(Symbols.ERROR)
        raise SystemExit(1)

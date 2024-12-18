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
from riocli.config import new_client
from rapyuta_io.clients.device import DeviceStatus
from riocli.constants import Colors, Symbols
from riocli.device.util import name_to_guid, generate_shared_url, upload_debug_logs
from riocli.utils.spinner import with_spinner


@click.command(
    "report",
    cls=HelpColorsCommand,
    help_headers_color=Colors.YELLOW,
    help_options_color=Colors.GREEN,
)
@click.option(
    "--force", "-f", "--silent", "force", is_flag=True, help="Skip confirmation"
)
@click.option(
    "--share",
    "-s",
    is_flag=True,
    help="Generate a public URL for sharing",
    default=False,
)
@click.option(
    "--expiry",
    "-e",
    help="Expiry time for the shared URL in days",
    default=7,
    required=False,
    show_default=True,
)
@click.argument("device-name", type=str)
@name_to_guid
@with_spinner(text="Upload debugging files...")
def report_device(
    device_name: str,
    device_guid: str,
    force: bool,
    share: bool,
    expiry: int,
    spinner=None,
) -> None:
    """
    Uploads device debug logs.

    Usage Examples:

        Report a device with confirmation prompt.

            $ rio device report DEVICE_NAME

        Report a device without confirmation prompt.

            $ rio device report -f DEVICE_NAME

        Report a device and generate a public URL for sharing.

            $ rio device report -s DEVICE_NAME

        Report a device with a custom expiry time for the shared URL.

            $ rio device report -s -e 10 DEVICE_NAME
    """
    device = new_client().get_device(device_guid)
    if device["status"] != DeviceStatus.ONLINE:
        spinner.text = click.style(
            "Device is not online. Skipping report.", fg=Colors.YELLOW
        )
        spinner.yellow.ok(Symbols.WARNING)
        return

    if not force:
        with spinner.hidden():
            click.confirm(
                "Report Device?",
                abort=True,
            )
    try:
        # Upload the debug logs
        response = upload_debug_logs(device_guid=device_guid)

        if share:
            spinner.text = click.style("Creating shared URL...", fg=Colors.YELLOW)
            public_url = generate_shared_url(
                device_guid, response["response"]["data"]["request_uuid"], expiry
            )
            click.secho("\nURL: {}".format(public_url.url), fg=Colors.GREEN)

        spinner.text = click.style("Device reported successfully.", fg=Colors.GREEN)
        spinner.green.ok(Symbols.SUCCESS)
    except Exception as e:
        spinner.text = click.style("Failed to report device: {}".format(e), fg=Colors.RED)
        spinner.red.fail(Symbols.ERROR)

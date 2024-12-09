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
import typing

import click
from click_help_colors import HelpColorsCommand
from yaspin.api import Yaspin

from riocli.config import new_hwil_client
from riocli.constants import Colors, Symbols
from riocli.utils.spinner import with_spinner


@click.command(
    "create",
    cls=HelpColorsCommand,
    help_headers_color=Colors.YELLOW,
    help_options_color=Colors.GREEN,
)
@click.option(
    "--arch",
    "arch",
    help="Device architecture",
    type=click.Choice(["amd64", "arm64"]),
    default="amd64",
)
@click.option(
    "--os",
    "os",
    help="Type of the OS",
    type=click.Choice(["debian", "ubuntu"]),
    default="ubuntu",
)
@click.option(
    "--codename",
    "codename",
    help="Code name of the OS",
    type=click.Choice(["bionic", "focal", "jammy", "noble", "bullseye"]),
    default="focal",
)
@click.option(
    "--expire-after",
    "expire_after",
    help="Duration after which the device will expire. Example: 12h, 1d, 600s, 10m",
    type=str,
    default="12h",
)
@click.argument("device-name", type=str)
@with_spinner(text="Creating device...")
@click.pass_context
def create_device(
    ctx: click.Context,
    device_name: str,
    arch: str,
    os: str,
    codename: str,
    expire_after: str,
    spinner: Yaspin = None,
) -> None:
    """Create a new hardware-in-the-loop device.

    You can specify the parameters to create the kind of device
    you want using the --arch, --os and the --codename flags.

    The --arch defines the architecture of the device, which
    can be either amd64 or arm64.

    The --os defines the type of the OS, which can be either
    debian or ubuntu.

    The --codename defines the code name of the OS, which can
    be either bionic, focal, jammy or bullseye.

    Usage Example:

      Create a new device with the name 'my-device' and the default

        $ rio hwil create my-device

      Create a new device with the name 'my-device' and custom
      parameters for example, arm64 architecture, debian OS and
      bullseye codename.

        $ rio hwil create my-device --arch arm64 --os debian --codename bullseye

    Note: All combinations of the --arch, --os and --codename flags may not always
    work. Please contact io-support for more information.
    """
    info = click.style(
        f"{Symbols.INFO} Device configuration = {os}:{codename}:{arch}",
        fg=Colors.CYAN,
        bold=True,
    )
    spinner.write(info)
    client = new_hwil_client()
    labels = prepare_device_labels_from_context(ctx)

    labels["expiry_after"] = expire_after

    try:
        client.create_device(device_name, arch, os, codename, labels)
        spinner.text = click.style(
            f"Device {device_name} created successfully.", fg=Colors.GREEN
        )
        spinner.green.ok(Symbols.SUCCESS)
    except Exception as e:
        spinner.text = click.style(f"Failed to create device: {str(e)}", fg=Colors.RED)
        spinner.red.fail(Symbols.ERROR)
        raise SystemExit(1)


def prepare_device_labels_from_context(ctx: click.Context) -> typing.Dict:
    user_email = ctx.obj.data.get("email_id", "")
    if user_email:
        user_email = user_email.split("@")[0]

    return {
        "user": user_email,
        "organization": ctx.obj.data.get("organization_id", ""),
        "project": ctx.obj.data.get("project_id", ""),
    }

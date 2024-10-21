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
import sys
import typing

import click
from click_help_colors import HelpColorsCommand

if sys.stdout.isatty():
    from yaspin import kbi_safe_yaspin as Spinner
else:
    from riocli.utils.spinner import DummySpinner as Spinner

from riocli.config import new_client
from riocli.constants import Colors, Symbols
from riocli.utils import tabulate_data, print_separator
from riocli.parameter.utils import list_trees
from riocli.device.util import fetch_devices


@click.command(
    "apply",
    cls=HelpColorsCommand,
    help_headers_color=Colors.YELLOW,
    help_options_color=Colors.GREEN,
)
@click.option(
    "--devices",
    type=click.STRING,
    multiple=True,
    default=(),
    help="Device names to apply configurations. If --device_name_pattern is"
    "provided, this will be ignored.",
)
@click.option(
    "--device-name-pattern",
    type=click.STRING,
    multiple=False,
    help="Device name regex pattern to apply configurations. Does not work with --devices.",
)
@click.option(
    "--tree-names",
    type=click.STRING,
    multiple=True,
    default=None,
    help="Tree names to apply to the device(s)",
)
@click.option("--retry-limit", type=click.INT, default=0, help="Retry limit")
@click.option(
    "-f",
    "--force",
    "--silent",
    "silent",
    is_flag=True,
    type=click.BOOL,
    default=False,
    help="Skip confirmation",
)
def apply_configurations(
    devices: typing.List,
    tree_names: typing.List[str] = None,
    retry_limit: int = 0,
    device_name_pattern: str = None,
    silent: bool = False,
) -> None:
    """Apply a set of configuration parameter trees to a list of devices.

    You can either specify the device names using the ``--devices`` flag or
    use the ``--device-name-pattern`` flag to apply configurations to devices.

    Note that the ``--devices`` flag will be ignored if the ``--device-name-pattern``
    flag is provided.

    You can specify the trees to apply using the ``--tree-names`` flag.

    Skip the confirmation prompt by using the ``--force`` or ``--silent`` or the ``-f`` flag.

    Usage Examples:

        Apply configurations to a list of devices

            $ rio parameter apply --devices device1 --devices device2 --tree-names tree1

        Apply configurations to devices using a regex pattern

            $ rio parameter apply --device-name-pattern 'amr.*' --tree-names params
    """
    client = new_client()

    if tree_names:
        validate_trees(tree_names)

    online_devices = client.get_all_devices(online_device=True)

    try:
        # If device_name_pattern is specified, fetch devices based on the pattern
        # else fetch all devices. That means, include_all is False if
        # device_name_pattern is specified for the fetch_devices function.
        include_all = not len(device_name_pattern or "") > 0
        online_devices = fetch_devices(
            client, device_name_pattern, include_all=include_all, online_devices=True
        )

        device_map = {d.name: d for d in online_devices}

        # If devices are specified, filter online devices based on the
        # list of device names. But if device_name_pattern is specified
        # this list of devices will not be honoured.
        if devices and not device_name_pattern:
            device_ids = {device_map[d].uuid: d for d in devices if d in device_map}
        else:
            device_ids = {v.uuid: k for k, v in device_map.items()}

        if not device_ids:
            click.secho(
                "{} No device(s) found online. Please check the name or pattern".format(
                    Symbols.ERROR
                ),
                fg=Colors.RED,
            )
            raise SystemExit(1)

        click.secho(
            "Online Devices: {}".format(",".join(device_ids.values())), fg=Colors.GREEN
        )

        printable_tree_names = ",".join(tree_names) if tree_names != "" else "*all*"

        click.secho("Config Trees: {}".format(printable_tree_names), fg=Colors.GREEN)

        if not silent:
            click.confirm(
                "Do you want to apply the configurations?", default=True, abort=True
            )

        with Spinner(text="Applying parameters..."):
            response = client.apply_parameters(
                list(device_ids.keys()), list(tree_names), retry_limit
            )

        print_separator()

        result = []
        for device in response:
            device_name = device_ids[device["device_id"]]
            success = device["success"] or "Partial"
            result.append([device_name, success])

        tabulate_data(result, headers=["Device", "Success"])
    except Exception as e:
        click.secho(
            "{} Failed to apply configs: {}".format(Symbols.ERROR, e), fg=Colors.RED
        )
        raise SystemExit(1) from e


def validate_trees(tree_names: typing.List[str]) -> None:
    available_trees = set(list_trees())
    if not set(tree_names).issubset(available_trees):
        raise Exception("one or more specified tree names are invalid")

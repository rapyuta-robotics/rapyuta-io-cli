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


@click.command(
    'apply',
    cls=HelpColorsCommand,
    help_headers_color=Colors.YELLOW,
    help_options_color=Colors.GREEN,
)
@click.option('--devices', type=click.STRING, multiple=True, default=(),
              help='Device names to apply configurations')
@click.option('--tree-names', type=click.STRING, multiple=True, default=None,
              help='Tree names to apply')
@click.option('--retry-limit', type=click.INT, default=0,
              help='Retry limit')
@click.option('-f', '--force', '--silent', 'silent', is_flag=True,
              type=click.BOOL, default=False,
              help="Skip confirmation")
def apply_configurations(
        devices: typing.List,
        tree_names: str = None,
        retry_limit: int = 0,
        silent: bool = False,
) -> None:
    """
    Apply a set of configurations to a list of devices
    """
    try:
        client = new_client()

        online_devices = client.get_all_devices(online_device=True)
        device_map = {d.name: d for d in online_devices}

        if devices:
            device_ids = {device_map[d].uuid: d for d in devices if
                          d in device_map}
        else:
            device_ids = {v.uuid: k for k, v in device_map.items()}

        if not device_ids:
            click.secho(
                "{} Invalid devices or no device is currently online".format(
                    Symbols.ERROR),
                fg=Colors.RED)
            raise SystemExit(1)

        click.secho('Online Devices: {}'.format(','.join(device_ids.values())),
                    fg=Colors.GREEN)

        printable_tree_names = ','.join(
            tree_names) if tree_names != "" else "*all*"

        click.secho('Config Trees: {}'.format(printable_tree_names),
                    fg=Colors.GREEN)

        if not silent:
            click.confirm(
                "Do you want to apply the configurations?",
                default=True, abort=True)

        with Spinner(text='Applying parameters...'):
            response = client.apply_parameters(
                list(device_ids.keys()),
                list(tree_names),
                retry_limit
            )

        print_separator()

        result = []
        for device in response:
            device_name = device_ids[device['device_id']]
            success = device['success'] or "Partial"
            result.append([device_name, success])

        tabulate_data(result, headers=["Device", "Success"])
    except IOError as e:
        click.secho(str(e.__traceback__), fg=Colors.RED)
        click.secho(str(e), fg=Colors.RED)
        raise SystemExit(1) from e

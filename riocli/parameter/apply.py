# Copyright 2021 Rapyuta Robotics
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

from riocli.config import new_client
from riocli.utils import tabulate_data, print_separator


@click.command('apply')
@click.option('--devices', type=click.STRING, multiple=True, default=(),
              help='Device names to apply configurations')
@click.option('--tree-names', type=click.STRING, multiple=True, default=None,
              help='Tree names to apply')
@click.option('--retry-limit', type=click.INT, default=0,
              help='Retry limit')
@click.option('--silent', type=click.BOOL, default=False, help="Skip confirmation")
def apply_configurations(devices: typing.List, tree_names: str = None, retry_limit: int = 0,
                         silent: bool = False) -> None:
    """
    Apply a set of configurations to a list of devices
    """
    try:
        client = new_client()

        online_devices = client.get_all_devices(online_device=True)
        device_map = {d.name: d for d in online_devices}

        if devices:
            device_ids = {device_map[d].uuid: d for d in devices if d in device_map}
        else:
            device_ids = {v.uuid: k for k, v in device_map.items()}

        if len(device_ids) == 0:
            click.secho("invalid devices or no device is currently online", fg='red')
            raise SystemExit(1)

        click.secho('Online Devices: {}'.format(','.join(device_ids.values())), fg='green')

        printable_tree_names = "*all*"
        if len(tree_names) > 0:
            printable_tree_names = ','.join(tree_names)

        click.secho('Config Trees: {}'.format(printable_tree_names), fg='green')

        if not silent:
            click.confirm(
                "Do you want to apply the configurations?",
                default=True, abort=True)

        response = client.apply_parameters(list(device_ids.keys()),
                                           list(tree_names),
                                           retry_limit)

        print_separator()

        result = []
        for device in response:
            device_name = device_ids[device['device_id']]
            success = device['success'] or "Partial"
            result.append([device_name, success])

        tabulate_data(result, headers=["Device", "Success"])
    except IOError as e:
        click.secho(str(e.__traceback__), fg='red')
        click.secho(str(e), fg='red')
        raise SystemExit(1)

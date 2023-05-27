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
import typing

import click
from rapyuta_io.utils.rest_client import HttpMethod

from riocli.constants import Colors
from riocli.disk.util import _api_call
from riocli.utils import tabulate_data


@click.command('list')
def list_disks() -> None:
    """
    List the disks in the selected project
    """
    try:
        disks = _api_call(HttpMethod.GET)
        disks = sorted(disks, key=lambda d: d['name'].lower())
        _display_disk_list(disks, show_header=True)
    except Exception as e:
        click.secho(str(e), fg=Colors.RED)
        raise SystemExit(1)


def _display_disk_list(disks: typing.Any, show_header: bool = True):
    headers = []
    if show_header:
        headers = (
            'Disk ID', 'Name', 'Status', 'Capacity',
            'Used', 'Available', 'Used By',
        )

    data = [[d['guid'],
             d['name'],
             d['status'],
             d['capacity'],
             d.get('used', 'NA'),
             d.get('available', 'NA'),
             d['usedBy']]
            for d in disks]

    tabulate_data(data, headers)

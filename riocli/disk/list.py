# Copyright 2022 Rapyuta Robotics
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
from rapyuta_io import Build
from rapyuta_io.utils.rest_client import HttpMethod

from riocli.disk.util import _api_call


@click.command('list')
def list_disks() -> None:
    """
    List the disks in the selected project
    """
    try:
        disks = _api_call(HttpMethod.GET)
        _display_disk_list(disks, show_header=True)
    except Exception as e:
        click.secho(str(e), fg='red')
        raise SystemExit(1)


def _display_disk_list(disks: typing.Any, show_header: bool = True):
    if show_header:
        click.secho('{:30} {:25} {:12} {:8} {:<64}'.format('Disk ID', 'Name', 'Status', 'Capacity', 'Used By'),
                    fg='yellow')

    for disk in disks:
        click.secho('{:30} {:25} {:12} {:8} {:<64}'.format(disk['guid'], disk['name'], disk['status'], disk['capacity'],
                                                           disk['usedBy']))

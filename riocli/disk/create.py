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
import click
from click_spinner import spinner
from rapyuta_io.clients.persistent_volumes import DiskCapacity
from rapyuta_io.utils.rest_client import HttpMethod

from riocli.disk.util import _api_call


@click.command('create')
@click.argument('disk-name', type=str)
@click.option('--capacity', 'capacity', type=int)
def create_disk(disk_name: str, capacity: int) -> None:
    """
    Creates a new disk
    """
    try:
        capacity = DiskCapacity(capacity)
        with spinner():
            payload = {
                "name": disk_name,
                "diskType": "ssd",
                "runtime": "cloud",
                "capacity": DiskCapacity(capacity).value,
            }
            disk = _api_call(HttpMethod.POST, payload=payload)

        click.secho('Disk {} ({}) created successfully!'.
                    format(disk['name'], disk['guid']), fg='green')
    except Exception as e:
        click.secho(str(e), fg='red')
        raise SystemExit(1)

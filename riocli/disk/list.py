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
import click

from riocli.constants import Colors
from riocli.config import new_v2_client
from riocli.disk.util import display_disk_list


@click.command('list')
def list_disks() -> None:
    """
    List the disks in the selected project
    """
    try:
        client = new_v2_client(with_project=True)
        disks = client.list_disks()
        display_disk_list(disks, show_header=True)
    except Exception as e:
        click.secho(str(e), fg=Colors.RED)
        raise SystemExit(1)

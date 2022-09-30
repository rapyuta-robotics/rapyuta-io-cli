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
from click_help_colors import HelpColorsGroup

from riocli.disk.create import create_disk
from riocli.disk.list import list_disks
from riocli.disk.delete import delete_disk


@click.group(
    invoke_without_command=False,
    cls=HelpColorsGroup,
    help_headers_color='yellow',
    help_options_color='green',
)
def disk() -> None:
    """
    Persistent disks
    """
    pass


disk.add_command(list_disks)
disk.add_command(create_disk)
disk.add_command(delete_disk)
#disk.add_command(inspect_project)

# Copyright 2025 Rapyuta Robotics
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

from riocli.backup.create import create_backup
from riocli.backup.delete import delete_backup
from riocli.backup.inspect import inspect_backup
from riocli.backup.list import list_backups
from riocli.constants import Colors
from riocli.utils import AliasedGroup


@click.group(
    invoke_without_command=False,
    cls=AliasedGroup,
    help_headers_color=Colors.YELLOW,
    help_options_color=Colors.GREEN,
)
def backup() -> None:
    """Manage database backups.

    Create, list, inspect, and delete managed database backups. Backups are
    first-class resources and survive deletion of their source database.
    Use ``rio apply`` to create backups from a manifest file.
    """
    pass


backup.add_command(list_backups)
backup.add_command(inspect_backup)
backup.add_command(create_backup)
backup.add_command(delete_backup)

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

from riocli.constants import Colors
from riocli.restore.create import create_restore
from riocli.restore.inspect import inspect_restore
from riocli.restore.list import list_restores
from riocli.utils import AliasedGroup


@click.group(
    invoke_without_command=False,
    cls=AliasedGroup,
    help_headers_color=Colors.YELLOW,
    help_options_color=Colors.GREEN,
)
def restore() -> None:
    """Restore data into a running database.

    A restore loads logical databases into a live, running database, from either
    a backup or an old on-device data directory. The latter is how a
    major-version migration is done: create the new database, then restore into
    it from the old data directory.

    A restore never creates a database, and never touches logical databases
    outside the ones it is given. Restores are sub-resources of a database, so
    every command takes the target with --database.

    Use ``rio apply`` to run a restore from a manifest file.
    """
    pass


restore.add_command(list_restores)
restore.add_command(inspect_restore)
restore.add_command(create_restore)

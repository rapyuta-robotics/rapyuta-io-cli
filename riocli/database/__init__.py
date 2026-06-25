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
from riocli.database.delete import delete_database
from riocli.database.inspect import inspect_database
from riocli.database.list import list_databases
from riocli.utils import AliasedGroup


@click.group(
    invoke_without_command=False,
    cls=AliasedGroup,
    help_headers_color=Colors.YELLOW,
    help_options_color=Colors.GREEN,
)
def database() -> None:
    """Manage PostgreSQL databases.

    Create, list, inspect, and delete managed databases.
    Use ``rio apply`` to create or update databases from a manifest file.
    """
    pass


database.add_command(list_databases)
database.add_command(inspect_database)
database.add_command(delete_database)

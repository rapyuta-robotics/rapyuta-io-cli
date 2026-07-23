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
from click_help_colors import HelpColorsCommand
from rapyuta_io_sdk_v2 import walk_pages

from riocli.backup.util import display_backup_list
from riocli.config import new_v2_client
from riocli.constants import Colors


@click.command(
    "list",
    cls=HelpColorsCommand,
    help_headers_color=Colors.YELLOW,
    help_options_color=Colors.GREEN,
)
@click.option(
    "--database",
    "-d",
    "database",
    type=click.STRING,
    default=None,
    help="Filter backups by their source database",
)
@click.option(
    "--label",
    "-l",
    "labels",
    multiple=True,
    type=click.STRING,
    default=(),
    help="Filter the backup list by labels",
)
def list_backups(database: str, labels: list[str]) -> None:
    """List the backups in the current project.

    Backups are first-class resources and survive the deletion of their
    source database.

    Usage Examples:

        $ rio backup list

        $ rio backup list --database orders-db

        $ rio backup list -l app=orders
    """
    try:
        client = new_v2_client(with_project=True)
        backups = []
        for page in walk_pages(client.list_backups, label_selector=labels):
            backups.extend(page)
        display_backup_list(backups, show_header=True)
    except Exception as e:
        click.secho(str(e), fg=Colors.RED)
        raise SystemExit(1) from e

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

import functools
from queue import Queue

import click
from click_help_colors import HelpColorsCommand
from rapyuta_io_sdk_v2 import Client
from yaspin.api import Yaspin

from riocli.config import new_v2_client
from riocli.constants import Colors, Symbols
from riocli.restore.model import Restore
from riocli.restore.util import display_restore_list, fetch_restores
from riocli.utils import tabulate_data
from riocli.utils.execute import apply_func_with_result
from riocli.utils.spinner import with_spinner


@click.command(
    "delete",
    cls=HelpColorsCommand,
    help_headers_color=Colors.YELLOW,
    help_options_color=Colors.GREEN,
)
@click.option(
    "--database",
    "-d",
    "database",
    type=click.STRING,
    required=True,
    help="Database the restore(s) belong to",
)
@click.option(
    "--force", "-f", is_flag=True, default=False, help="Skip confirmation", type=bool
)
@click.option(
    "-a",
    "--all",
    "delete_all",
    is_flag=True,
    default=False,
    help="Delete every restore record of the database",
)
@click.option(
    "--workers",
    "-w",
    help="Number of parallel workers while deleting restores. Defaults to 10",
    type=int,
    default=10,
)
@click.argument("restore-name-or-regex", type=str, default="")
@with_spinner(text="Deleting restore...")
def delete_restore(
    database: str,
    force: bool,
    restore_name_or_regex: str,
    delete_all: bool = False,
    workers: int = 10,
    spinner: Yaspin = None,
) -> None:
    """Delete one or more restore records.

    This removes the record, not the restored data: by the time a restore can be
    deleted its effect is already part of the live database.

    Usage Examples:

        Delete a restore by name

            $ rio restore delete orders-db-restore --database orders-db

        Delete without confirmation

            $ rio restore delete orders-db-restore -d orders-db --force

        Delete every restore record of a database

            $ rio restore delete -d orders-db --all

        Delete restores using a regex pattern

            $ rio restore delete "orders.*" -d orders-db
    """
    client = new_v2_client()

    if not (restore_name_or_regex or delete_all):
        spinner.text = "Nothing to delete"
        spinner.green.ok(Symbols.SUCCESS)
        return

    try:
        restores = fetch_restores(client, database, restore_name_or_regex, delete_all)
    except Exception as e:
        spinner.text = click.style(f"Failed to find restore(s): {e}", Colors.RED)
        spinner.red.fail(Symbols.ERROR)
        raise SystemExit(1) from e

    if not restores:
        spinner.text = "Restore(s) not found"
        spinner.green.ok(Symbols.SUCCESS)
        return

    with spinner.hidden():
        display_restore_list(restores)

    spinner.write("")

    if not force:
        with spinner.hidden():
            click.confirm(
                "Do you want to delete the above restore(s)?", default=True, abort=True
            )

    try:
        f = functools.partial(_apply_delete, client, database)
        result = apply_func_with_result(
            f=f, items=restores, workers=workers, key=lambda x: x[0]
        )
        data, statuses = [], []
        for name, status, msg in result:
            fg = Colors.GREEN if status else Colors.RED
            icon = Symbols.SUCCESS if status else Symbols.ERROR

            statuses.append(status)
            data.append([click.style(name, fg), click.style(f"{icon}  {msg}", fg)])

        with spinner.hidden():
            tabulate_data(data, headers=["Name", "Status"])

        if not any(statuses):
            spinner.write("")
            spinner.text = click.style("Failed to delete restore(s).", Colors.RED)
            spinner.red.fail(Symbols.ERROR)
            raise SystemExit(1)

        icon = Symbols.SUCCESS if all(statuses) else Symbols.WARNING
        fg = Colors.GREEN if all(statuses) else Colors.YELLOW
        text = "successfully" if all(statuses) else "partially"

        spinner.text = click.style(f"Restore(s) deleted {text}.", fg)
        spinner.ok(click.style(icon, fg))
    except Exception as e:
        spinner.text = click.style(f"Failed to delete restore(s): {e}", Colors.RED)
        spinner.red.fail(Symbols.ERROR)
        raise SystemExit(1) from e


def _apply_delete(client: Client, database: str, result: Queue, restore: Restore) -> None:
    try:
        client.delete_restore(database=database, name=restore.metadata.name)
        result.put((restore.metadata.name, True, "Restore deleted successfully"))
    except Exception as e:
        result.put((restore.metadata.name, False, str(e)))

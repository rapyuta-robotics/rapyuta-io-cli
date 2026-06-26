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

from riocli.backup.model import Backup
from riocli.backup.util import display_backup_list, fetch_backups
from riocli.config import new_v2_client
from riocli.constants import Colors, Symbols
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
    "--force", "-f", is_flag=True, default=False, help="Skip confirmation", type=bool
)
@click.option(
    "-a",
    "--all",
    "delete_all",
    is_flag=True,
    default=False,
    help="Delete all backups in the project",
)
@click.option(
    "--workers",
    "-w",
    help="Number of parallel workers while deleting backups. Defaults to 10",
    type=int,
    default=10,
)
@click.argument("backup-name-or-regex", type=str, default="")
@with_spinner(text="Deleting backup...")
def delete_backup(
    force: bool,
    backup_name_or_regex: str,
    delete_all: bool = False,
    workers: int = 10,
    spinner: Yaspin = None,
) -> None:
    """Delete one or more backups with a name or regex pattern.

    Deleting a backup also removes its linked file-upload archives.

    Usage Examples:

        Delete a backup by name

            $ rio backup delete orders-nightly

        Delete without confirmation

            $ rio backup delete orders-nightly --force

        Delete all backups in the project

            $ rio backup delete --all

        Delete backups using a regex pattern

            $ rio backup delete "orders.*"
    """
    client = new_v2_client()

    if not (backup_name_or_regex or delete_all):
        spinner.text = "Nothing to delete"
        spinner.green.ok(Symbols.SUCCESS)
        return

    try:
        backups = fetch_backups(client, backup_name_or_regex, delete_all)
    except Exception as e:
        spinner.text = click.style(f"Failed to find backup(s): {e}", Colors.RED)
        spinner.red.fail(Symbols.ERROR)
        raise SystemExit(1) from e

    if not backups:
        spinner.text = "Backup(s) not found"
        spinner.green.ok(Symbols.SUCCESS)
        return

    with spinner.hidden():
        display_backup_list(backups)

    spinner.write("")

    if not force:
        with spinner.hidden():
            click.confirm(
                "Do you want to delete the above backup(s)?", default=True, abort=True
            )

    try:
        f = functools.partial(_apply_delete, client)
        result = apply_func_with_result(
            f=f, items=backups, workers=workers, key=lambda x: x[0]
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
            spinner.text = click.style("Failed to delete backup(s).", Colors.RED)
            spinner.red.fail(Symbols.ERROR)
            raise SystemExit(1)

        icon = Symbols.SUCCESS if all(statuses) else Symbols.WARNING
        fg = Colors.GREEN if all(statuses) else Colors.YELLOW
        text = "successfully" if all(statuses) else "partially"

        spinner.text = click.style(f"Backup(s) deleted {text}.", fg)
        spinner.ok(click.style(icon, fg))
    except Exception as e:
        spinner.text = click.style(f"Failed to delete backup(s): {e}", Colors.RED)
        spinner.red.fail(Symbols.ERROR)
        raise SystemExit(1) from e


def _apply_delete(client: Client, result: Queue, backup: Backup) -> None:
    try:
        client.delete_backup(guid=backup.metadata.guid)
        result.put((backup.metadata.name, True, "Backup deleted successfully"))
    except Exception as e:
        result.put((backup.metadata.name, False, str(e)))

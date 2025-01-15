# Copyright 2024 Rapyuta Robotics
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
from yaspin.api import Yaspin

from riocli.config import new_v2_client
from riocli.constants import Colors, Symbols
from riocli.disk.model import Disk
from riocli.disk.util import display_disk_list, fetch_disks
from riocli.utils import tabulate_data
from riocli.utils.execute import apply_func_with_result
from riocli.utils.spinner import with_spinner
from riocli.v2client import Client


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
    help="Deletes all disks in the project",
)
@click.option(
    "--workers",
    "-w",
    help="Number of parallel workers while running deleting disks. Defaults to 10",
    type=int,
    default=10,
)
@click.argument("disk-name-or-regex", type=str)
@with_spinner(text="Deleting disk...")
def delete_disk(
    force: bool,
    disk_name_or_regex: str,
    delete_all: bool = False,
    workers: int = 10,
    spinner: Yaspin = None,
) -> None:
    """Delete one or more disks with a name or a regex pattern.

    You can specify a name or a regex pattern to delete one
    or more disks.

    If you want to delete all the disks, then
    simply use the ``--all`` flag.

    If you want to delete disks without confirmation, then use the
    ``--force`` or ``--silent`` or ``-f``.

    Usage Examples:

        Delete a disk by name

            $ rio disk delete DISK_NAME

        Delete a disk without confirmation

            $ rio disk delete DISK_NAME --force

        Delete all disks in the project

            $ rio disk delete --all

        Delete disks using regex pattern

            $ rio disk delete "DISK.*"
    """
    client = new_v2_client()

    if not (disk_name_or_regex or delete_all):
        spinner.text = "Nothing to delete"
        spinner.green.ok(Symbols.SUCCESS)
        return

    try:
        disks = fetch_disks(client, disk_name_or_regex, delete_all)
    except Exception as e:
        spinner.text = click.style("Failed to find disk(s): {}".format(e), Colors.RED)
        spinner.red.fail(Symbols.ERROR)
        raise SystemExit(1) from e

    if not disks:
        spinner.text = "Disk(s) not found"
        spinner.green.ok(Symbols.SUCCESS)
        return

    with spinner.hidden():
        display_disk_list(disks)

    spinner.write("")

    if not force:
        with spinner.hidden():
            click.confirm(
                "Do you want to delete the above disk(s)?", default=True, abort=True
            )

    try:
        f = functools.partial(_apply_delete, client)
        result = apply_func_with_result(
            f=f, items=disks, workers=workers, key=lambda x: x[0]
        )
        data, statuses = [], []
        for name, status, msg in result:
            fg = Colors.GREEN if status else Colors.RED
            icon = Symbols.SUCCESS if status else Symbols.ERROR

            statuses.append(status)
            data.append(
                [click.style(name, fg), click.style("{}  {}".format(icon, msg), fg)]
            )

        with spinner.hidden():
            tabulate_data(data, headers=["Name", "Status"])

        # When no disk is deleted, raise an exception.
        if not any(statuses):
            spinner.write("")
            spinner.text = click.style("Failed to delete disk(s).", Colors.RED)
            spinner.red.fail(Symbols.ERROR)
            raise SystemExit(1)

        icon = Symbols.SUCCESS if all(statuses) else Symbols.WARNING
        fg = Colors.GREEN if all(statuses) else Colors.YELLOW
        text = "successfully" if all(statuses) else "partially"

        spinner.text = click.style("Disk(s) deleted {}.".format(text), fg)
        spinner.ok(click.style(icon, fg))
    except Exception as e:
        spinner.text = click.style("Failed to delete disk(s): {}".format(e), Colors.RED)
        spinner.red.fail(Symbols.ERROR)
        raise SystemExit(1) from e


def _apply_delete(client: Client, result: Queue, disk: Disk) -> None:
    try:
        client.delete_disk(name=disk.metadata.name)
        result.put((disk.metadata.name, True, "Disk deleted successfully"))
    except Exception as e:
        result.put((disk.metadata.name, False, str(e)))

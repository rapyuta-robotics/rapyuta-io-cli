import functools
from queue import Queue

import click
from click_help_colors import HelpColorsCommand
from rapyuta_io_sdk_v2 import Client
from yaspin.api import Yaspin

from riocli.config import new_v2_client
from riocli.constants import Colors, Symbols
from riocli.database.util import fetch_databases, print_databases_for_confirmation
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
    "--force", "-f", "--silent", is_flag=True, default=False, help="Skip confirmation"
)
@click.option(
    "-a",
    "--all",
    "delete_all",
    is_flag=True,
    default=False,
    help="Delete all databases in the project",
)
@click.option(
    "--workers",
    "-w",
    help="Number of parallel workers while deleting databases. Defaults to 10.",
    type=int,
    default=10,
)
@click.argument("database-name-or-regex", type=str, default="")
@with_spinner(text="Deleting database...")
def delete_database(
    force: bool,
    database_name_or_regex: str,
    delete_all: bool = False,
    workers: int = 10,
    spinner: Yaspin = None,
) -> None:
    """Delete one or more databases with a name or a regex pattern.

    You can specify a database name or a regex pattern to delete one
    or more databases.

    If you want to delete all the databases, use the ``--all`` flag.

    If you want to skip confirmation, use the ``--force`` or ``-f`` flag.

    Usage Examples:

        Delete a database by name

            $ rio database delete DATABASE_NAME

        Delete a database without confirmation

            $ rio database delete DATABASE_NAME --force

        Delete all databases in the project

            $ rio database delete --all

        Delete databases using regex pattern

            $ rio database delete "db-.*"
    """
    client = new_v2_client()

    if not (database_name_or_regex or delete_all):
        spinner.text = "Nothing to delete"
        spinner.green.ok(Symbols.SUCCESS)
        return

    try:
        databases = fetch_databases(client, database_name_or_regex, delete_all)
    except Exception as e:
        spinner.text = click.style(f"Failed to find database(s): {e}", Colors.RED)
        spinner.red.fail(Symbols.ERROR)
        raise SystemExit(1) from e

    if not databases:
        spinner.text = "Database(s) not found"
        spinner.green.ok(Symbols.SUCCESS)
        return

    with spinner.hidden():
        print_databases_for_confirmation(databases)

    spinner.write("")

    if not force:
        with spinner.hidden():
            click.confirm(
                "Do you want to delete the above database(s)?", default=True, abort=True
            )

    try:
        f = functools.partial(_apply_delete, client)
        result = apply_func_with_result(
            f=f, items=databases, workers=workers, key=lambda x: x[0]
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
            spinner.text = click.style("Failed to delete database(s).", Colors.RED)
            spinner.red.fail(Symbols.ERROR)
            raise SystemExit(1)

        icon = Symbols.SUCCESS if all(statuses) else Symbols.WARNING
        fg = Colors.GREEN if all(statuses) else Colors.YELLOW
        text = "successfully" if all(statuses) else "partially"

        spinner.write("")
        spinner.text = click.style(f"Database(s) deleted {text}.", fg)
        spinner.ok(click.style(icon, fg))
    except Exception as e:
        spinner.text = click.style(f"Failed to delete database(s): {e}", Colors.RED)
        spinner.red.fail(Symbols.ERROR)
        raise SystemExit(1) from e


def _apply_delete(client: Client, result: Queue, database) -> None:
    try:
        client.delete_database(name=database.metadata.name)
        result.put((database.metadata.name, True, "Database Deleted Successfully"))
    except Exception as e:
        result.put((database.metadata.name, False, str(e)))

import click
from click_help_colors import HelpColorsCommand

from riocli.config import new_v2_client
from riocli.constants import Colors, Symbols
from riocli.utils import AliasedGroup, inspect_with_format, tabulate_data
from riocli.utils.spinner import with_spinner


@click.group(
    "backup",
    invoke_without_command=False,
    cls=AliasedGroup,
    help_headers_color=Colors.YELLOW,
    help_options_color=Colors.GREEN,
)
def backup() -> None:
    """Manage backups for a database."""
    pass


@backup.command(
    "list",
    cls=HelpColorsCommand,
    help_headers_color=Colors.YELLOW,
    help_options_color=Colors.GREEN,
)
@click.argument("database-name")
def list_backups(database_name: str) -> None:
    """List backups for a database.

    Usage Examples:

        $ rio database backup list DATABASE_NAME
    """
    try:
        client = new_v2_client(with_project=True)
        result = client.list_backups(database_name=database_name)
        backups = result.items or []
        _display_backup_list(backups, show_header=True)
    except Exception as e:
        click.secho(str(e), fg=Colors.RED)
        raise SystemExit(1)


def _display_backup_list(backups: list, show_header: bool = True) -> None:
    headers = []
    if show_header:
        headers = ["Backup ID", "Database", "Upload Status"]

    data = []
    for b in backups:
        data.append(
            [
                b.spec.id if b.spec else "",
                b.spec.databaseName if b.spec else "",
                b.spec.status if b.spec else "",
            ]
        )

    tabulate_data(data, headers)


@backup.command(
    "inspect",
    cls=HelpColorsCommand,
    help_headers_color=Colors.YELLOW,
    help_options_color=Colors.GREEN,
)
@click.option(
    "--format",
    "-f",
    "format_type",
    default="yaml",
    type=click.Choice(["json", "yaml"], case_sensitive=False),
)
@click.argument("database-name")
@click.argument("backup-id")
def inspect_backup(format_type: str, database_name: str, backup_id: str) -> None:
    """Inspect a database backup.

    Prints the backup resource in the specified format.
    The supported formats are ``json`` and ``yaml``. Default is ``yaml``.

    Usage Examples:

        $ rio database backup inspect DATABASE_NAME BACKUP_ID
    """
    try:
        client = new_v2_client()
        b = client.get_backup(database_name=database_name, backup_id=backup_id)

        if not b:
            click.secho("backup not found", fg=Colors.RED)
            raise SystemExit(1)

        inspect_with_format(b.model_dump(exclude_none=True, by_alias=True), format_type)
    except Exception as e:
        click.secho(str(e), fg=Colors.RED)
        raise SystemExit(1)


@backup.command(
    "delete",
    cls=HelpColorsCommand,
    help_headers_color=Colors.YELLOW,
    help_options_color=Colors.GREEN,
)
@click.option(
    "--force", "-f", "--silent", is_flag=True, default=False, help="Skip confirmation"
)
@click.argument("database-name")
@click.argument("backup-id")
@with_spinner(text="Deleting backup...")
def delete_backup(
    force: bool,
    database_name: str,
    backup_id: str,
    spinner=None,
) -> None:
    """Delete a backup for a database.

    Usage Examples:

        $ rio database backup delete DATABASE_NAME BACKUP_ID
    """
    client = new_v2_client()

    if not force:
        with spinner.hidden():
            click.confirm(
                f"Do you want to delete backup {backup_id!r} for database {database_name!r}?",
                default=True,
                abort=True,
            )

    try:
        client.delete_backup(database_name=database_name, backup_id=backup_id)
        spinner.text = click.style("Backup deleted successfully.", Colors.GREEN)
        spinner.ok(click.style(Symbols.SUCCESS, Colors.GREEN))
    except Exception as e:
        spinner.text = click.style(f"Failed to delete backup: {e}", Colors.RED)
        spinner.red.fail(Symbols.ERROR)
        raise SystemExit(1) from e


@backup.command(
    "restore",
    cls=HelpColorsCommand,
    help_headers_color=Colors.YELLOW,
    help_options_color=Colors.GREEN,
)
@click.option(
    "--force", "-f", "--silent", is_flag=True, default=False, help="Skip confirmation"
)
@click.argument("database-name")
@click.argument("backup-id")
@with_spinner(text="Restoring backup...")
def restore_backup(
    force: bool,
    database_name: str,
    backup_id: str,
    spinner=None,
) -> None:
    """Restore a database from a backup.

    Usage Examples:

        $ rio database backup restore DATABASE_NAME BACKUP_ID
    """
    client = new_v2_client()

    if not force:
        with spinner.hidden():
            click.confirm(
                f"Do you want to restore database {database_name!r} from backup {backup_id!r}?",
                default=True,
                abort=True,
            )

    try:
        client.restore_backup(database_name=database_name, backup_id=backup_id)
        spinner.text = click.style("Restore initiated successfully.", Colors.GREEN)
        spinner.ok(click.style(Symbols.SUCCESS, Colors.GREEN))
    except Exception as e:
        spinner.text = click.style(f"Failed to restore backup: {e}", Colors.RED)
        spinner.red.fail(Symbols.ERROR)
        raise SystemExit(1) from e

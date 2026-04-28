import click

from riocli.constants import Colors
from riocli.database.backup import backup
from riocli.database.delete import delete_database
from riocli.database.inspect import inspect_database
from riocli.database.list import list_databases
from riocli.database.versions import list_database_versions
from riocli.utils import AliasedGroup


@click.group(
    invoke_without_command=False,
    cls=AliasedGroup,
    help_headers_color=Colors.YELLOW,
    help_options_color=Colors.GREEN,
)
def database() -> None:
    """Manage database resources."""
    pass


database.add_command(list_databases)
database.add_command(inspect_database)
database.add_command(delete_database)
database.add_command(list_database_versions)
database.add_command(backup)

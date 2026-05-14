import click
from click_help_colors import HelpColorsCommand

from riocli.config import new_v2_client
from riocli.constants import Colors
from riocli.utils import inspect_with_format


@click.command(
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
def inspect_database(format_type: str, database_name: str) -> None:
    """Inspect a database resource.

    Prints the database resource in the specified format.
    The supported formats are ``json`` and ``yaml``. Default is ``yaml``.

    Usage Examples:

        Inspect a database in YAML format

            $ rio database inspect DATABASE_NAME

        Inspect a database in JSON format

            $ rio database inspect DATABASE_NAME --format json
    """
    try:
        client = new_v2_client()
        db = client.get_database(database_name)

        if not db:
            click.secho("database not found", fg=Colors.RED)
            raise SystemExit(1)

        inspect_with_format(db.model_dump(exclude_none=True, by_alias=True), format_type)
    except Exception as e:
        click.secho(str(e), fg=Colors.RED)
        raise SystemExit(1)

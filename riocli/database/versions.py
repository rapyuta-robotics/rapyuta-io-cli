import click
from click_help_colors import HelpColorsCommand

from riocli.config import new_v2_client
from riocli.constants import Colors
from riocli.utils import tabulate_data


@click.command(
    "versions",
    cls=HelpColorsCommand,
    help_headers_color=Colors.YELLOW,
    help_options_color=Colors.GREEN,
)
def list_database_versions() -> None:
    """List supported database versions.

    Usage Examples:

        $ rio database versions
    """
    try:
        client = new_v2_client()
        versions = client.list_database_versions()
        data = [[v] for v in versions]
        tabulate_data(data, headers=["Supported Versions"])
    except Exception as e:
        click.secho(str(e), fg=Colors.RED)
        raise SystemExit(1)

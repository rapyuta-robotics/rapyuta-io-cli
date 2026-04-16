import click
from click_help_colors import HelpColorsCommand

from riocli.config import new_v2_client
from riocli.constants import Colors
from riocli.utils import tabulate_data


@click.command(
    "list",
    cls=HelpColorsCommand,
    help_headers_color=Colors.YELLOW,
    help_options_color=Colors.GREEN,
)
@click.option(
    "--wide", "-w", is_flag=True, default=False, help="Print more details", type=bool
)
def list_databases(wide: bool = False) -> None:
    """List all databases in the current project."""
    try:
        client = new_v2_client(with_project=True)
        result = client.list_databases()
        databases = sorted(result.items, key=lambda d: d.metadata.name.lower())
        _display_database_list(databases, show_header=True, wide=wide)
    except Exception as e:
        click.secho(str(e), fg=Colors.RED)
        raise SystemExit(1)


def _display_database_list(
    databases: list,
    show_header: bool = True,
    wide: bool = False,
) -> None:
    headers = []
    if show_header:
        headers = ["Name", "Type", "Version", "Primary Device", "Phase"]

    if show_header and wide:
        headers.extend(["GUID", "Creation Time (UTC)"])

    data = []
    for db in databases:
        version = ""
        primary_device = ""
        if db.spec.postgres:
            version = db.spec.postgres.version or ""
            primary_device = db.spec.postgres.primary.deviceName or ""

        row = [
            db.metadata.name,
            db.spec.type,
            version,
            primary_device,
            db.status.phase if db.status else "",
        ]

        if wide:
            row.extend([db.metadata.guid, db.metadata.createdAt])

        data.append(row)

    tabulate_data(data, headers)

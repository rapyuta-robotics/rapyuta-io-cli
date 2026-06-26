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

from riocli.backup.util import display_backup_list
from riocli.config import new_v2_client
from riocli.constants import Colors, Symbols


@click.command(
    "create",
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
    help="Source database for the backup",
)
@click.option(
    "--type",
    "-t",
    "backup_type",
    type=click.Choice(["scheduled", "onDemand"], case_sensitive=False),
    default="scheduled",
    help="Type of the backup. Defaults to scheduled",
)
@click.option(
    "--schedule",
    "-s",
    "schedule",
    type=click.STRING,
    default=None,
    help="Cron schedule (required when type is scheduled)",
)
@click.option(
    "--retention",
    "-r",
    "retention",
    type=click.INT,
    default=None,
    help="Number of backups to retain",
)
@click.argument("backup-name", type=str)
def create_backup(
    database: str,
    backup_type: str,
    schedule: str,
    retention: int,
    backup_name: str,
) -> None:
    """Create a backup for a database.

    A scheduled backup runs on the given cron schedule; an on-demand backup
    runs immediately.

    Usage Examples:

        Create a scheduled nightly backup

            $ rio backup create orders-nightly --database orders-db --schedule "0 2 * * *" --retention 7

        Trigger an on-demand backup

            $ rio backup create orders-adhoc --database orders-db --type onDemand
    """
    if backup_type == "scheduled" and not schedule:
        click.secho("--schedule is required when --type is scheduled", fg=Colors.RED)
        raise SystemExit(1)

    spec = {
        "type": backup_type,
        "database": database,
    }
    if schedule:
        spec["schedule"] = schedule
    if retention is not None:
        spec["retention"] = {"count": retention}

    body = {
        "apiVersion": "api.rapyuta.io/v2",
        "kind": "Backup",
        "metadata": {"name": backup_name},
        "spec": spec,
    }

    try:
        client = new_v2_client()
        backup = client.create_backup(body=body)
        click.secho(f"{Symbols.SUCCESS} Backup created successfully", fg=Colors.GREEN)
        display_backup_list([backup], show_header=True)
    except Exception as e:
        click.secho(str(e), fg=Colors.RED)
        raise SystemExit(1) from e

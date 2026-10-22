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

from datetime import datetime, timezone

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
    default=None,
    help="Type of the backup. Defaults to scheduled when --schedule is given, "
    "otherwise onDemand",
)
@click.option(
    "--schedule",
    "-s",
    "schedule",
    type=click.STRING,
    default=None,
    help="Cron schedule (required when type is scheduled)",
)
@click.argument("backup-name", type=str, required=False, default=None)
def create_backup(
    database: str,
    backup_type: str | None,
    schedule: str,
    backup_name: str | None,
) -> None:
    """Create a backup for a database.

    A scheduled backup runs on the given cron schedule; an on-demand backup
    runs once, immediately, and ends in Succeeded or Failed. A finished
    on-demand backup is kept as a record until you delete it.

    An on-demand backup requires the database to already have a running
    scheduled backup: it reuses that backup's Barman pod and WAL stream. A
    restore of the same database waits for a running on-demand backup to
    finish, and an on-demand backup waits for a running restore.

    Without --schedule the backup is on-demand. An on-demand backup may omit
    BACKUP_NAME; one is generated as <database>-ondemand-<UTC date-time>.

    Usage Examples:

        Create a scheduled nightly backup

            $ rio backup create orders-nightly --database orders-db --schedule "0 2 * * *"

        Trigger an on-demand backup with a generated name

            $ rio backup create --database orders-db

        Trigger an on-demand backup with a chosen name

            $ rio backup create orders-adhoc --database orders-db
    """
    backup_type = backup_type or ("scheduled" if schedule else "onDemand")

    if backup_type == "scheduled" and not schedule:
        click.secho("--schedule is required when --type is scheduled", fg=Colors.RED)
        raise SystemExit(1)

    if not backup_name:
        if backup_type == "scheduled":
            click.secho("BACKUP_NAME is required for a scheduled backup", fg=Colors.RED)
            raise SystemExit(1)

        backup_name = generated_backup_name(database)

    spec = {
        "type": backup_type,
        "database": database,
    }
    if schedule:
        spec["schedule"] = schedule

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


def generated_backup_name(database: str, now: datetime | None = None) -> str:
    """Name an on-demand backup <database>-ondemand-<UTC date-time>.

    The server caps names at 75 characters, so a long database name is cut.
    """
    stamp = (now or datetime.now(timezone.utc)).strftime("%Y%m%d-%H%M%S")
    suffix = f"-ondemand-{stamp}"
    return database[: 75 - len(suffix)] + suffix

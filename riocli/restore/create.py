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

from riocli.config import new_v2_client
from riocli.constants import Colors, Symbols
from riocli.restore.util import display_restore_list


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
    help="Target database. Must be running; the data is loaded into it",
)
@click.option(
    "--source",
    "-s",
    "source_type",
    type=click.Choice(["backup", "dataDirectory"], case_sensitive=False),
    default="backup",
    help="Where to restore from. Defaults to backup",
)
@click.option(
    "--backup",
    "-b",
    "backup_name",
    type=click.STRING,
    default=None,
    help="Source backup (required when --source is backup)",
)
@click.option(
    "--backup-run",
    "backup_run_id",
    type=click.STRING,
    default=None,
    help="Barman backup ID to restore. Defaults to the backup's latest run",
)
@click.option(
    "--old-data-directory",
    "old_data_directory",
    type=click.STRING,
    default=None,
    help="Absolute path of the old cluster (required when --source is dataDirectory)",
)
@click.option(
    "--source-version",
    "source_version",
    type=click.Choice(["16", "17", "18"]),
    default=None,
    help="Major version of the old cluster (required when --source is dataDirectory)",
)
@click.option(
    "--db",
    "databases",
    multiple=True,
    type=click.STRING,
    default=(),
    help="Logical database to restore. Repeatable. Defaults to every one in the source",
)
@click.option(
    "--clean",
    is_flag=True,
    default=False,
    help="Drop the objects being restored before recreating them",
)
@click.option(
    "--no-owner",
    "no_owner",
    is_flag=True,
    default=False,
    help="Skip restoring object ownership",
)
@click.option(
    "--if-exists",
    "if_exists",
    is_flag=True,
    default=False,
    help="Tolerate objects that are already absent. Only meaningful with --clean",
)
@click.argument("restore-name", type=str)
def create_restore(
    database: str,
    source_type: str,
    backup_name: str,
    backup_run_id: str,
    old_data_directory: str,
    source_version: str,
    databases: list[str],
    clean: bool,
    no_owner: bool,
    if_exists: bool,
    restore_name: str,
) -> None:
    """Restore data into a running database.

    Only the logical databases you name are touched; everything else in the
    target is left as it was. A restore is one-shot and is refused while another
    is still running against the same database.

    Usage Examples:

        Restore one logical database from a backup

            $ rio restore create orders-restore -d orders-db -b orders-nightly --db orders

        Restore every logical database the backup holds

            $ rio restore create orders-restore -d orders-db -b orders-nightly

        Migrate a v17 cluster into a new v18 database

            $ rio restore create orders-migrate -d orders-db-v18 \\
                --source dataDirectory \\
                --old-data-directory /opt/rapyuta/volumes/orders-db \\
                --source-version 17
    """
    source = {"type": source_type}

    if source_type == "backup":
        if not backup_name:
            click.secho("--backup is required when --source is backup", fg=Colors.RED)
            raise SystemExit(1)

        source["backupName"] = backup_name
        if backup_run_id:
            source["backupRunID"] = backup_run_id
    else:
        if not old_data_directory or not source_version:
            click.secho(
                "--old-data-directory and --source-version are required when "
                "--source is dataDirectory",
                fg=Colors.RED,
            )
            raise SystemExit(1)

        source["oldDataDirectory"] = old_data_directory
        source["sourceVersion"] = source_version

    spec = {"database": database, "source": source}

    if databases:
        spec["databases"] = list(databases)

    options = {}
    if clean:
        options["clean"] = True
    if no_owner:
        options["noOwner"] = True
    # pg_restore errors on --if-exists without --clean, so the device drops it;
    # say so here rather than letting it silently do nothing.
    if if_exists:
        if not clean:
            click.secho("--if-exists has no effect without --clean", fg=Colors.YELLOW)
        else:
            options["ifExists"] = True

    if options:
        spec["options"] = options

    body = {
        "apiVersion": "api.rapyuta.io/v2",
        "kind": "Restore",
        "metadata": {"name": restore_name},
        "spec": spec,
    }

    try:
        client = new_v2_client()
        restore = client.create_restore(body=body)
        click.secho(f"{Symbols.SUCCESS} Restore started", fg=Colors.GREEN)
        display_restore_list([restore], show_header=True)
        click.secho(
            f"\nFollow it with: rio restore inspect {restore_name} -d {database}",
            fg=Colors.YELLOW,
        )
    except Exception as e:
        click.secho(str(e), fg=Colors.RED)
        raise SystemExit(1) from e

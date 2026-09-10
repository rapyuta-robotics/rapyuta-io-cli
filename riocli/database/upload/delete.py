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
from riocli.utils.spinner import with_spinner


@click.command(
    "delete",
    cls=HelpColorsCommand,
    help_headers_color=Colors.YELLOW,
    help_options_color=Colors.GREEN,
)
@click.option(
    "--force",
    "-f",
    "--silent",
    "force",
    is_flag=True,
    default=False,
    help="Skip confirmation",
)
@click.option(
    "--database",
    "-d",
    type=click.STRING,
    default=None,
    help="Name or GUID of the database the archive must belong to.",
)
@click.argument("upload-guid", type=click.STRING)
@with_spinner(text="Deleting archive...")
def delete_upload(
    database: str | None, upload_guid: str, force: bool, spinner=None
) -> None:
    """Delete one uploaded backup archive.

    Archives outlive their backup and their database, so this is the only thing
    that removes one. The blob goes with it.

    Usage Examples:

        $ rio database upload delete fileupload-abc123

        $ rio database upload delete fileupload-abc123 --database orders-db
    """
    with spinner.hidden():
        if not force:
            target = f"archive {upload_guid}"
            if database:
                target += f" of {database}"
            click.confirm(f"Delete {target}?", abort=True)

    try:
        client = new_v2_client(with_project=True)
        client.delete_database_upload(guid=upload_guid, database=database)
        spinner.text = click.style("Archive deleted successfully.", fg=Colors.GREEN)
        spinner.green.ok(Symbols.SUCCESS)
    except Exception as e:
        spinner.text = click.style(str(e), fg=Colors.RED)
        spinner.red.fail(Symbols.ERROR)
        raise SystemExit(1) from e

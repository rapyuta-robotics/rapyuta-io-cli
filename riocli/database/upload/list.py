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
from rapyuta_io_sdk_v2 import walk_pages

from riocli.config import new_v2_client
from riocli.constants import Colors
from riocli.database.upload.util import display_archive_list


@click.command(
    "list",
    cls=HelpColorsCommand,
    help_headers_color=Colors.YELLOW,
    help_options_color=Colors.GREEN,
)
@click.argument("database", type=click.STRING)
def list_uploads(database: str) -> None:
    """List a database's uploaded backup archives.

    The Upload ID is what ``rio database restore create --file-upload`` takes.
    Archives are found by the database they belong to, so they remain listed
    after the uploading device is deleted.

    Usage Examples:

        $ rio database upload list orders-db
    """
    try:
        client = new_v2_client(with_project=True)
        archives = []
        for page in walk_pages(client.list_database_uploads, database=database):
            archives.extend(page)
        display_archive_list(archives, show_header=True)
    except Exception as e:
        click.secho(str(e), fg=Colors.RED)
        raise SystemExit(1) from e

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
@click.argument("backup-name", type=str)
def inspect_backup(format_type: str, backup_name: str) -> None:
    """Inspect a backup by its name.

    Usage Examples:

        $ rio backup inspect orders-nightly

        $ rio backup inspect orders-nightly --format json
    """
    try:
        client = new_v2_client()
        backup = client.get_backup(backup_name)
        inspect_with_format(
            backup.model_dump(exclude_none=True, by_alias=True), format_type
        )
    except Exception as e:
        click.secho(str(e), fg=Colors.RED)
        raise SystemExit(1) from e

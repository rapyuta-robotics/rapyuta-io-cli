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
from yaspin.api import Yaspin

from riocli.config import get_config_from_context
from riocli.constants import Colors, Symbols
from riocli.usergroup.util import name_to_guid
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
@click.argument("group-name")
@click.pass_context
@with_spinner(text="Deleting user group...")
@name_to_guid
def delete_usergroup(
    ctx: click.Context,
    group_name: str,
    group_guid: str,
    force: bool,
    spinner: Yaspin = None,
) -> None:
    """Delete a usergroup from current organization.

    To skip confirmation, use the ``--force`` or ``-f`` or
    the ``--silent`` flag.
    """
    if not force:
        with spinner.hidden():
            click.confirm(f"Deleting usergroup {group_name} ({group_guid})", abort=True)

    try:
        config = get_config_from_context(ctx)
        client = config.new_v2_client(with_project=False)
        client.delete_user_group(group_guid=group_guid, group_name=group_name)
        spinner.text = click.style("User group deleted successfully.", fg=Colors.GREEN)
        spinner.green.ok(Symbols.SUCCESS)
    except Exception as e:
        spinner.text = click.style(f"Failed to delete usergroup: {e}", Colors.RED)
        spinner.red.fail(Symbols.ERROR)
        raise SystemExit(1) from e

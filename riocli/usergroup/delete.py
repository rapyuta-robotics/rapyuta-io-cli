# Copyright 2024 Rapyuta Robotics
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

from riocli.config import new_client
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
            click.confirm(
                "Deleting usergroup {} ({})".format(group_name, group_guid), abort=True
            )

    try:
        client = new_client()
        org_guid = ctx.obj.data.get("organization_id")
        client.delete_usergroup(org_guid, group_guid)
        spinner.text = click.style("User group deleted successfully.", fg=Colors.GREEN)
        spinner.green.ok(Symbols.SUCCESS)
    except Exception as e:
        spinner.text = click.style("Failed to delete usergroup: {}".format(e), Colors.RED)
        spinner.red.fail(Symbols.ERROR)
        raise SystemExit(1) from e

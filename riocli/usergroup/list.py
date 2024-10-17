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

import typing

import click
from click_help_colors import HelpColorsCommand

from riocli.config import new_client
from riocli.constants import Colors
from riocli.utils import tabulate_data


@click.command(
    "list",
    cls=HelpColorsCommand,
    help_headers_color=Colors.YELLOW,
    help_options_color=Colors.GREEN,
)
@click.pass_context
def list_usergroup(ctx: click.Context) -> None:
    """List all user groups in current organization."""
    try:
        client = new_client()
        org_guid = ctx.obj.data.get("organization_id")
        user_groups = client.list_usergroups(org_guid)
        _display_usergroup_list(user_groups)
    except Exception as e:
        click.secho(str(e), fg=Colors.RED)
        raise SystemExit(1)


def _display_usergroup_list(usergroups: typing.Any, show_header: bool = True):
    headers = []
    if show_header:
        headers = ("ID", "Name", "Creator", "Members", "Projects", "Description")

    data = [
        [
            group.guid,
            group.name,
            group.creator,
            len(group.members) if group.members else 0,
            len(group.projects) if group.projects else 0,
            group.description,
        ]
        for group in usergroups
    ]

    tabulate_data(data, headers)

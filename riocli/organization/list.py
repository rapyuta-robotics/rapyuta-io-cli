# Copyright 2023 Rapyuta Robotics
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

from riocli.config import new_client
from riocli.constants import Colors
from riocli.utils import tabulate_data


@click.command(
    'list',
    cls=HelpColorsCommand,
    help_headers_color=Colors.YELLOW,
    help_options_color=Colors.GREEN,
)
@click.pass_context
def list_organizations(ctx: click.Context) -> None:
    """
    List all the organizations that you are a part of

    Example:

        rio organization list
    """
    try:
        client = new_client(with_project=False)
        organizations = client.get_user_organizations()
        current = ctx.obj.data['organization_id']
        print_organizations(organizations, current)
    except Exception as e:
        click.secho(str(e), fg=Colors.RED)
        raise SystemExit(1) from e


def print_organizations(organizations, current):
    organizations = sorted(organizations, key=lambda o: o.name)

    headers = ["Name", "GUID", "Creator", "Short GUID"]

    data = []
    for org in organizations:
        fg, bold = None, False
        if org.guid == current:
            fg = Colors.GREEN
            bold = True
        data.append([
            click.style(v, fg=fg, bold=bold)
            for v in (org.name, org.guid,
                      org.creator, org.short_guid)
        ])

    tabulate_data(data, headers)

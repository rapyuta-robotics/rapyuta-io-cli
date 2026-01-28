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

from riocli.config import get_config_from_context, new_v2_client
from riocli.constants import Colors, Symbols
from riocli.utils import tabulate_data
from riocli.utils.context import get_root_context


@click.command(
    "users",
    cls=HelpColorsCommand,
    help_headers_color=Colors.YELLOW,
    help_options_color=Colors.GREEN,
)
@click.pass_context
def list_users(ctx: click.Context) -> None:
    """Lists all users in the organization."""
    ctx = get_root_context(ctx)
    config = get_config_from_context(ctx)
    current_user_email = config.data.get("email_id")

    try:
        org_guid = config.organization_guid
        client = new_v2_client(config_inst=config)
        result = client.list_users(organization_guid=org_guid)
        users = result.items or []
    except Exception as e:
        click.secho(
            f"{Symbols.ERROR} Failed to get user details. Error: {e}", fg=Colors.RED
        )
        raise SystemExit(1) from e

    users.sort(key=lambda u: u.spec.email_id)

    data = []
    for u in users:
        fg, bold = None, False
        if u.spec.email_id == current_user_email:
            fg, bold = Colors.GREEN, True
        full_name = f"{u.spec.first_name} {u.spec.last_name}"
        row = [
            u.metadata.guid,
            full_name,
            u.spec.email_id,
            u.spec.organizations[0].role_names,
        ]
        data.append([click.style(v, fg=fg, bold=bold) for v in row])

    tabulate_data(data, headers=["GUID", "Name", "EmailID", "Role"])

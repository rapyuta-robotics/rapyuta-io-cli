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
        organization_guid = config.organization_guid
        client = new_v2_client(config_inst=config)
        organization = client.get_organization(organization_guid)
    except Exception as e:
        click.secho(
            "{} Failed to get organization details".format(Symbols.ERROR), fg=Colors.RED
        )
        raise SystemExit(1) from e

    users = organization.spec.users
    users.sort(key=lambda u: u["emailID"])

    data = []
    for u in users:
        fg, bold = None, False
        if u["emailID"] == current_user_email:
            fg, bold = Colors.GREEN, True
        full_name = "{} {}".format(u.firstName, u.lastName)
        row = [u.guid, full_name, u.emailID, u.roleInOrganization]
        data.append([click.style(v, fg=fg, bold=bold) for v in row])

    tabulate_data(data, headers=["GUID", "Name", "EmailID", "Role"])

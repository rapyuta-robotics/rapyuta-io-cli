# Copyright 2026 Rapyuta Robotics
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

from riocli.config import get_config_from_context
from riocli.constants import Colors
from riocli.exceptions import NoOrganizationSelected
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
    default="json",
    type=click.Choice(["json", "yaml"], case_sensitive=False),
)
@click.pass_context
def inspect_permission(ctx, format_type: str) -> None:
    """Print the permissions of the current user in current organization."""
    try:
        config = get_config_from_context(ctx)
        org_guid = config.data.get("organization_id")
        if not org_guid:
            raise NoOrganizationSelected
        client = config.new_v2_client(with_project=False)

        permissions = client.get_user_permissions(
            user_guid="", organization_guid=org_guid
        )
        inspect_with_format(
            permissions.model_dump(by_alias=True, exclude_none=True), format_type
        )
    except Exception as e:
        click.secho(str(e), fg=Colors.RED)
        raise SystemExit(1)

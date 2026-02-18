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

from riocli.config import get_config_from_context, new_v2_client
from riocli.constants import Colors
from riocli.utils import inspect_with_format


@click.command(
    "inspect",
    cls=HelpColorsCommand,
    help_headers_color=Colors.YELLOW,
    help_options_color=Colors.GREEN,
)
@click.pass_context
def inspect_permission(ctx) -> None:
    """Print the permissions of the current user in current organization."""
    try:
        config = get_config_from_context(ctx)
        org_guid = config.organization_guid
        client = new_v2_client(with_project=False)

        user = client.get_myself()
        user_guid = user.metadata.guid

        permissions = client.get_user_permissions(
            user_guid=user_guid, organization_guid=org_guid
        )
        inspect_with_format(
            permissions.model_dump(by_alias=True, exclude_none=True, mode="json"), "json"
        )
    except Exception as e:
        click.secho(str(e), fg=Colors.RED)
        raise SystemExit(1)

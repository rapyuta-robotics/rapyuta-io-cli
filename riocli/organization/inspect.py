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
import typing

import click
from click_help_colors import HelpColorsCommand
from munch import unmunchify

from riocli.config import get_config_from_context, new_v2_client
from riocli.constants import Colors
from riocli.organization.util import name_to_guid
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
@click.argument("organization-name", type=str)
@name_to_guid
@click.pass_context
def inspect_organization(
    ctx: click.Context,
    format_type: str,
    organization_name: str,
    organization_guid: str,
    organization_short_id: str,
) -> None:
    """Inspect an organization.

    Provides an overview of the organization. The output
    is not the exact ouptut of the API, but a more human-readable
    version of the organization details.
    """
    try:
        config = get_config_from_context(ctx)
        client = new_v2_client(config_inst=config)
        organization = client.get_organization(organization_guid)
        inspect_with_format(unmunchify(organization), format_type)
    except Exception as e:
        click.secho(str(e), fg=Colors.RED)
        raise SystemExit(1) from e


def make_organization_inspectable(organization: typing.Dict) -> typing.Dict:
    creator = None
    for user in organization["users"]:
        if user["guid"] == organization["creator"]:
            creator = user["emailID"]
            break

    return {
        "name": organization["name"],
        "created_at": organization["CreatedAt"],
        "updated_at": organization["UpdatedAt"],
        "guid": organization["guid"],
        "url": organization["url"],
        "creator": creator,
        "short_guid": organization["shortGUID"],
        "state": organization["state"],
        "users": len(organization["users"]),
        "country": organization["country"]["code"],
    }

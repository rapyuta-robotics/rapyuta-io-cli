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
from riocli.constants import Colors, Symbols
from riocli.organization.util import name_to_guid as name_to_organization_guid
from riocli.utils.spinner import with_spinner


@click.command(
    "create",
    cls=HelpColorsCommand,
    help_headers_color=Colors.YELLOW,
    help_options_color=Colors.GREEN,
)
@click.argument("project-name", type=str)
@click.option(
    "--organization",
    "organization_name",
    help="Pass organization name for which project needs to be created. Default will be current organization",
)
@click.pass_context
@name_to_organization_guid
@with_spinner(text="Creating project...")
def create_project(
    ctx: click.Context,
    project_name: str,
    organization_guid: str,
    organization_name: str,
    organization_short_id: str,
    spinner=None,
) -> None:
    """Create a new project.

    If you do not specify the organization, the project will
    be created in the current organization.
    """
    if not organization_guid:
        organization_guid = ctx.obj.data.get("organization_id")

    payload = {
        "metadata": {
            "name": project_name,
            "organizationGUID": organization_guid,
            "labels": {"createdBy": "rio-cli"},
        },
        "spec": {},
    }

    try:
        client = new_v2_client(with_project=False)
        client.create_project(payload)
        spinner.text = click.style("Project created successfully.", fg=Colors.GREEN)
        spinner.green.ok(Symbols.SUCCESS)
    except Exception as e:
        spinner.text = click.style("Failed to create project: {}".format(e), Colors.RED)
        spinner.red.fail(Symbols.ERROR)
        raise SystemExit(1)

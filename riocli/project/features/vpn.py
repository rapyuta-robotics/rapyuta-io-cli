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
from typing import List

import click
from click_help_colors import HelpColorsCommand

from riocli.config import new_v2_client
from riocli.constants import Colors, Symbols
from riocli.project.util import name_to_guid
from riocli.utils.spinner import with_spinner


@click.command(
    "vpn",
    cls=HelpColorsCommand,
    help_headers_color=Colors.YELLOW,
    help_options_color=Colors.GREEN,
)
@click.argument("project-name", type=str)
@click.argument("enable", type=bool)
@click.option(
    "--subnets",
    type=click.STRING,
    multiple=True,
    default=(),
    help="Subnet ranges for the project. For example: 10.81.0.0/16",
)
@name_to_guid
@with_spinner(text="Updating VPN state...")
def vpn(
    project_name: str,
    project_guid: str,
    enable: bool,
    subnets: List[str],
    spinner=None,
) -> None:
    """
    Enable or disable VPN on a project

    Example:

        rio project features vpn "my-project" true

        rio project features vpn "my-project" true --subnets 10.81.0.0/16
    """
    client = new_v2_client(with_project=False)

    try:
        project = client.get_project(project_guid)
    except Exception as e:
        spinner.text = click.style("Failed: {}".format(e), fg=Colors.RED)
        spinner.red.fail(Symbols.ERROR)
        raise SystemExit(1) from e

    project["spec"]["features"]["vpn"] = {"enabled": enable, "subnets": subnets or []}

    is_vpn_enabled = project["spec"]["features"]["vpn"].get("enabled", False)

    status = "Enabling VPN..." if enable else "Disabling VPN..."
    if is_vpn_enabled and subnets:
        status = "Updating the VPN subnet ranges for the project..."

    spinner.text = status

    try:
        client.update_project(project_guid, project)
        spinner.text = click.style("Done", fg=Colors.GREEN)
        spinner.green.ok(Symbols.SUCCESS)
    except Exception as e:
        spinner.text = click.style("Failed: {}".format(e), fg=Colors.RED)
        spinner.red.fail(Symbols.ERROR)
        raise SystemExit(1) from e

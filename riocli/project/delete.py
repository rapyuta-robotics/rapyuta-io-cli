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

from riocli.config import new_v2_client
from riocli.constants import Colors, Symbols
from riocli.project.util import name_to_guid
from riocli.utils.spinner import with_spinner


@click.command(
    "delete",
    cls=HelpColorsCommand,
    help_headers_color=Colors.YELLOW,
    help_options_color=Colors.GREEN,
)
@click.option(
    "--force", "-f", "--silent", "force", is_flag=True, help="Skip confirmation"
)
@click.argument("project-name", type=str)
@name_to_guid
@with_spinner(text="Deleting project...")
def delete_project(
    force: bool,
    project_name: str,
    project_guid: str,
    spinner=None,
) -> None:
    """Delete a project.

    You can skip the confirmation prompt by using the ``--force``
    or ``-f`` or the ``--silent`` flag.
    """
    if not force:
        with spinner.hidden():
            click.confirm(
                "Deleting project {} ({})".format(project_name, project_guid),
                abort=True,
            )

    try:
        client = new_v2_client()
        client.delete_project(project_guid)
        spinner.text = click.style("Project deleted successfully.", fg=Colors.GREEN)
        spinner.green.ok(Symbols.SUCCESS)
    except Exception as e:
        spinner.text = click.style("Failed to delete project: {}".format(e), Colors.RED)
        spinner.red.fail(Symbols.ERROR)
        raise SystemExit(1)

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
from click_help_colors import HelpColorsGroup

from riocli.project.create import create_project
from riocli.project.delete import delete_project
from riocli.project.features import features
from riocli.project.inspect import inspect_project
from riocli.project.list import list_projects
from riocli.project.select import select_project
from riocli.project.update_owner import update_owner
from riocli.project.whoami import whoami


@click.group(
    invoke_without_command=False,
    cls=HelpColorsGroup,
    help_headers_color="yellow",
    help_options_color="green",
)
def project() -> None:
    """
    High-level groups for other resources
    """
    pass


project.add_command(list_projects)
project.add_command(create_project)
project.add_command(delete_project)
project.add_command(select_project)
project.add_command(inspect_project)
project.add_command(features)
project.add_command(whoami)
project.add_command(update_owner)

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
from click_help_colors import HelpColorsGroup

from riocli.organization.list import list_organizations
from riocli.organization.select import select_organization


@click.group(
    invoke_without_command=False,
    cls=HelpColorsGroup,
    help_headers_color='yellow',
    help_options_color='green',
)
def organization() -> None:
    """
    Organizations in rapyuta.io
    """
    pass


organization.add_command(list_organizations)
organization.add_command(select_organization)

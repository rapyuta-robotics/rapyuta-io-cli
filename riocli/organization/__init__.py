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
from click_help_colors import HelpColorsGroup

from riocli.constants import Colors
from riocli.organization.inspect import inspect_organization

from riocli.organization.add_user import invite_user, add_user
from riocli.organization.list import list_organizations
from riocli.organization.remove_user import remove_user
from riocli.organization.select import select_organization
from riocli.organization.users import list_users


@click.group(
    invoke_without_command=False,
    cls=HelpColorsGroup,
    help_headers_color=Colors.YELLOW,
    help_options_color=Colors.GREEN,
)
def organization() -> None:
    """Interact with organizations.

    In rapyuta.io, an organization is the top-level entity that
    contains all the projects and resources. Using the CLI, you
    can view and select organizations, it's users, invite users,
    and remove users.

    Note that in order to invite or remove users, you need to login
    as the organization admin.
    """
    pass


organization.add_command(list_users)
organization.add_command(invite_user)
organization.add_command(add_user)
organization.add_command(remove_user)
organization.add_command(list_organizations)
organization.add_command(select_organization)
organization.add_command(inspect_organization)

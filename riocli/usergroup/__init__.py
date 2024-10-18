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

from riocli.constants import Colors
from riocli.usergroup.delete import delete_usergroup
from riocli.usergroup.inspect import inspect_usergroup
from riocli.usergroup.list import list_usergroup


@click.group(
    invoke_without_command=False,
    cls=HelpColorsGroup,
    help_headers_color=Colors.YELLOW,
    help_options_color=Colors.GREEN,
)
def usergroup() -> None:
    """Manage usergroups in current organization.

    Usergroups are a way to organize users and projects
    in your organization. You can create usergroups and
    add users and projects to them. This helps in managing
    access control and permissions in your organization.

    Users can be part of multiple usergroups and projects
    can be part of multiple usergroups. You can further
    make some users admins of a usergroup and they will
    have the permissions to manage the usergroup.
    """
    pass


usergroup.add_command(list_usergroup)
usergroup.add_command(inspect_usergroup)
usergroup.add_command(delete_usergroup)

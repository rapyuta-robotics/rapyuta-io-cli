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

from riocli.role.bind import bind
from riocli.role.inspect_role import inspect_role
from riocli.role.list import list_role_bindings, list_roles
from riocli.role.unbind import unbind
from riocli.utils.alias import AliasedGroup


@click.group(
    invoke_without_command=False,
    cls=AliasedGroup,
    help_headers_color="yellow",
    help_options_color="green",
)
def role():
    """Manage RBAC roles."""
    pass


role.add_command(list_roles)
role.add_command(list_role_bindings)
role.add_command(inspect_role)
role.add_command(bind)
role.add_command(unbind)

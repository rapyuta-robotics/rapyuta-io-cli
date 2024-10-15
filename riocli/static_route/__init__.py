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
from riocli.static_route.create import create_static_route
from riocli.static_route.delete import delete_static_route
from riocli.static_route.inspect import inspect_static_route
from riocli.static_route.list import list_static_routes
from riocli.static_route.open import open_static_route


@click.group(
    invoke_without_command=False,
    cls=HelpColorsGroup,
    help_headers_color=Colors.YELLOW,
    help_options_color=Colors.GREEN,
)
def static_route() -> None:
    """
    Named routes for the deployments with exposed endpoints
    """
    pass


static_route.add_command(list_static_routes)
static_route.add_command(create_static_route)
static_route.add_command(delete_static_route)
static_route.add_command(inspect_static_route)
static_route.add_command(open_static_route)

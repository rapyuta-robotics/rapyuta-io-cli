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
from typing import List

import click
from click_help_colors import HelpColorsCommand
from rapyuta_io.clients.static_route import StaticRoute

from riocli.config import new_v2_client
from riocli.constants import Colors
from riocli.utils import tabulate_data

@click.command(
    'list',
    cls=HelpColorsCommand,
    help_headers_color=Colors.YELLOW,
    help_options_color=Colors.GREEN,
)
def list_static_routes() -> None:
    """
    List the static routes in the selected project
    """
    try:
        client = new_v2_client(with_project=True)
        routes = client.list_static_routes()
        _display_routes_list(routes)
    except Exception as e:
        click.secho(str(e), fg=Colors.RED)
        raise SystemExit(1) from e

def _display_routes_list(routes: List[StaticRoute]) -> None:
    headers = ['Route ID', 'Name', 'URL', 'Creator', 'CreatedAt']

    data = []
    for route in routes:
        data.append([
            route.metadata.guid,
            route.metadata.name,
            route.spec.url,
            route.metadata.creatorGUID,
            route.metadata.createdAt,
        ])

    tabulate_data(data, headers)

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
import typing
from typing import List

import click
import munch
from click_help_colors import HelpColorsCommand

from riocli.config import new_v2_client
from riocli.constants import Colors
from riocli.utils import tabulate_data


@click.command(
    "list",
    cls=HelpColorsCommand,
    help_headers_color=Colors.YELLOW,
    help_options_color=Colors.GREEN,
)
@click.option(
    "--label",
    "-l",
    "labels",
    multiple=True,
    type=click.STRING,
    default=(),
    help="Filter the deployment list by labels",
)
def list_static_routes(labels: typing.List[str]) -> None:
    """List the static routes in the current project.

    You can filter the list by providing labels using
    the ``--label`` or ``-l`` flag.

    Usage Examples:

        List static routes with label 'app=web'

            $ rio static-route list --label app=web
    """
    try:
        client = new_v2_client(with_project=True)
        routes = client.list_static_routes(query={"labelSelector": labels})
        _display_routes_list(routes)
    except Exception as e:
        click.secho(str(e), fg=Colors.RED)
        raise SystemExit(1) from e


def _display_routes_list(routes: List[munch.Munch]) -> None:
    headers = ["Route ID", "Name", "URL", "Creator", "CreatedAt"]

    data = []
    for route in routes:
        data.append(
            [
                route.metadata.guid,
                route.metadata.name,
                route.spec.url,
                route.metadata.creatorGUID,
                route.metadata.createdAt,
            ]
        )

    tabulate_data(data, headers)

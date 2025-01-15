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
import functools
import typing
from queue import Queue

import click
from click_help_colors import HelpColorsCommand

from riocli.config import new_v2_client
from riocli.constants import Colors, Symbols
from riocli.static_route.util import fetch_static_routes, print_routes_for_confirmation
from riocli.utils import tabulate_data
from riocli.utils.execute import apply_func_with_result
from riocli.utils.spinner import with_spinner
from riocli.v2client.client import Client


@click.command(
    "delete",
    cls=HelpColorsCommand,
    help_headers_color=Colors.YELLOW,
    help_options_color=Colors.GREEN,
)
@click.option(
    "--force", "-f", "--silent", is_flag=True, default=False, help="Skip confirmation"
)
@click.option(
    "-a",
    "--all",
    "delete_all",
    is_flag=True,
    default=False,
    help="Deletes all static routes in the project",
)
@click.option(
    "--workers",
    "-w",
    help="Number of parallel workers while running delete static route "
    "command. Defaults to 10.",
    type=int,
    default=10,
)
@click.argument("route-name-or-regex", type=str, default="")
@with_spinner(text="Deleting static route...")
def delete_static_route(
    route_name_or_regex: str,
    force: bool,
    delete_all: bool = False,
    workers: int = 10,
    spinner=None,
) -> None:
    """Delete one or more static routes with a name or a regex pattern.

    You can specify a static route name or a regex pattern to delete one
    or more deployment.

    If you want to delete all the static routes, then
    simply use the ``--all`` flag.

    If you want to delete static routes without confirmation, then use the
    ``--force`` or ``--silent`` or ``-f``

    Usage Examples:

        Delete a static route by name

            $ rio static-route delete STATIC_ROUTE_NAME

        Delete a static route without confirmation

            $ rio deployment delete STATIC_ROUTE_NAME --force

        Delete all static routes in the project

            $ rio static-route delete --all

        Delete static routes using regex pattern

            $ rio static-route delete "STATIC_ROUTE.*"
    """
    client = new_v2_client()
    if not (route_name_or_regex or delete_all):
        spinner.text = "Nothing to delete"
        spinner.green.ok(Symbols.SUCCESS)
        return

    try:
        routes = fetch_static_routes(client, route_name_or_regex, delete_all)
    except Exception as e:
        spinner.text = click.style(
            "Failed to delete static route(s): {}".format(e), Colors.RED
        )
        spinner.red.fail(Symbols.ERROR)
        raise SystemExit(1) from e

    if not routes:
        spinner.text = "Static route(s) not found"
        spinner.green.ok(Symbols.SUCCESS)
        return

    with spinner.hidden():
        print_routes_for_confirmation(routes)

    spinner.write("")

    if not force:
        with spinner.hidden():
            click.confirm("Do you want to delete the above static route(s)?", abort=True)
        spinner.write("")

    try:
        f = functools.partial(_apply_delete, client)
        result = apply_func_with_result(
            f=f, items=routes, workers=workers, key=lambda x: x[0]
        )

        data, statuses = [], []
        for name, status, msg in result:
            fg = Colors.GREEN if status else Colors.RED
            icon = Symbols.SUCCESS if status else Symbols.ERROR
            statuses.append(status)
            data.append(
                [click.style(name, fg), click.style("{}  {}".format(icon, msg), fg)]
            )

        with spinner.hidden():
            tabulate_data(data, headers=["Name", "Status"])

        # When no route is deleted, raise an exception.
        if not any(statuses):
            spinner.write("")
            spinner.text = click.style("Failed to delete static route(s).", Colors.RED)
            spinner.red.fail(Symbols.ERROR)
            raise SystemExit(1)

        icon = Symbols.SUCCESS if all(statuses) else Symbols.WARNING
        fg = Colors.GREEN if all(statuses) else Colors.YELLOW
        text = "successfully" if all(statuses) else "partially"

        spinner.write("")
        spinner.text = click.style("Static route(s) deleted {}.".format(text), fg)
        spinner.ok(click.style(icon, fg))
    except Exception as e:
        spinner.text = click.style(
            "Failed to delete static route(s): {}".format(e), Colors.RED
        )
        spinner.red.fail(Symbols.ERROR)
        raise SystemExit(1) from e


def _apply_delete(client: Client, result: Queue, route: typing.Any) -> None:
    try:
        client.delete_static_route(name=route.metadata.name)
        result.put((route.metadata.name, True, "Static route deleted successfully"))
    except Exception as e:
        result.put((route.metadata.name, False, str(e)))

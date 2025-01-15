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
from queue import Queue

import click
from click_help_colors import HelpColorsCommand
from yaspin.api import Yaspin

from riocli.config import new_v2_client
from riocli.constants import Colors, Symbols
from riocli.network.model import Network
from riocli.network.util import fetch_networks, print_networks_for_confirmation
from riocli.utils import tabulate_data
from riocli.utils.execute import apply_func_with_result
from riocli.utils.spinner import with_spinner
from riocli.v2client import Client


@click.command(
    "delete",
    cls=HelpColorsCommand,
    help_headers_color=Colors.YELLOW,
    help_options_color=Colors.GREEN,
)
@click.option(
    "--force", "-f", is_flag=True, default=False, help="Skip confirmation", type=bool
)
@click.option(
    "--workers",
    "-w",
    help="Number of parallel workers while running deleting networks. Defaults to 10",
    type=int,
    default=10,
)
@click.argument("network-name-or-regex", type=str)
@with_spinner(text="Deleting network...")
def delete_network(
    force: bool,
    network_name_or_regex: str,
    delete_all: bool = False,
    workers: int = 10,
    spinner: Yaspin = None,
) -> None:
    """Delete one or more networks with a name or a regex pattern.

    You can specify a name or a regex pattern to delete one
    or more networks.

    If you want to delete all the networks, then
    simply use the ``--all`` flag.

    If you want to delete networks without confirmation, then use the
    ``--force`` or ``--silent`` or ``-f``.

    Usage Examples:

        Delete a network by name

            $ rio network delete NETWORK_NAME

        Delete a network without confirmation

            $ rio network delete NETWORK_NAME --force

        Delete all networks in the project

            $ rio network delete --all

        Delete networks using regex pattern

            $ rio network delete "NETWORK.*"
    """
    client = new_v2_client()

    if not (network_name_or_regex or delete_all):
        spinner.text = "Nothing to delete"
        spinner.green.ok(Symbols.SUCCESS)
        return

    try:
        networks = fetch_networks(client, network_name_or_regex, "", delete_all)
    except Exception as e:
        spinner.text = click.style("Failed to find network(s): {}".format(e), Colors.RED)
        spinner.red.fail(Symbols.ERROR)
        raise SystemExit(1) from e

    if not networks:
        spinner.text = "Network(s) not found"
        spinner.green.ok(Symbols.SUCCESS)
        return

    with spinner.hidden():
        print_networks_for_confirmation(networks)

    spinner.write("")

    if not force:
        with spinner.hidden():
            click.confirm(
                "Do you want to delete the above network(s)?", default=True, abort=True
            )

    try:
        f = functools.partial(_apply_delete, client)
        result = apply_func_with_result(
            f=f, items=networks, workers=workers, key=lambda x: x[0]
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

        # When no network is deleted, raise an exception.
        if not any(statuses):
            spinner.write("")
            spinner.text = click.style("Failed to delete network(s).", Colors.RED)
            spinner.red.fail(Symbols.ERROR)
            raise SystemExit(1)

        icon = Symbols.SUCCESS if all(statuses) else Symbols.WARNING
        fg = Colors.GREEN if all(statuses) else Colors.YELLOW
        text = "successfully" if all(statuses) else "partially"

        spinner.text = click.style("Networks(s) deleted {}.".format(text), fg)
        spinner.ok(click.style(icon, fg))
    except Exception as e:
        spinner.text = click.style(
            "Failed to delete network(s): {}".format(e), Colors.RED
        )
        spinner.red.fail(Symbols.ERROR)
        raise SystemExit(1) from e


def _apply_delete(client: Client, result: Queue, network: Network) -> None:
    try:
        client.delete_network(network_name=network.metadata.name)
        result.put((network.metadata.name, True, "Network Deleted Successfully"))
    except Exception as e:
        result.put((network.metadata.name, False, str(e)))

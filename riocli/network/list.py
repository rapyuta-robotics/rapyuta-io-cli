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

import click
from click_help_colors import HelpColorsCommand
from munch import Munch

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
    "--network",
    help="Type of Network",
    type=click.Choice(["routed", "native", "both"]),
    default="both",
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
def list_networks(network: str, labels: typing.List[str]) -> None:
    """List the networks in the current project.

    You can also filter the list by specifying labels using
    the ``--label`` or the ``-l`` flag.

    Usage Examples:

        List all networks with label "app=nginx"

            $ rio network list --label app=nginx
    """
    try:
        client = new_v2_client(with_project=True)

        query = {"labelSelector": labels}
        if network not in ("both", ""):
            query.update({"networkType": network})

        networks = client.list_networks(query=query)
        networks = sorted(networks, key=lambda n: n.metadata.name.lower())
        _display_network_list(networks, show_header=True)
    except Exception as e:
        click.secho(str(e), fg="red")
        raise SystemExit(1)


def _display_network_list(
    networks: typing.List[Munch],
    show_header: bool = True,
) -> None:
    headers = []
    if show_header:
        headers = ("Network ID", "Network Name", "Runtime", "Type", "Phase", "Status")
    data = []
    for network in networks:
        phase = network.status.phase if network.status else ""
        status = network.status.status if network.status else ""
        network_type = network.spec.type

        data.append(
            [
                network.metadata.guid,
                network.metadata.name,
                network.spec.runtime,
                network_type,
                phase,
                status,
            ]
        )

    tabulate_data(data, headers)

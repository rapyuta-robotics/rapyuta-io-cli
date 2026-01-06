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
from click_help_colors import HelpColorsCommand
from rapyuta_io_sdk_v2 import ServiceAccount
from rapyuta_io_sdk_v2.utils import walk_pages

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
def list_service_acc(labels: list[str]) -> None:
    """List service accounts in Organization.

    You can filter the list by providing labels using
    the ``--label`` or ``-l`` flag.

    Usage Examples:

        List service accounts

            $ rio service-account list
    """
    try:
        client = new_v2_client(with_project=False)
        service_accounts = []
        for items in walk_pages(client.list_service_accounts, label_selector=labels):
            service_accounts.extend(items)
        _display_service_accounts_list(service_accounts)
    except Exception as e:
        click.secho(str(e), fg=Colors.RED)
        raise SystemExit(1) from e


def _display_service_accounts_list(accounts: list[ServiceAccount]) -> None:
    headers = ["Name", "ID", "Description"]

    data = []
    for acc in accounts:
        description = acc.spec.description

        if description is not None:
            description = description.replace("\n", " ")
            if len(description) > 48:
                description = description[:48] + ".."

        data.append(
            [
                acc.metadata.name,
                acc.metadata.guid,
                description,
            ]
        )

    tabulate_data(data=data, headers=headers)

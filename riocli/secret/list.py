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
def list_secrets(labels: typing.List[str]) -> None:
    """
    List the secrets in the selected project
    """
    try:
        client = new_v2_client(with_project=True)
        secrets = client.list_secrets(query={"labelSelector": labels})
        secrets = sorted(secrets, key=lambda s: s.metadata.name.lower())
        _display_secret_list(secrets, show_header=True)
    except Exception as e:
        click.secho(str(e), fg=Colors.RED)
        raise SystemExit(1)


def _display_secret_list(
    secrets: typing.List[munch.Munch],
    show_header: bool = True,
) -> None:
    headers = []
    if show_header:
        headers = ("ID", "Name", "Created At", "Creator")

    data = [
        [
            secret.metadata.guid,
            secret.metadata.name,
            secret.metadata.createdAt,
            secret.metadata.creatorGUID,
        ]
        for secret in secrets
    ]

    tabulate_data(data, headers)

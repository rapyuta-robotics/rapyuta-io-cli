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
import typing

import click
from rapyuta_io import Secret

from riocli.config import new_v2_client
from riocli.utils import tabulate_data
from riocli.constants import Colors
from click_help_colors import HelpColorsCommand

@click.command(
    'list',
    cls=HelpColorsCommand,
    help_headers_color=Colors.YELLOW,
    help_options_color=Colors.GREEN,
)
def list_secrets() -> None:
    """
    List the secrets in the selected project
    """
    try:
        client = new_v2_client(with_project=True)
        secrets = client.list_secrets()
        secrets = sorted(secrets, key=lambda s: s.name.lower())
        _display_secret_list(secrets, show_header=True)
    except Exception as e:
        click.secho(str(e), fg=Colors.RED)
        raise SystemExit(1)


def _display_secret_list(
        secrets: typing.List[Secret],
        show_header: bool = True,
) -> None:
    headers = []
    if show_header:
        headers = ('ID', 'Name', 'Created At', 'Creator')

    data = [ [secret.guid, secret.name,
                secret.createdAt, secret.creatorGUID] for secret in secrets ]

    tabulate_data(data, headers)

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

from riocli.config import new_client
from riocli.utils import tabulate_data
from riocli.constants import Colors
from click_help_colors import HelpColorsCommand

@click.command(
    'list',
    cls=HelpColorsCommand,
    help_headers_color=Colors.YELLOW,
    help_options_color=Colors.GREEN,
)
@click.option('--secret-type', '-t', default=['docker', 'source'], multiple=True,
              help='Types to filter the list of Secret [default: docker,source]')
def list_secrets(secret_type: typing.Union[str, typing.Tuple[str]]) -> None:
    """
    List the secrets in the selected project
    """
    try:
        client = new_client()
        secrets = client.list_secrets()
        secrets = sorted(secrets, key=lambda s: s.name.lower())
        _display_secret_list(secrets, secret_type, show_header=True)
    except Exception as e:
        click.secho(str(e), fg=Colors.RED)
        raise SystemExit(1)


def _display_secret_list(
        secrets: typing.List[Secret],
        secret_type: typing.Union[str, typing.Tuple[str]],
        show_header: bool = True,
) -> None:
    headers = []
    if show_header:
        headers = ('Secret ID', 'Secret Name', 'Type', 'Created_At', 'Creator')

    data = []
    for secret in secrets:
        for prefix in secret_type:
            if secret.secret_type.name.lower().find(prefix) != -1:
                data.append([secret.guid, secret.name, secret.secret_type.name.lower(),
                             secret.created_at, secret.creator])

    tabulate_data(data, headers)

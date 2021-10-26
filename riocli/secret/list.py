# Copyright 2021 Rapyuta Robotics
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


@click.command('list')
@click.option('--secret-type', '-t', default=['docker', 'source'], multiple=True,
              help='Types to filter the list of Secret [default: docker,source]')
def list_secrets(secret_type: typing.Union[str, typing.Tuple[str]]) -> None:
    """
    List the secrets in the selected project
    """
    try:
        client = new_client()
        secrets = client.list_secrets()
        _display_secret_list(secrets, secret_type, show_header=True)
    except Exception as e:
        click.secho(str(e), fg='red')
        exit(1)


def _display_secret_list(
        secrets: typing.List[Secret],
        secret_type: typing.Union[str, typing.Tuple[str]],
        show_header: bool = True,
) -> None:
    if show_header:
        click.secho('{:<32} {:<28} {:28} {:28} {:28}'.
                    format('Secret ID', 'Secret Name', 'Type', 'Created_At', 'Creator'),
                    fg='yellow')

    for secret in secrets:
        for prefix in secret_type:
            if secret.secret_type.name.lower().find(prefix) != -1:
                click.secho('{:<32} {:<28} {:28} {:28} {:28}'.
                            format(secret.guid, secret.name, secret.secret_type.name.lower(),
                                   secret.created_at, secret.creator))

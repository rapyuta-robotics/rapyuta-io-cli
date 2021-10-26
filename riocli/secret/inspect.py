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
import click
from rapyuta_io import Secret

from riocli.config import new_client
from riocli.secret.util import name_to_guid
from riocli.utils import inspect_with_format


@click.command('inspect')
@click.option('--format', '-f', 'format_type', default='yaml',
              type=click.Choice(['json', 'yaml'], case_sensitive=False))
@click.argument('secret-name', type=str)
@name_to_guid
def inspect_secret(format_type: str, secret_name: str, secret_guid: str) -> None:
    """
    Inspect the secret resource
    """
    try:
        client = new_client()
        secret = client.get_secret(secret_guid)
        data = make_secret_inspectable(secret)
        inspect_with_format(data, format_type)
    except Exception as e:
        click.secho(str(e), fg='red')
        exit(1)


def make_secret_inspectable(obj: Secret) -> dict:
    return {
        'created_at': obj.created_at,
        'creator': obj.creator,
        'guid': obj.guid,
        'name': obj.name,
        'project': obj.project_guid,
        'secret_type': obj.secret_type.value,
    }

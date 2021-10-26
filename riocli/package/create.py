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
import json

import click
import yaml
from click_spinner import spinner

from riocli.config import new_client


@click.command('create')
@click.option('--manifest', type=click.File(mode='r', lazy=True),
              help='Path for the manifest file')
@click.option('--format', 'format_type', default='json',
              type=click.Choice(['json', 'yaml'], case_sensitive=False))
def create_package(manifest: click.File, format_type: str) -> None:
    """
    Create a new package
    """
    data = manifest.read()
    if format_type == 'json':
        package = json.loads(data)
    else:
        package = yaml.load(data)

    try:
        client = new_client()
        with spinner():
            client.create_package(package)
        click.secho('Package created successfully!', fg='green')
    except Exception as e:
        click.secho(str(e), fg='red')
        exit(1)

# Copyright 2022 Rapyuta Robotics
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
import typing

import click
import yaml
from click_help_colors import HelpColorsCommand
from rapyuta_io import Client

from riocli.build.model import Build
from riocli.config import Configuration
from riocli.device.model import Device
from riocli.network.model import Network
from riocli.project.model import Project
from riocli.secret.model import Secret

KIND_TO_CLASS = {
    'Project': Project,
    'Secret': Secret,
    'Build': Build,
    'Device': Device,
    'Network': Network,
}


@click.command(
    'apply',
    hidden=True,
    cls=HelpColorsCommand,
    help_headers_color='yellow',
    help_options_color='green',
)
@click.argument('files', nargs=-1)
def apply(files: typing.List[str]) -> None:
    """
    Apply resource manifests
    """
    if len(files) == 0:
        click.secho('no files specified', fg='red')
        exit(1)

    try:
        # Don't use the Context Client, Project can change
        config = Configuration()
        project = config.data.get('project_id', None)
        client = config.new_client(with_project=False)

        for f in files:
            client.set_project(project)

            # Let the apply_file overwrite Project
            apply_file(client, f)
    except Exception as e:
        click.secho(str(e), fg='red')
        exit(1)


def apply_file(client: Client, filepath: str) -> None:
    with open(filepath) as f:
        data = f.read()

    if filepath.endswith("json"):
        data = json.loads(data)
    elif filepath.endswith('yaml') or filepath.endswith('yml'):
        data = yaml.safe_load(data)

    if not data:
        raise Exception('{} file is empty'.format(filepath))

    cls = get_model(data)
    ist = cls.from_dict(client, data)
    ist.apply(client)


def get_model(data: dict) -> typing.Any:
    kind = data.get('kind', None)
    if not kind:
        raise Exception('kind is missing')

    cls = KIND_TO_CLASS.get(kind, None)
    if not cls:
        raise Exception('invalid kind {}'.format(kind))

    return cls

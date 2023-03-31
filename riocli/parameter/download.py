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
from tempfile import mkdtemp
from xmlrpc.client import Boolean

import click
from click_spinner import spinner

from riocli.config import new_client
from riocli.parameter.utils import display_trees


# -----------------------------------------------------------------------------
#
# Configurations
# Args
#    path,  tree_names,  delete_existing=True|False
# -----------------------------------------------------------------------------


@click.command('download')
@click.option('--tree-names', type=click.STRING, multiple=True, default=None, help='Tree names to fetch')
@click.option('--overwrite', '--delete-existing', 'delete_existing', is_flag=True,
              help='Overwrite existing parameter tree')
@click.argument('path', type=click.Path(exists=True), required=False)
def download_configurations(path: str, tree_names: typing.Tuple[str] = None, delete_existing: Boolean = False) -> None:
    """
    Download the Configuration Parameter trees.
    """
    if path is None:
        # Not using the Context Manager because we need to persist the Temporary directory.
        path = mkdtemp()

    click.secho('Downloading at {}'.format(path))

    try:
        client = new_client()

        with spinner():
            client.download_configurations(path, tree_names=list(tree_names),
                                           delete_existing_trees=delete_existing)

        click.secho('✅ Configuration Parameters downloaded successfully', fg='green')
    except Exception as e:
        click.secho(e, fg='red')
        raise SystemExit(1)

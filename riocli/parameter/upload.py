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
from click_spinner import spinner

from riocli.config import new_client
from riocli.parameter.utils import filter_trees, display_trees


@click.command('upload')
@click.option('--tree-names', type=click.STRING, multiple=True, default=[], help='Directory names to upload')
@click.option('--recreate', '--delete-existing', 'delete_existing', is_flag=True,
              help='Overwrite existing parameter tree')
@click.option('-f', '--force', '--silent', 'silent', is_flag=True, default=False, help="Skip confirmation")
@click.argument('path', type=click.Path(exists=True))
def upload_configurations(path: str, tree_names: typing.Tuple[str] = None, delete_existing: bool = False,
                          silent: bool = False) -> None:
    """
    Upload a set of Configuration Parameter directory trees.
    """
    trees = filter_trees(path, tree_names)

    click.secho('Following Trees will be uploaded')
    click.secho('')
    display_trees(path, trees)

    if not silent:
        click.confirm('Do you want to proceed?', default=True, abort=True)

    try:
        client = new_client()
        with spinner():
            client.upload_configurations(rootdir=path, tree_names=trees, delete_existing_trees=delete_existing,
                                         as_folder=True)

        click.secho('✅ Configuration parameters uploaded successfully', fg='green')
    except Exception as e:
        click.secho(str(e), fg='red')
        raise SystemExit(1)

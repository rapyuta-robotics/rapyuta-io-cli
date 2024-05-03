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
import os
from typing import Optional, Iterable
from pathlib import Path

import click
from click_help_colors import HelpColorsCommand
from benedict import benedict
from yaspin.core import Yaspin

from riocli.config import new_v2_client
from riocli.configtree.etcd import import_in_etcd
from riocli.configtree.revision import Revision
from riocli.constants import Symbols, Colors
from riocli.utils.spinner import with_spinner


@click.command(
    'import',
    cls=HelpColorsCommand,
    help_headers_color=Colors.YELLOW,
    help_options_color=Colors.GREEN,
)
@click.option('--commit/--no-commit', 'commit', is_flag=True, type=bool,)
@click.option('--update-head/--no-update-head', 'update_head', is_flag=True, type=bool)
@click.option('--etcd-endpoint', 'etcd_endpoint', type=str,
              help='Import keys to local etcd instead of rapyuta.io cloud')
@click.option('--export-directory', 'export_directory', type=str,
              help='Path to the directory for exporting files.')
@click.option('--etcd-port', 'etcd_port', type=int,
              help='Port for the etcd endpoint')
@click.option('--etcd-prefix', 'etcd_prefix', type=str,
              help='Prefix to use for the key-space')
@click.option('--project', 'with_project', is_flag=True, type=bool,
              help='Operate on the Config trees in Project-scope.')
@click.argument('tree-name', type=str)
@click.argument('files', type=str, nargs=-1)
@click.pass_context
@with_spinner(text="Importing keys...")
def import_keys(
        _: click.Context,
        tree_name: str,
        files: Iterable[str],
        commit: bool,
        update_head: bool,
        export_directory: Optional[str],
        etcd_endpoint: Optional[str],
        etcd_port: Optional[int],
        etcd_prefix: Optional[str],
        with_project: bool,
        spinner: Yaspin,
) -> None:
    """
    Imports keys in a Config tree from YAML files.
    """

    data = {}

    for f in files:
        file_prefix = Path(f).stem
        file_format = 'yaml'
        if f.endswith('json'):
            file_format = 'json'

        data[file_prefix] = benedict(f, format=file_format)
        spinner.write(
            click.style(
                '{} File {} processed.'.format(Symbols.SUCCESS, f),
                fg=Colors.CYAN,
            )
        )

    data, description = split_description(data)

    if export_directory is not None:
        export_to_files(base_dir=export_directory, data=data)

    data, description = benedict(data).flatten(separator='/'), \
        benedict(description).flatten(separator='/')


    if etcd_endpoint:
        import_in_etcd(data=data, endpoint=etcd_endpoint, port=etcd_port, prefix=etcd_prefix)
        return

    try:
        client = new_v2_client(with_project=with_project)
        with Revision(tree_name=tree_name, commit=commit, client=client, spinner=spinner) as rev:
            rev_id = rev.revision_id

            for key, value in data.items():
                desc = descriptions.get(key)
                rev.store(key=key, value=str(value), perms=644, description=desc)
                spinner.write(
                    click.style(
                        '\t{} Key {} added.'.format(Symbols.SUCCESS, key),
                        fg=Colors.CYAN,
                    )
                )

        if update_head:
            payload = {
                'kind': 'ConfigTree',
                'apiVersion': 'api.rapyuta.io/v2',
                'metadata': {
                    'name': tree_name,
                },
                'head': {
                    'metadata': {
                        'guid': rev_id,
                    }
                },
            }

            client.set_revision_config_tree(tree_name, payload)
            spinner.text = click.style('Config tree Head updated successfully.', fg=Colors.CYAN)
            spinner.green.ok(Symbols.SUCCESS)

    except Exception as e:
        spinner.red.text = str(e)
        spinner.red.fail(Symbols.ERROR)
        raise SystemExit(1) from e


def split_description(input: Iterable) -> (Iterable, Iterable):
    if not isinstance(input, dict):
        return input, None

    data, comments = {}, {}

    for key, value in input.items():
        if not isinstance(value, dict):
            data[key] = value
            continue

        if len(value) == 2 and value.get('value') and value.get('description'):
            data[key] = value.get('value')
            comments[key] = value.get('description')
            continue

        data[key], comments[key] = split_description(value)

def export_to_files(base_dir: str, data: dict) -> None:
    base_dir = os.path.abspath(base_dir)

    for file_name, file_data in data.items():
        file_path = os.path.join(base_dir, '{}.yaml'.format(file_name))
        benedict(file_data).to_yaml(filepath=file_path)

    return data, comments

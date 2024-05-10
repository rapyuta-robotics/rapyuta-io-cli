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
from pathlib import Path
from typing import Optional, Iterable

import click
from benedict import benedict
from click_help_colors import HelpColorsCommand
from yaspin.core import Yaspin

from riocli.config import new_v2_client
from riocli.configtree.etcd import import_in_etcd
from riocli.configtree.revision import Revision
from riocli.configtree.util import Metadata
from riocli.constants import Symbols, Colors
from riocli.utils.spinner import with_spinner


@click.command(
    'import',
    cls=HelpColorsCommand,
    help_headers_color=Colors.YELLOW,
    help_options_color=Colors.GREEN,
)
@click.option('--commit/--no-commit', 'commit', is_flag=True, type=bool, )
@click.option('--update-head/--no-update-head', 'update_head', is_flag=True, type=bool)
@click.option('--etcd-endpoint', 'etcd_endpoint', type=str,
              help='Import keys to local etcd instead of rapyuta.io cloud')
@click.option('--export-directory', 'export_directory', type=str,
              help='Path to the directory for exporting files.')
@click.option('--etcd-port', 'etcd_port', type=int,
              help='Port for the etcd endpoint')
@click.option('--etcd-prefix', 'etcd_prefix', type=str,
              help='Prefix to use for the key-space')
@click.option('--organization', 'with_org', is_flag=True, type=bool,
              default=False, help='Operate on organization-scoped Config Trees only.')
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
        with_org: bool,
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

    data, metadata = split_metadata(data)

    if export_directory is not None:
        export_to_files(base_dir=export_directory, data=data)

    data = benedict(data).flatten(separator='/')
    metadata = benedict(metadata).flatten(separator='/')

    if etcd_endpoint:
        import_in_etcd(data=data, endpoint=etcd_endpoint, port=etcd_port, prefix=etcd_prefix)
        return

    try:
        client = new_v2_client(with_project=(not with_org))
        with Revision(tree_name=tree_name, commit=commit, client=client, spinner=spinner) as rev:
            rev_id = rev.revision_id

            for key, value in data.items():
                key_metadata = metadata.get(key, None)
                if key_metadata is not None and isinstance(key_metadata, Metadata):
                    key_metadata = key_metadata.get_dict()

                rev.store(key=key, value=str(value), perms=644, metadata=key_metadata)
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


def split_metadata(input: Iterable) -> (Iterable, Iterable):
    if not isinstance(input, dict):
        return input, None

    content, metadata = {}, {}

    for key, value in input.items():
        if not isinstance(value, dict):
            content[key] = value
            continue

        potential_content = value.get('value')
        potential_meta = value.get('metadata')

        if len(value) == 2 and potential_content is not None and \
                potential_meta is not None and isinstance(potential_meta, dict):
            content[key] = potential_content
            metadata[key] = Metadata(potential_meta)
            continue

        content[key], metadata[key] = split_metadata(value)

    return content, metadata


def export_to_files(base_dir: str, data: dict) -> None:
    base_dir = os.path.abspath(base_dir)

    for file_name, file_data in data.items():
        file_path = os.path.join(base_dir, '{}.yaml'.format(file_name))
        benedict(file_data).to_yaml(filepath=file_path)

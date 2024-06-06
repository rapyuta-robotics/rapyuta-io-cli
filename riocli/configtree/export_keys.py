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
from base64 import b64decode
from typing import Optional

import click
from benedict import benedict
from click_help_colors import HelpColorsCommand
from yaspin.core import Yaspin

from riocli.config import new_v2_client
from riocli.configtree.util import export_to_files
from riocli.constants import Symbols, Colors
from riocli.utils.spinner import with_spinner


@click.command(
    'export',
    cls=HelpColorsCommand,
    help_headers_color=Colors.YELLOW,
    help_options_color=Colors.GREEN,
)
@click.option('--organization', 'with_org', is_flag=True, type=bool,
              default=False, help='Operate on organization-scoped Config Trees only.')
@click.option('--export-directory', 'export_directory', type=str,
              help='Path to the directory for exporting files.')
@click.argument('tree-name', type=str)
@click.argument('rev-id', type=str, required=False)
@click.pass_context
@with_spinner(text="Exporting keys...")
def export_keys(
        _: click.Context,
        tree_name: str,
        rev_id: Optional[str],
        with_org: bool,
        export_directory: Optional[str],
        spinner: Yaspin,
) -> None:
    """
    Export keys of the Config tree to files.
    """

    if export_directory is None:
        export_directory = '.'

    try:
        client = new_v2_client(with_project=(not with_org))
        tree = client.get_config_tree(tree_name=tree_name, rev_id=rev_id, include_data=True)
        if not tree.get('head'):
            raise Exception('Config tree does not have keys in the revision')

        keys = tree.get('keys')
        if not isinstance(keys, dict):
            raise Exception('Keys are not dictionary')

        data = combine_metadata(keys)
        data = benedict(data).unflatten(separator='/')

        export_to_files(base_dir=export_directory, data=data)

    except Exception as e:
        spinner.red.text = str(e)
        spinner.red.fail(Symbols.ERROR)
        raise SystemExit(1) from e


def combine_metadata(keys: dict) -> dict:
    result = {}

    for key, val in keys.items():
        data = val.get('data', None)
        data = b64decode(data).decode('utf-8')
        metadata = val.get('metadata', None)

        if metadata:
            result[key] = {'value': data, 'metadata': metadata,}
        else:
            result[key] = data

    return result


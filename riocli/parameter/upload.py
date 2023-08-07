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

import sys
import typing

import click
from click_help_colors import HelpColorsCommand

if sys.stdout.isatty():
    from yaspin import kbi_safe_yaspin as Spinner
else:
    from riocli.utils.spinner import DummySpinner as Spinner
from riocli.config import new_client
from riocli.constants import Colors, Symbols
from riocli.parameter.utils import filter_trees, display_trees


@click.command(
    'upload',
    cls=HelpColorsCommand,
    help_headers_color=Colors.YELLOW,
    help_options_color=Colors.GREEN,
)
@click.option('--tree-names', type=click.STRING, multiple=True, default=[],
              help='Directory names to upload')
@click.option('--recreate', '--delete-existing', 'delete_existing',
              is_flag=True,
              help='Overwrite existing parameter tree')
@click.option('-f', '--force', '--silent', 'silent', is_flag=True,
              default=False, help="Skip confirmation")
@click.argument('path', type=click.Path(exists=True))
def upload_configurations(
        path: str,
        tree_names: typing.Tuple[str] = None,
        delete_existing: bool = False,
        silent: bool = False
) -> None:
    """
    Upload a directories as configuration parameters.
    """
    trees = filter_trees(path, tree_names)

    click.secho('Following configuration trees will be uploaded')
    click.secho()
    display_trees(path, trees)

    if not silent:
        click.confirm('Do you want to proceed?', default=True, abort=True)

    client = new_client()

    with Spinner(text="Uploading configurations...", timer=True) as spinner:
        try:
            client.upload_configurations(
                rootdir=path,
                tree_names=trees,
                delete_existing_trees=delete_existing,
                as_folder=True
            )

            spinner.text = click.style(
                'Configuration parameters uploaded successfully',
                fg=Colors.GREEN)
            spinner.green.ok(Symbols.SUCCESS)
        except Exception as e:
            spinner.text = click.style(e, fg=Colors.RED)
            spinner.red.fail(Symbols.ERROR)
            raise SystemExit(1)

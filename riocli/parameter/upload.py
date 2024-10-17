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
    "upload",
    cls=HelpColorsCommand,
    help_headers_color=Colors.YELLOW,
    help_options_color=Colors.GREEN,
)
@click.option(
    "--tree-names",
    type=click.STRING,
    multiple=True,
    default=[],
    help="Directory names to upload",
)
@click.option(
    "--recreate",
    "--delete-existing",
    "delete_existing",
    is_flag=True,
    help="Overwrite existing parameter tree",
)
@click.option(
    "-f",
    "--force",
    "--silent",
    "silent",
    is_flag=True,
    default=False,
    help="Skip confirmation",
)
@click.argument("path", type=click.Path(exists=True))
def upload_configurations(
    path: str,
    tree_names: typing.Tuple[str] = None,
    delete_existing: bool = False,
    silent: bool = False,
) -> None:
    """Upload directories as configuration parameter trees.

    You can upload one or more directories as configuration
    parameter trees on rapyuta.io. If you do not wish to
    upload all the directories as a tree you can specify
    the directory names using the ``--tree-names`` flag.
    Directories that match the tree names will be parsed and
    uploaded.

    You can also specify the ``--recreate`` or ``--delete-existing``
    flag to overwrite the existing parameter tree on rapyuta.io.

    You can skip the confirmation prompt by using the ``--force`` or
    ``--silent`` or the ``-f`` flag.

    Usage Examples:

        Upload all directories as configuration parameter trees

            $ rio parameter upload .

        Upload only the directories "config" and "secrets"

            $ rio parameter upload . --tree-names config --tree-names secrets

        Recreate the existing parameter tree

            $ rio parameter upload . --recreate
    """
    try:
        trees = filter_trees(path, tree_names)
    except Exception as e:
        click.secho("{} {}".format(Symbols.ERROR, e), fg=Colors.RED)
        raise SystemExit(1)

    if not trees:
        click.secho(
            "{} No configuration trees to upload.".format(Symbols.INFO),
            fg=Colors.BRIGHT_CYAN,
        )
        return

    click.secho("Following configuration trees will be uploaded")
    click.secho()
    display_trees(path, trees)

    if not silent:
        click.confirm("Do you want to proceed?", default=True, abort=True)

    client = new_client()

    with Spinner(text="Uploading configurations...", timer=True) as spinner:
        try:
            client.upload_configurations(
                rootdir=path,
                tree_names=trees,
                delete_existing_trees=delete_existing,
                as_folder=True,
            )

            spinner.text = click.style(
                "Configuration parameters uploaded successfully", fg=Colors.GREEN
            )
            spinner.green.ok(Symbols.SUCCESS)
        except Exception as e:
            spinner.text = click.style(e, fg=Colors.RED)
            spinner.red.fail(Symbols.ERROR)
            raise SystemExit(1)

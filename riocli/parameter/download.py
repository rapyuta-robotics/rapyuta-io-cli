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
import typing
from os.path import abspath
from tempfile import mkdtemp

import click
from click_help_colors import HelpColorsCommand

from riocli.config import new_client
from riocli.constants import Colors, Symbols
from riocli.utils.spinner import with_spinner


# -----------------------------------------------------------------------------
#
# Configurations
# Args
#    path,  tree_names,  delete_existing=True|False
# -----------------------------------------------------------------------------


@click.command(
    "download",
    cls=HelpColorsCommand,
    help_headers_color=Colors.YELLOW,
    help_options_color=Colors.GREEN,
)
@click.option(
    "--tree-names",
    type=click.STRING,
    multiple=True,
    default=None,
    help="Tree names to fetch",
)
@click.option(
    "--overwrite",
    "--delete-existing",
    "delete_existing",
    is_flag=True,
    help="Overwrite existing parameter tree",
)
@click.argument("path", type=click.Path(exists=True), required=False)
@with_spinner(text="Download configurations...", timer=True)
def download_configurations(
    path: str,
    tree_names: typing.Tuple[str] = None,
    delete_existing: bool = False,
    spinner=None,
) -> None:
    """Download configuration parameter trees from rapyuta.io.

    You can specify the tree names to download using the ``--tree-names`` flag.

    If you do not specify any tree names, all the trees will be downloaded.

    You can also specify the ``--overwrite`` or ``--delete-existing`` flag to
    overwrite the existing parameter tree on the local machine.
    """
    if path is None:
        # Not using the Context Manager because
        # we need to persist the temporary directory.
        path = mkdtemp()

    if not tree_names:
        msg = click.style(
            "{} No tree names specified. Downloading all the trees...".format(
                Symbols.INFO
            ),
            fg=Colors.BRIGHT_CYAN,
        )
        spinner.write(msg)

    spinner.write("Downloading at {}".format(abspath(path)))

    try:
        client = new_client()

        client.download_configurations(
            path, tree_names=list(tree_names), delete_existing_trees=delete_existing
        )

        spinner.text = click.style(
            "Configurations downloaded successfully.", fg=Colors.GREEN
        )
        spinner.green.ok(Symbols.SUCCESS)
    except Exception as e:
        spinner.text = click.style(e, fg=Colors.RED)
        spinner.red.fail(Symbols.ERROR)
        raise SystemExit(1)

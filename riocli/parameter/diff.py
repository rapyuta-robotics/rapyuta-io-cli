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
# -----------------------------------------------------------------------------
#
# Configurations
# Args
#    path,  tree_names,  delete_existing=True|False
# -----------------------------------------------------------------------------
import os.path
from difflib import unified_diff
from filecmp import dircmp
from tempfile import TemporaryDirectory
from typing import Tuple

import click
from click_help_colors import HelpColorsCommand
from rapyuta_io.utils.error import APIError, InternalServerError

from riocli.config import new_client
from riocli.constants import Colors
from riocli.parameter.utils import filter_trees


@click.command(
    "diff",
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
@click.argument("path", type=click.Path(exists=True), required=False)
def diff_configurations(path: str, tree_names: Tuple = None) -> None:
    """Diff between the local and cloud configuration trees.

    You can specify the tree names to diff using the ``--tree-names`` flag.
    """
    trees = filter_trees(path, tree_names)

    try:
        client = new_client()
        with TemporaryDirectory(prefix="riocli-") as tmp_path:
            client.download_configurations(tmp_path, tree_names=list(tree_names))

            for tree in trees:
                left_tree = os.path.join(tmp_path, tree)
                right_tree = os.path.join(path, tree)
                diff_tree(left_tree, right_tree)
    except (APIError, InternalServerError) as e:
        click.secho(str(e), fg=Colors.RED)
        raise SystemExit(1)


def diff_tree(left: str, right: str) -> None:
    comp = dircmp(left, right)

    for f in comp.common_dirs:
        remote_dir, local_dir = os.path.join(comp.left, f), os.path.join(comp.right, f)
        diff_tree(remote_dir, local_dir)

    for f in comp.diff_files:
        remote_file, local_file = (
            os.path.join(comp.left, f),
            os.path.join(comp.right, f),
        )
        diff_file(remote_file, local_file)

    for f in comp.right_only:
        remote_file, local_file = (
            os.path.join(comp.left, f),
            os.path.join(comp.right, f),
        )
        changed_file(remote_file, local_file, right_only=True)

    for f in comp.left_only:
        remote_file, local_file = (
            os.path.join(comp.left, f),
            os.path.join(comp.right, f),
        )
        changed_file(remote_file, local_file, left_only=True)


def diff_file(left: str, right: str):
    try:
        with open(left, "r", encoding="utf-8") as left_f:
            left_lines = left_f.readlines()

        with open(right, "r", encoding="utf-8") as right_f:
            right_lines = right_f.readlines()
    except UnicodeDecodeError:
        changed_file(left, right, binary=True)
        return

    diff = unified_diff(
        left_lines, right_lines, fromfile=left, tofile=right, lineterm="\n"
    )

    for line in diff:
        click.secho(line, nl=False)


def changed_file(
    left: str,
    right: str,
    left_only: bool = False,
    right_only: bool = False,
    binary: bool = False,
):
    click.secho("--- {}".format(left))
    click.secho("+++ {}".format(right))

    if left_only:
        click.secho("deleted file")
        click.secho()
    elif right_only:
        click.secho("new file")
        click.secho()
    elif binary:
        click.secho("binary file changed")
        click.secho()

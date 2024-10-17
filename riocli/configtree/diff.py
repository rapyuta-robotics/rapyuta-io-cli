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
from tempfile import NamedTemporaryFile

import click
from click_help_colors import HelpColorsCommand

from riocli.config import get_config_from_context
from riocli.configtree.util import fetch_ref_keys, unflatten_keys
from riocli.constants.colors import Colors


@click.command(
    "diff",
    cls=HelpColorsCommand,
    help_headers_color=Colors.YELLOW,
    help_options_color=Colors.GREEN,
)
@click.argument("ref_1", type=str)
@click.argument("ref_2", type=str)
@click.pass_context
def diff_revisions(ctx: click.Context, ref_1: str, ref_2: str):
    """
    Diff between two revisions of the same or different trees.

    The ref is a slash ('/') separated string.

    * The first part can be 'org' or 'proj' defining the scope of the reference.

    * The second part defines the name of the Tree.

    * The third optional part defines the revision-id or milestone of the Tree.

    Examples:

    * org/tree-name

    * org/tree-name/rev-id

    * org/tree-name/milestone

    * proj/tree-name

    * proj/tree-name/rev-id

    * proj/tree-name/milestone
    """
    try:
        ref_1_keys = fetch_ref_keys(ref_1)
        ref_2_keys = fetch_ref_keys(ref_2)

        display_diff(ctx, ref_1_keys, ref_2_keys)
    except Exception as e:
        click.secho(str(e), fg=Colors.RED)
        raise SystemExit(1) from e


def display_diff(ctx: click.Context, keys_1: dict, keys_2: dict) -> None:
    cfg = get_config_from_context(ctx)
    keys_1 = unflatten_keys(keys_1)
    keys_2 = unflatten_keys(keys_2)

    with NamedTemporaryFile(mode="w+b") as file_1, NamedTemporaryFile(
        mode="w+b"
    ) as file_2:
        keys_1.to_json(filepath=file_1.name, indent=4)
        keys_2.to_json(filepath=file_2.name, indent=4)
        os.system("{} {} {}".format(cfg.diff_tool, file_1.name, file_2.name))

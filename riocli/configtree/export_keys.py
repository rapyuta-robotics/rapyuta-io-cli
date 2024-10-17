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
from pathlib import Path
from typing import Optional

import click
from click_help_colors import HelpColorsCommand
from yaspin.core import Yaspin

from riocli.config import new_v2_client
from riocli.configtree.util import export_to_files, unflatten_keys
from riocli.constants import Symbols, Colors
from riocli.utils.spinner import with_spinner


@click.command(
    "export",
    cls=HelpColorsCommand,
    help_headers_color=Colors.YELLOW,
    help_options_color=Colors.GREEN,
)
@click.option(
    "--organization",
    "with_org",
    is_flag=True,
    type=bool,
    default=False,
    help="Operate on organization-scoped Config Trees only.",
)
@click.option(
    "--export-directory",
    "export_directory",
    type=str,
    help="Path to the directory for exporting files.",
)
@click.option(
    "--format",
    "-f",
    "file_format",
    type=click.Choice(["json", "yaml"]),
    default="json",
    help="Format of the exported files.",
)
@click.argument("tree-name", type=str)
@click.argument("rev-id", type=str, required=False)
@click.pass_context
@with_spinner(text="Exporting keys...")
def export_keys(
    _: click.Context,
    tree_name: str,
    rev_id: Optional[str],
    with_org: bool,
    export_directory: Optional[str],
    file_format: Optional[str],
    spinner: Yaspin,
) -> None:
    """Export keys of the Config tree to files."""
    if export_directory is None:
        export_directory = "."

    export_directory = Path(export_directory).absolute()

    try:
        client = new_v2_client(with_project=(not with_org))
        tree = client.get_config_tree(
            tree_name=tree_name, rev_id=rev_id, include_data=True
        )
        if not tree.get("head"):
            raise Exception("Config tree does not have keys in the revision")

        keys = tree.get("keys")
        if not isinstance(keys, dict):
            raise Exception("Keys are not a dictionary")

        data = unflatten_keys(keys)

        export_to_files(base_dir=export_directory, data=data, file_format=file_format)

        spinner.text = click.style(
            f"Keys exported to {export_directory}", fg=Colors.GREEN
        )
        spinner.ok(Symbols.SUCCESS)
    except Exception as e:
        spinner.text = click.style(f"Failed to export keys: {e}", fg=Colors.RED)
        spinner.red.fail(Symbols.ERROR)
        raise SystemExit(1) from e

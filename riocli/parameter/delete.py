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

import click
from click_help_colors import HelpColorsCommand
from rapyuta_io.utils.rest_client import HttpMethod

if sys.stdout.isatty():
    from yaspin import kbi_safe_yaspin as Spinner
else:
    from riocli.utils.spinner import DummySpinner as Spinner

from riocli.constants import Colors, Symbols
from riocli.parameter.utils import _api_call


@click.command(
    "delete",
    cls=HelpColorsCommand,
    help_headers_color=Colors.YELLOW,
    help_options_color=Colors.GREEN,
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
@click.argument("tree", type=click.STRING)
def delete_configurations(tree: str, silent: bool = False) -> None:
    """Delete a configuration parameter tree.

    You can skip the confirmation prompt by using the ``--force`` or
    ``--silent`` or ``-f`` flag.
    """
    click.secho("Configuration Parameter {} will be deleted".format(tree))

    if not silent:
        click.confirm("Do you want to proceed?", default=True, abort=True)

    with Spinner(text="Deleting...", timer=True) as spinner:
        try:
            data = _api_call(HttpMethod.DELETE, name=tree)
            if data.get("data") != "ok":
                raise Exception("Failed to delete configuration")

            spinner.text = click.style(
                "Configuration deleted successfully.", fg=Colors.GREEN
            )
            spinner.green.ok(Symbols.SUCCESS)
        except IOError as e:
            spinner.text = click.style(e, fg=Colors.RED)
            spinner.red.fail(Symbols.ERROR)
            raise SystemExit(1)

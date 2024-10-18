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

import click
from click_help_colors import HelpColorsCommand

from riocli.constants import Colors, Symbols
from riocli.utils import tabulate_data


@click.command(
    "list-examples",
    cls=HelpColorsCommand,
    help_headers_color=Colors.YELLOW,
    help_options_color=Colors.GREEN,
    help="List all examples supported in rio explain command",
)
def list_examples() -> None:
    """List all examples supported in rio explain command."""
    path = Path(__file__).parent.joinpath("manifests")

    examples = []
    for each in path.glob("*.yaml"):
        examples.append([each.name.split(".yaml")[0]])

    tabulate_data(examples, ["Examples"])


@click.command(
    "explain",
    cls=HelpColorsCommand,
    help_headers_color=Colors.YELLOW,
    help_options_color=Colors.GREEN,
    help="Generates a sample resource manifest for the given type",
)
@click.option("--templates", help="Alternate root for templates", default=None)
@click.argument("resource")
def explain(resource: str, templates: str = None) -> None:
    """Explain a resource manifest for the given type.

    The explain command can be used to generate a sample
    resource manifest using the examples that are shown
    in the output. This is particularly useful to understand
    the structure of the manifest and the fields that are
    required for the resource.

    Usage Examples:

        View examples for deployment

        $ rio explain deployment

        View examples for usergroup

        $ rio explain usergroup
    """
    if templates:
        path = Path(templates)
    else:
        path = Path(__file__).parent.joinpath("manifests")

    for each in path.glob("**/*"):
        if resource + ".yaml" == each.name:
            with open(each) as f:
                click.echo_via_pager(f.readlines())
                raise SystemExit(0)

    click.secho(
        '{} Resource "{}" not found'.format(Symbols.ERROR, resource), fg=Colors.RED
    )
    raise SystemExit(1)

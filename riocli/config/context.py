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
import json
from pathlib import Path
from typing import Optional

import click
import yaml
from click_help_colors import HelpColorsGroup, HelpColorsCommand

from riocli.config import Configuration
from riocli.constants import Symbols, Colors
from riocli.utils import inspect_with_format


@click.group(
    name="context",
    invoke_without_command=False,
    cls=HelpColorsGroup,
    help_headers_color=Colors.YELLOW,
    help_options_color=Colors.GREEN,
)
def cli_context() -> None:
    """Manage the CLI's context.

    The CLI maintains a context that is used to store the configuration that
    is used for all CLI operations. It contains essential information like the
    user's auth token, the project ID, and the organization ID and other details.
    """
    pass


@cli_context.command(
    name="view",
    cls=HelpColorsCommand,
    help_headers_color=Colors.YELLOW,
    help_options_color=Colors.GREEN,
)
@click.option(
    "--format",
    "-f",
    "format_type",
    default="yaml",
    type=click.Choice(["json", "yaml"], case_sensitive=False),
)
def view_cli_context(format_type: Optional[str]) -> None:
    """View the current CLI context.

    This command prints the current CLI context to the console.
    """
    data = Configuration().data

    inspect_with_format(data, format_type)


@cli_context.command(
    hidden=True,
    name="set",
    cls=HelpColorsCommand,
    help_headers_color=Colors.YELLOW,
    help_options_color=Colors.GREEN,
)
@click.argument(
    "file",
    type=click.Path(
        exists=True, file_okay=True, dir_okay=False, resolve_path=True, path_type=Path
    ),
)
def set_cli_context(file: Path) -> None:
    """Set the CLI context.

    This command sets the CLI context to the values in the specified file.
    The supported file formats are JSON and YAML only.
    """
    with file.open(mode="r") as fp:
        if file.suffix == ".json":
            data = json.load(fp)
        elif file.suffix == ".yaml":
            data = yaml.safe_load(fp)
        else:
            raise Exception("unsupported file format")

        Configuration().data = data
        Configuration().save()

    click.secho(f"{Symbols.SUCCESS} Context has been updated.", fg=Colors.GREEN)

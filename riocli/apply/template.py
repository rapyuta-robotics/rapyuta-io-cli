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

import click
from click_help_colors import HelpColorsCommand

from riocli.apply.parse import Applier
from riocli.apply.util import process_files_values_secrets
from riocli.config import get_config_from_context
from riocli.constants import Colors


@click.command(
    "template",
    cls=HelpColorsCommand,
    help_headers_color=Colors.YELLOW,
    help_options_color=Colors.GREEN,
)
@click.option(
    "--values",
    "-v",
    multiple=True,
    default=(),
    help="Path to values yaml file. key/values specified in the "
    "values file can be used as variables in template YAMLs",
)
@click.option(
    "--secrets",
    "-s",
    multiple=True,
    default=(),
    help="Secret files are sops encoded value files. riocli "
    "expects sops to be authorized for decoding files on this computer",
)
@click.argument("files", nargs=-1)
@click.pass_context
def template(
    ctx: click.Context,
    values: typing.Tuple[str],
    secrets: typing.Tuple[str],
    files: typing.Tuple[str],
) -> None:
    """Print manifests with values and secrets applied

    The template command can be used to preview the manifests
    with values and secrets applied. This is particularly useful
    to check if the values and secrets are correctly substituted
    in the manifests before applying them.

    Just like the apply command, the template command also accepts
    a list of files as arguments. You can specify one or more files,
    directories or glob pattern.

    You can also specify one or more values and secrets files using
    the `-v` and `-s` flags respectively. The values and secrets files
    are used to substitute the variables in the manifests.

    Usage Examples:

        Specify one value and secret file

            rio template manifests/*.yaml -v values.yaml -s secrets.yaml

        Specify more than one values file

            rio template templates/** -v common.yaml -v site.yaml
    """
    glob_files, abs_values, abs_secrets = process_files_values_secrets(
        files, values, secrets
    )

    if len(glob_files) == 0:
        click.secho("No files specified", fg=Colors.RED)
        raise SystemExit(1)

    config = get_config_from_context(ctx)
    applier = Applier(glob_files, abs_values, abs_secrets, config)
    applier.print_resolved_manifests()

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

from typing import Iterable

import click
from click_help_colors import HelpColorsCommand

from riocli.apply.parse import Applier
from riocli.apply.util import process_files_values_secrets
from riocli.constants import Colors


@click.command(
    'template',
    cls=HelpColorsCommand,
    help_headers_color=Colors.YELLOW,
    help_options_color=Colors.GREEN,
)
@click.option('--values', '-v',
              help='Path to values yaml file. key/values specified in the '
                   'values file can be used as variables in template YAMLs')
@click.option('--secrets', '-s',
              help='Secret files are sops encoded value files. riocli '
                   'expects sops to be authorized for decoding files on this computer')
@click.argument('files', nargs=-1)
def template(values: str, secrets: str, files: Iterable[str]) -> None:
    """Print manifests with values and secrets applied

    The template command can be used to preview the manifests
    with values and secrets applied. This is particularly useful
    to check if the values and secrets are correctly substituted
    in the manifests before applying them.

    Just like the apply command, the template command also accepts
    a list of files as arguments. You can specify one or more files,
    directories or glob pattern.

    However, it will only accept on values and secrets file as input.

    Usage Examples:

    rio template manifests/*.yaml -v values.yaml -s secrets.yaml
    """
    glob_files, abs_values, abs_secrets = process_files_values_secrets(
        files, values, secrets)

    if len(glob_files) == 0:
        click.secho('No files specified', fg=Colors.RED)
        raise SystemExit(1)

    applier = Applier(glob_files, abs_values, abs_secrets)
    applier.print_resolved_manifests()

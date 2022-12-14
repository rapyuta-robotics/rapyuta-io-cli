# Copyright 2022 Rapyuta Robotics
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


@click.command(
    'template',
    cls=HelpColorsCommand,
    help_headers_color='yellow',
    help_options_color='green',
)
@click.option('--values', '-v',
              help="path to values yaml file. key/values specified in the values file can be used as variables in template yamls")
@click.option('--secrets', '-s',
              help="secret files are sops encoded value files. rio-cli expects sops to be authorized for decoding files on this computer")
@click.argument('files', nargs=-1)
def template(values: str, secrets: str, files: Iterable[str]) -> None:
    """
    Print manifests with filled values
    """
    glob_files, abs_values, abs_secrets = process_files_values_secrets(
        files, values, secrets)

    if len(glob_files) == 0:
        click.secho('no files specified', fg='red')
        raise SystemExit(1)

    rc = Applier(glob_files, abs_values, abs_secrets)
    rc.print_resolved_manifests()

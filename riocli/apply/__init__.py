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

from riocli.apply.explain import explain
from riocli.apply.parse import Applier
from riocli.apply.template import template
from riocli.apply.util import process_files_values_secrets
from riocli.constants import Colors


@click.command(
    'apply',
    cls=HelpColorsCommand,
    help_headers_color=Colors.YELLOW,
    help_options_color=Colors.GREEN,
)
@click.option('--dryrun', '-d', is_flag=True, default=False,
              help='dry run the yaml files without applying any change')
@click.option('--show-graph', '-g', is_flag=True, default=False,
              help='Opens a mermaid.live dependency graph')
@click.option('--values', '-v',
              help="path to values yaml file. key/values "
                   "specified in the values file can be "
                   "used as variables in template YAMLs")
@click.option('--secrets', '-s',
              help="secret files are sops encoded value files. "
                   "rio-cli expects sops to be authorized for "
                   "decoding files on this computer")
@click.option('--workers', '-w',
              help="number of parallel workers while running apply "
                   "command. defaults to 6.", type=int)
@click.option('-f', '--force', '--silent', 'silent', is_flag=True,
              type=click.BOOL, default=False,
              help="Skip confirmation")
@click.option('--retry-count', '-rc', type=int, default=50,
              help="Number of retries before a resource creation times out status, defaults to 50")
@click.option('--retry-interval', '-ri', type=int, default=6,
              help="Interval between retries defaults to 6")
@click.argument('files', nargs=-1)
def apply(
        values: str,
        secrets: str,
        files: Iterable[str],
        retry_count: int = 50,
        retry_interval: int = 6,
        dryrun: bool = False,
        workers: int = 6,
        silent: bool = False,
        show_graph: bool = False,
) -> None:
    """
    Apply resource manifests
    """
    glob_files, abs_values, abs_secrets = process_files_values_secrets(
        files, values, secrets)

    if len(glob_files) == 0:
        click.secho('No files specified', fg=Colors.RED)
        raise SystemExit(1)

    click.secho("----- Files Processed ----", fg=Colors.YELLOW)
    for file in glob_files:
        click.secho(file, fg=Colors.YELLOW)

    rc = Applier(glob_files, abs_values, abs_secrets)
    rc.parse_dependencies()

    if show_graph and dryrun:
        click.secho('You cannot dry run and launch the graph together.',
                    fg='yellow')
        return

    if show_graph:
        rc.show_dependency_graph()
        return

    if not silent and not dryrun:
        click.confirm("Do you want to proceed?", default=True, abort=True)

    rc.apply(dryrun=dryrun, workers=workers, retry_count=retry_count, retry_interval=retry_interval)


@click.command(
    'delete',
    cls=HelpColorsCommand,
    help_headers_color=Colors.YELLOW,
    help_options_color=Colors.GREEN,
)
@click.option('--dryrun', '-d', is_flag=True, default=False,
              help='dry run the yaml files without applying any change')
@click.option('--values', '-v',
              help="Path to values yaml file. key/values specified in the"
                   " values file can be used as variables in template YAMLs")
@click.option('--secrets', '-s',
              help="Secret files are sops encoded value files. riocli expects "
                   "sops to be authorized for decoding files on this computer")
@click.option('-f', '--force', '--silent', 'silent', is_flag=True,
              type=click.BOOL, default=False,
              help="Skip confirmation")
@click.argument('files', nargs=-1)
def delete(
        values: str,
        secrets: str,
        files: Iterable[str],
        dryrun: bool = False,
        silent: bool = False
) -> None:
    """
    Removes resources defined in the manifest
    """
    glob_files, abs_values, abs_secrets = process_files_values_secrets(
        files, values, secrets)

    if len(glob_files) == 0:
        click.secho('no files specified', fg=Colors.RED)
        raise SystemExit(1)

    rc = Applier(glob_files, abs_values, abs_secrets)
    rc.parse_dependencies(check_missing=False, delete=True)

    if not silent and not dryrun:
        click.confirm("Do you want to proceed?", default=True, abort=True)

    rc.delete(dryrun=dryrun)

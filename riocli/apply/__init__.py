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
from riocli.apply.util import print_context, process_files_values_secrets
from riocli.config import get_config_from_context
from riocli.constants import Colors
from riocli.utils import print_centered_text


@click.command(
    "apply",
    cls=HelpColorsCommand,
    help_headers_color=Colors.YELLOW,
    help_options_color=Colors.GREEN,
)
@click.option(
    "--dryrun",
    "-d",
    is_flag=True,
    default=False,
    help="Dry run the yaml files without applying any change",
)
@click.option(
    "--show-graph",
    "-g",
    is_flag=True,
    default=False,
    help="Opens a mermaid.live dependency graph",
)
@click.option(
    "--values",
    "-v",
    multiple=True,
    default=(),
    help="Path to values yaml file. Key/values "
    "specified in the values file can be "
    "used as variables in template YAMLs",
)
@click.option(
    "--secrets",
    "-s",
    multiple=True,
    default=(),
    help="Secret files are sops encoded value files. "
    "rio-cli expects sops to be authorized for "
    "decoding files on this computer",
)
@click.option(
    "--workers",
    "-w",
    help="Number of parallel workers while running apply command. defaults to 6.",
    type=int,
)
@click.option(
    "--recreate",
    "--delete-existing",
    "delete_existing",
    is_flag=True,
    default=False,
    help="Overwrite existing resources",
)
@click.option(
    "-f",
    "--force",
    "--silent",
    "silent",
    is_flag=True,
    type=click.BOOL,
    default=False,
    help="Skip confirmation",
)
@click.option(
    "--retry-count",
    "-rc",
    type=int,
    default=50,
    help="Number of retries before a resource creation times out status, defaults to 50",
)
@click.option(
    "--retry-interval",
    "-ri",
    type=int,
    default=6,
    help="Interval between retries defaults to 6",
)
@click.argument("files", nargs=-1)
@click.pass_context
def apply(
    ctx: click.Context,
    values: Iterable[str],
    secrets: Iterable[str],
    files: Iterable[str],
    retry_count: int = 50,
    retry_interval: int = 6,
    delete_existing: bool = False,
    dryrun: bool = False,
    workers: int = 6,
    silent: bool = False,
    show_graph: bool = False,
) -> None:
    """Apply resource manifests.

    The apply command provides the mechanism to create or update resources on
    rapyuta.io. The resources are defined in YAML manifests allowing for a
    declarative and repeatable process. The command can take multiple files,
    paths or globs as arguments and parse the manifests to create or update
    resources.

    The manifest files can optionally be templated using Jinja2 syntax. All the
    Ansible filters are supported. The secret management with sops is also
    supported.

    You can provide value files with the ``--values`` option and
    sops encrypted secret files with ``--secret`` option.

    You can use the ``--show-graph`` option to visualize the
    dependency graph of the resources defined in the manifests.

    The --dryrun option can be used to execute the manifests without
    actually creating the resources. This is useful to validate the
    manifests before applying them.

    You can specify the number of parallel workers with the ``--workers``
    option. The default value is ``6``.

    The ``--silent``, ``--force`` or ``-f`` option lets you skip the confirmation
    prompt before applying the manifests. This is particularly useful
    in CI/CD pipelines.

    Usage Examples:

        Apply a single manifest file with secret and values file.

            $ rio apply -v values.yaml -s secrets.yaml manifest.yaml

        Apply manifests from a directory with secret and values file.

            $ rio apply -v values.yaml -s secrets.yaml templates/

        Apply manifests from a directory without confirmation prompt.

            $ rio apply -f templates/

        Apply manifests with multiple value files.

            $ rio apply -v values1.yaml -v values2.yaml templates/**

        Re-create existing resources from the manifests.

            $ rio apply -v values.yaml --delete-existing templates/

    """
    print_context(ctx)

    glob_files, abs_values, abs_secrets = process_files_values_secrets(
        files, values, secrets
    )

    if len(glob_files) == 0:
        click.secho("No files specified", fg=Colors.RED)
        raise SystemExit(1)

    print_centered_text("Files Processed")
    for file in glob_files:
        click.secho(file, fg=Colors.YELLOW)

    config = get_config_from_context(ctx)

    applier = Applier(glob_files, abs_values, abs_secrets, config)
    applier.parse_dependencies()

    if show_graph and dryrun:
        click.secho("You cannot dry run and launch the graph together.", fg="yellow")
        return

    if show_graph:
        applier.show_dependency_graph()
        return

    if not silent and not dryrun:
        click.confirm("\nDo you want to proceed?", default=True, abort=True)

    if delete_existing:
        deleter = Applier(glob_files, abs_values, abs_secrets, config)
        deleter.parse_dependencies(print_resources=False)

        print_centered_text("Deleting Resources")
        deleter.delete(
            dryrun=dryrun,
            workers=workers,
            retry_count=retry_count,
            retry_interval=retry_interval,
        )

    print_centered_text("Applying Manifests")
    applier.apply(
        dryrun=dryrun,
        workers=workers,
        retry_count=retry_count,
        retry_interval=retry_interval,
    )


@click.command(
    "delete",
    cls=HelpColorsCommand,
    help_headers_color=Colors.YELLOW,
    help_options_color=Colors.GREEN,
)
@click.option(
    "--dryrun",
    "-d",
    is_flag=True,
    default=False,
    help="Dry run the yaml files without applying any change",
)
@click.option(
    "--values",
    "-v",
    multiple=True,
    default=(),
    help="Path to values yaml file. key/values specified in the"
    " values file can be used as variables in template YAMLs",
)
@click.option(
    "--secrets",
    "-s",
    multiple=True,
    default=(),
    help="Secret files are sops encoded value files. riocli expects "
    "sops to be authorized for decoding files on this computer",
)
@click.option(
    "-f",
    "--force",
    "--silent",
    "silent",
    is_flag=True,
    type=click.BOOL,
    default=False,
    help="Skip confirmation",
)
@click.option(
    "--workers",
    "-w",
    help="Number of parallel workers while running apply command. defaults to 6.",
    type=int,
)
@click.option(
    "--retry-count",
    "-rc",
    type=int,
    default=50,
    help="Number of retries before a resource creation times out status, defaults to 50",
)
@click.option(
    "--retry-interval",
    "-ri",
    type=int,
    default=6,
    help="Interval between retries defaults to 6",
)
@click.argument("files", nargs=-1)
@click.pass_context
def delete(
    ctx: click.Context,
    values: str,
    secrets: str,
    files: Iterable[str],
    retry_count: int = 50,
    retry_interval: int = 6,
    dryrun: bool = False,
    workers: int = 6,
    silent: bool = False,
) -> None:
    """Removes resources via manifests

    The delete command provides the mechanism to remove resources on
    rapyuta.io defined in YAML manifests making the process declarative
    and repeatable. The command can take multiple files, paths or globs
    as arguments and parse the manifests to remove resources.

    The manifest files can optionally be templated using Jinja2 syntax. All the
    Ansible filters are supported. The secret management with sops is also
    supported.

    You can provide value files with the ``--values`` option and
    sops encrypted secret files with ``--secret`` option.

    The ``--dryrun`` option can be used to execute the manifests without
    actually deleting the resources. This is useful to validate the
    manifests before applying them.

    You can specify the number of parallel workers with the ``--workers``
    option. The default value is ``6``.

    The ``--silent``, ``--force`` or ``-f`` option lets you skip the confirmation
    prompt before applying the manifests. This is particularly useful
    in CI/CD pipelines.

    Usage Examples:

        Delete a single manifest file with secret and values file.

            $ rio delete -v values.yaml -s secrets.yaml manifest.yaml

        Delete manifests from a directory with secret and values file.

            $ rio delete -v values.yaml -s secrets.yaml templates/

        Delete manifests from a directory without confirmation prompt.

            $ rio delete -f templates/

        Delete manifests with multiple value files.

            $ rio delete -v values1.yaml -v values2.yaml templates/**

    """

    print_context(ctx)

    glob_files, abs_values, abs_secrets = process_files_values_secrets(
        files, values, secrets
    )

    if len(glob_files) == 0:
        click.secho("no files specified", fg=Colors.RED)
        raise SystemExit(1)

    print_centered_text("Files Processed")
    for file in glob_files:
        click.secho(file, fg=Colors.YELLOW)

    config = get_config_from_context(ctx)

    applier = Applier(glob_files, abs_values, abs_secrets, config)
    applier.parse_dependencies()

    if not silent and not dryrun:
        click.confirm("\nDo you want to proceed?", default=True, abort=True)

    print_centered_text("Deleting Resources")
    applier.delete(
        dryrun=dryrun,
        workers=workers,
        retry_count=retry_count,
        retry_interval=retry_interval,
    )

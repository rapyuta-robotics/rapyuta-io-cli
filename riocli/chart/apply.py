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

from riocli.chart.chart import Chart
from riocli.chart.util import find_chart
from riocli.constants import Colors


@click.command(
    "apply",
    cls=HelpColorsCommand,
    help_headers_color=Colors.YELLOW,
    help_options_color=Colors.GREEN,
    help="Apply a new Rapyuta Chart in the Project",
)
@click.option(
    "--dryrun",
    "-d",
    is_flag=True,
    default=False,
    help="dry run the yaml files without applying any change",
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
    "--values",
    "-v",
    multiple=True,
    default=(),
    help="Path to values yaml file. key/values specified in the "
    "values file can be used as variables in template yamls",
)
@click.option(
    "--secrets",
    "-s",
    multiple=True,
    default=(),
    help="Secret files are sops encoded value files. rio-cli "
    "expects sops to be authorized for decoding files on "
    "this computer",
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
    "--workers",
    "-w",
    help="number of parallel workers while running apply command. " "defaults to 6.",
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
@click.argument("chart", type=str)
def apply_chart(
    chart: str,
    values: Iterable[str],
    secrets: Iterable[str],
    retry_count: int = 50,
    retry_interval: int = 6,
    delete_existing: bool = False,
    dryrun: bool = False,
    workers: int = 6,
    silent: bool = False,
) -> None:
    """Install a chart from the rapyuta-charts repository.

    This command is based on the ``rio apply`` command. However,
    the manifests are pulled from rapyuta-charts repository on
    GitHub. A rapyuta chart is collection of manifest files with
    default values.

    You can provide value files with the ``--values`` option and
    sops encrypted secret files with ``--secret`` option.

    The ``--workers`` flag can be used to specify the number of parallel
    workers while running the apply command. The default value is 6.

    The ``--dryrun`` flag can be used to test the installation process
    without actually installing the chart.

    Repository: https://github.com/rapyuta-robotics/rapyuta-charts

    Usage Examples:

     Apply a chart with values and secrets files

        $ rio chart apply ioconfig-syncer -v values.yaml -s secrets.yaml

     Apply a chart with values and secrets files without confirmation

        $ rio chart apply ioconfig-syncer -v values.yaml -s secrets.yaml -f

     Re-create existing chart resources.

        $ rio chart apply -v values.yaml --delete-existing
    """
    versions = find_chart(chart)
    if len(versions) > 1:
        click.secho(
            "More than one charts are available, please specify the version!",
            fg=Colors.RED,
        )

    c = Chart(**versions[0])
    c.apply_chart(
        values,
        secrets,
        dryrun=dryrun,
        delete_existing=delete_existing,
        workers=workers,
        silent=silent,
        retry_count=retry_count,
        retry_interval=retry_interval,
    )
    c.cleanup()

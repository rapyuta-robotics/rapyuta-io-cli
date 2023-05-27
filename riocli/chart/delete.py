# Copyright 2023 Rapyuta Robotics
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
import click
from click_help_colors import HelpColorsCommand

from riocli.chart.chart import Chart
from riocli.chart.util import find_chart
from riocli.constants import Colors


@click.command(
    'delete',
    cls=HelpColorsCommand,
    help_headers_color=Colors.YELLOW,
    help_options_color=Colors.GREEN,
    help='Delete the Rapyuta Chart from the Project',
)
@click.option('--dryrun', '-d', is_flag=True, default=False,
              help='Dry run the yaml files without applying any change')
@click.option('-f', '--force', '--silent', 'silent', is_flag=True,
              type=click.BOOL, default=False, help="Skip confirmation")
@click.option('--values', '-v',
              help=("Path to values yaml file. key/values specified in the"
                    "values file can be used as variables in template yamls"))
@click.option('--secrets', '-s',
              help=("Secret files are sops encoded value files. rio-cli "
                    "expects sops to be authorized for decoding files on "
                    "this computer"))
@click.argument('chart', type=str)
def delete_chart(
        chart: str,
        values: str,
        secrets: str,
        dryrun: bool = False,
        silent: bool = False) -> None:
    """Uninstall a chart."""
    versions = find_chart(chart)
    if len(versions) > 1:
        click.secho('More than one charts are available, '
                    'please specify the version!', fg=Colors.YELLOW)

    chart = Chart(**versions[0])
    chart.delete_chart(values=values, secrets=secrets,
                       dryrun=dryrun, silent=silent)
    chart.cleanup()

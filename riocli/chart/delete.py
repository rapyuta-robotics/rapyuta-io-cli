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
import click
from click_help_colors import HelpColorsCommand

from riocli.chart.chart import Chart
from riocli.chart.util import find_chart


@click.command(
    'delete',
    cls=HelpColorsCommand,
    help_headers_color='yellow',
    help_options_color='green',
    help='Delete the Rapyuta Chart from the Project',
)
@click.option('--values')
@click.option('--dryrun', '-d', is_flag=True, default=False, help='Perform dry-run for applying the chart')
@click.argument('chart', type=str)
def delete_chart(chart: str, values: str, dryrun: bool) -> None:
    versions = find_chart(chart)
    if len(versions) > 1:
        click.secho('More than one charts are available, please specify the version!', fg='red')

    chart = Chart(**versions[0])
    chart.delete_chart(values, dryrun)
    chart.cleanup()

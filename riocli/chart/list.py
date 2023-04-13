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
from munch import munchify

from riocli.chart.util import fetch_index, print_chart_entries


@click.command(
    'list',
    cls=HelpColorsCommand,
    help_headers_color='yellow',
    help_options_color='green',
)
@click.option('-w', '--wide', is_flag=True, default=False,
              help='Print more details')
def list_charts(wide: bool = False) -> None:
    """List all available charts."""
    index = fetch_index()
    if 'entries' not in index:
        raise Exception('No entries found!')
    entries = []
    for name, chart in index['entries'].items():
        for version in chart:
            entries.append(version)

    print_chart_entries(munchify(entries), wide=wide)

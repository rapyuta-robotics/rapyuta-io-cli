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
import typing

import click
from click_help_colors import HelpColorsCommand
from munch import munchify
from tabulate import tabulate
from yaml import safe_dump_all

from riocli.chart.util import find_chart, fetch_index


@click.command(
    'info',
    cls=HelpColorsCommand,
    help_headers_color='yellow',
    help_options_color='green',
    help='Describe the available chart with versions',
)
@click.argument('chart', type=str)
def info_chart(chart: str) -> None:
    versions = find_chart(chart)
    click.echo(safe_dump_all(versions))


@click.command(
    'search',
    cls=HelpColorsCommand,
    help_headers_color='yellow',
    help_options_color='green',
    help='Search for available charts in the repository',
)
@click.argument('chart', type=str)
def search_chart(chart: str) -> None:
    versions = find_chart(chart)
    _display_entries(versions)


@click.command(
    'list',
    cls=HelpColorsCommand,
    help_headers_color='yellow',
    help_options_color='green',
)
def list_charts() -> None:
    index = fetch_index()
    if 'entries' not in index:
        raise Exception('No entries found!')
    entries = []
    for name, chart in index['entries'].items():
        for version in chart:
            entries.append(version)
    
    _display_entries(munchify(entries))


def _display_entries(entries: typing.List) -> None:
    headers, table = [], []
    for header in ['Name', 'Version', 'Description', 'Created At']:
        headers.append(click.style(header, fg='yellow'))

    for entry in entries:
        table.append([entry.get('name'), entry.get('version'),entry.get('description'), entry.get('created')])

    click.echo(tabulate(table, headers=headers, tablefmt='simple'))

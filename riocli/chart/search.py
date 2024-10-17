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

import click
from click_help_colors import HelpColorsCommand
from yaspin.api import Yaspin

from riocli.chart.util import find_chart, print_chart_entries
from riocli.constants import Colors, Symbols
from riocli.utils.spinner import with_spinner


@click.command(
    "search",
    cls=HelpColorsCommand,
    help_headers_color=Colors.YELLOW,
    help_options_color=Colors.GREEN,
    help="Search for available charts in the repository",
)
@click.option("-w", "--wide", is_flag=True, default=False, help="Print more details")
@click.argument("chart", type=str)
@with_spinner(text="Searching for chart...")
def search_chart(chart: str, wide: bool = False, spinner: Yaspin = None) -> None:
    """Search for a chart in the chart repo."""
    try:
        versions = find_chart(chart)
        with spinner.hidden():
            print_chart_entries(versions, wide=wide)
    except Exception as e:
        spinner.text = click.style(str(e), fg=Colors.RED)
        spinner.red.fail(Symbols.ERROR)
        raise SystemExit(1) from e

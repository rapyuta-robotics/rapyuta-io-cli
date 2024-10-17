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

from riocli.chart.util import find_chart
from riocli.constants import Colors
from riocli.utils import dump_all_yaml


@click.command(
    "info",
    cls=HelpColorsCommand,
    help_headers_color=Colors.YELLOW,
    help_options_color=Colors.GREEN,
    help="Describe the available chart with versions",
)
@click.argument("chart", type=str)
def info_chart(chart: str) -> None:
    """Print a chart's details."""
    versions = find_chart(chart)
    dump_all_yaml(versions)

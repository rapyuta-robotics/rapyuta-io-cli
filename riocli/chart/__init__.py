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
from click_help_colors import HelpColorsGroup

from riocli.chart.apply import apply_chart
from riocli.chart.delete import delete_chart
from riocli.chart.search import list_charts, search_chart, info_chart


@click.group(
    invoke_without_command=False,
    cls=HelpColorsGroup,
    help_headers_color='yellow',
    help_options_color='green',
)
def chart() -> None:
    """
    Rapyuta Charts is a way to package the complete Application for Rapyuta.io Platform.
    """
    pass


chart.add_command(search_chart)
chart.add_command(info_chart)
chart.add_command(apply_chart)
chart.add_command(delete_chart)
chart.add_command(list_charts)

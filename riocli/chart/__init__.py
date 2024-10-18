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
from click_help_colors import HelpColorsGroup

from riocli.chart.apply import apply_chart
from riocli.chart.delete import delete_chart
from riocli.chart.info import info_chart
from riocli.chart.list import list_charts
from riocli.chart.search import search_chart
from riocli.constants import Colors


@click.group(
    invoke_without_command=False,
    cls=HelpColorsGroup,
    help_headers_color=Colors.YELLOW,
    help_options_color=Colors.GREEN,
)
def chart() -> None:
    """Rapyuta chart is a way to package applications.

    With rapyuta chart, you can create, install, and manage applications
    that are a collection of one or more deployments and other resources.
    A chart comprises a collection of manifest files that define the
    resources to be created. It may also offer customization by means of
    values or secrets.
    """
    pass


chart.add_command(search_chart)
chart.add_command(info_chart)
chart.add_command(apply_chart)
chart.add_command(delete_chart)
chart.add_command(list_charts)

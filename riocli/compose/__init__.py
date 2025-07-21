# Copyright 2025 Rapyuta Robotics
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

from riocli.compose.down import down
from riocli.compose.generate import generate
from riocli.compose.up import up
from riocli.constants.colors import Colors


@click.group(
    invoke_without_command=False,
    cls=HelpColorsGroup,
    help_headers_color=Colors.YELLOW,
    help_options_color=Colors.GREEN,
)
def compose() -> None:
    """
    Manage Docker Compose workflows from Rapyuta.io manifests.

    This command group provides high-level operations to generate, start, and stop Docker Compose
    services based on Rapyuta.io manifest files, values, and secrets.
    """

    pass


compose.add_command(generate)
compose.add_command(up)
compose.add_command(down)

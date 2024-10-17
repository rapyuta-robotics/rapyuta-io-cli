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

from riocli.constants import Colors


@click.command(
    "status",
    cls=HelpColorsCommand,
    help_headers_color=Colors.YELLOW,
    help_options_color=Colors.GREEN,
)
@click.pass_context
def status(ctx: click.Context):
    """Shows the current login status."""
    if not ctx.obj.exists:
        click.secho("🔒You are logged out", fg=Colors.YELLOW)
        raise SystemExit(1)

    if "auth_token" in ctx.obj.data:
        click.secho("🎉 You are logged in", fg=Colors.GREEN)

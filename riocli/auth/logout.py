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

from riocli.constants import Colors, Symbols


@click.command(
    "logout",
    cls=HelpColorsCommand,
    help_headers_color=Colors.YELLOW,
    help_options_color=Colors.GREEN,
)
@click.pass_context
def logout(ctx: click.Context):
    """Log out from your rapyuta.io account."""
    if not ctx.obj.exists:
        return

    ctx.obj.data.pop("email_id", None)
    ctx.obj.data.pop("auth_token", None)
    ctx.obj.data.pop("project_id", None)
    ctx.obj.data.pop("project_name", None)
    ctx.obj.data.pop("organization_id", None)
    ctx.obj.data.pop("organization_name", None)
    ctx.obj.data.pop("organization_short_id", None)

    ctx.obj.save()

    click.secho("{} Logged out successfully.".format(Symbols.SUCCESS), fg=Colors.GREEN)

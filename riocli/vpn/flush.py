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
from click_help_colors import HelpColorsCommand

from riocli.constants.colors import Colors
from riocli.constants.symbols import Symbols
from riocli.utils import run_bash
from riocli.vpn.util import is_linux, priviledged_command


@click.command(
    "flush",
    cls=HelpColorsCommand,
    help_headers_color=Colors.YELLOW,
    help_options_color=Colors.GREEN,
)
def flush() -> None:
    """Flush the VPN configuration.

    This command clears the local Tailscale configuration for prestine state.
    """
    if not is_linux():
        click.secho("Only linux is supported", fg=Colors.YELLOW)
        raise SystemExit(1)

    run_bash(priviledged_command("systemctl stop tailscaled"))
    run_bash(priviledged_command("rm -rvf /var/lib/tailscale/"))
    run_bash(priviledged_command("systemctl start tailscaled"))
    click.secho("{} VPN configurations flushed.".format(Symbols.SUCCESS), fg=Colors.GREEN)

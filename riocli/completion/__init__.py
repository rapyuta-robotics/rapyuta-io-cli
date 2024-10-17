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
import os

import click
from click_help_colors import HelpColorsCommand


@click.command(
    cls=HelpColorsCommand,
    help_headers_color="yellow",
    help_options_color="green",
)
@click.argument("shell-name", type=click.Choice(["zsh", "fish", "bash"]))
def completion(shell_name):
    """
    Output shell completion code for the specified shell

    This command outputs the Completion functions for the supported Shells. You can add the following command in your
    Shell's Runtime Configuration file to evaluate the Completion Code everytime the new shell starts.

    For Bash:
        $ source <(rio completion bash)
    For Fish:
        $ eval (command rio completion bash)
    """
    os.environ["_RIO_COMPLETE"] = "{}_source".format(shell_name)
    os.system("rio")

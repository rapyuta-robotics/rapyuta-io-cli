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
import os

import click
from click_help_colors import HelpColorsCommand
from click_repl import repl
from prompt_toolkit.history import FileHistory, ThreadedHistory

from riocli.config import Configuration
from riocli.shell.prompt import prompt_callback


@click.command(
    cls=HelpColorsCommand,
    help_headers_color='yellow',
    help_options_color='green',
)
@click.pass_context
def shell(ctx: click.Context):
    """
    Interactive Shell for Rapyuta.io
    """
    start_shell(ctx)


@click.command(
    'repl',
    cls=HelpColorsCommand,
    help_headers_color='yellow',
    help_options_color='green',
    hidden=True
)
@click.pass_context
def deprecated_repl(ctx: click.Context):
    """
    [Deprecated] Use "rio shell" instead
    """
    start_shell(ctx)


def start_shell(ctx: click.Context):
    prompt_config = _parse_config(ctx.obj)
    while True:
        try:
            repl(click.get_current_context(), prompt_kwargs=prompt_config)
        except Exception as e:
            click.secho(str(e), fg='red')
        else:
            break


def _parse_config(config: Configuration) -> dict:
    history_path = os.path.join(click.get_app_dir(config.APP_NAME), "history")
    default_prompt_kwargs = {
        'history': ThreadedHistory(FileHistory(history_path)),
        'message': prompt_callback,
        'enable_suspend': True
    }

    shell_config = config.data.get('shell', {})

    return {**default_prompt_kwargs, **shell_config}

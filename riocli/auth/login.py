# Copyright 2021 Rapyuta Robotics
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

from riocli.auth.util import select_project, get_token
from riocli.utils.context import get_root_context


@click.command(
    cls=HelpColorsCommand,
    help_headers_color='yellow',
    help_options_color='green',
)
@click.option('--email', type=str,
              help='Email of the Rapyuta.io account')
@click.option('--password', type=str,
              help='Password for the Rapyuta.io account')
@click.option('--project', type=str, default=None,
              help='Context will be set to the Project after authentication')
@click.option('--interactive/--no-interactive', is_flag=True, type=bool, default=True,
              help='Make login interactive')
@click.pass_context
def login(ctx: click.Context, email: str, password: str, project: str, interactive: bool):
    """
    Log into the Rapyuta.io account using the CLI. This is required to use most of the
    functionalities of the CLI.
    """

    if interactive:
        email = email or click.prompt('Email')
        password = password or click.prompt('Password', hide_input=True)

    if not email:
        click.secho('email not specified')
        raise SystemExit(1)
    if not password:
        click.secho('password not specified')
        raise SystemExit(1)

    ctx = get_root_context(ctx)
    ctx.obj.data['email_id'] = email
    ctx.obj.data['password'] = password
    ctx.obj.data['auth_token'] = get_token(email, password)

    # Save if the file does not already exist
    if not ctx.obj.exists or not interactive:
        ctx.obj.save()
    else:
        click.echo("[Warning] rio already has a config file present")
        click.confirm('Do you want to override the config', abort=True)

    if not interactive and not project:
        click.echo('Logged in successfully!')
        return

    select_project(ctx.obj, project=project)
    ctx.obj.save()
    click.echo('Logged in successfully!')

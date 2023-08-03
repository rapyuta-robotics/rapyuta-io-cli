# Copyright 2023 Rapyuta Robotics
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

from riocli.auth.util import (
    get_token,
    select_organization,
    select_project,
    validate_token,
)
from riocli.constants import Colors, Symbols
from riocli.utils.context import get_root_context

LOGIN_SUCCESS = click.style('{} Logged in successfully!'.format(Symbols.SUCCESS), fg=Colors.GREEN)


@click.command(
    'login',
    cls=HelpColorsCommand,
    help_headers_color=Colors.YELLOW,
    help_options_color=Colors.GREEN,
)
@click.option('--email', type=str,
              help='Email of the rapyuta.io account')
@click.option('--password', type=str,
              help='Password for the rapyuta.io account')
@click.option('--organization', type=str, default=None,
              help=('Context will be set to the organization after '
                    'authentication'))
@click.option('--project', type=str, default=None,
              help='Context will be set to the project after authentication')
@click.option('--interactive/--no-interactive', '--interactive/--silent',
              is_flag=True, type=bool, default=True,
              help='Make login interactive')
@click.option('--auth-token', type=str, default=None,
              help="Login with auth token only")
@click.pass_context
def login(
        ctx: click.Context,
        email: str,
        password: str,
        organization: str,
        project: str,
        interactive: bool,
        auth_token: str,
) -> None:
    """
    Log into your rapyuta.io account using the CLI. This is required to
    use most commands of the CLI.
    
    You can log in with your email and password or just with and auth token
    if you already have one.
    """
    ctx = get_root_context(ctx)

    if auth_token:
        if not validate_token(auth_token):
            raise SystemExit(1)
        ctx.obj.data['auth_token'] = auth_token
    else:
        if interactive:
            email = email or click.prompt('Email')
            password = password or click.prompt('Password', hide_input=True)

        if not email:
            click.secho('email not specified')
            raise SystemExit(1)

        if not password:
            click.secho('password not specified')
            raise SystemExit(1)

        ctx.obj.data['email_id'] = email
        ctx.obj.data['password'] = password
        ctx.obj.data['auth_token'] = get_token(email, password)

    # Save if the file does not already exist
    if not ctx.obj.exists or not interactive:
        ctx.obj.save()
    else:
        click.confirm(
            '{} Config already exists. Do you want to override'
            ' the existing config?'.format(Symbols.WARNING),
            abort=True)

    if not interactive:
        # When just the email and password are provided
        if not project and not organization:
            click.echo(LOGIN_SUCCESS)
            return

        # When project is provided without an organization.
        # It is quite possible to have a project with the
        # same name in two organizations. Hence, organization
        # needs to be explicitly provided in this case.
        if project and not organization:
            click.secho(
                'Please specify an organization. See `rio auth login --help`',
                fg=Colors.YELLOW)
            raise SystemExit(1)

        # When just the organization is provided, we save the
        # organization name and id and the login is marked as
        # successful.
        if organization and not project:
            select_organization(ctx.obj, organization=organization)
            click.secho("Your organization is set to '{}'".format(
                ctx.obj.data['organization_name']), fg=Colors.CYAN)
            ctx.obj.save()
            click.echo(LOGIN_SUCCESS)
            return

    organization = select_organization(ctx.obj, organization=organization)
    select_project(ctx.obj, project=project, organization=organization)

    ctx.obj.save()

    click.echo(LOGIN_SUCCESS)

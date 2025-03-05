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

from riocli.auth.util import (
    get_token,
    select_organization,
    select_project,
    validate_and_set_token,
)
from riocli.config import get_config_from_context
from riocli.constants import Colors, Symbols
from riocli.utils.context import get_root_context
from riocli.vpn.util import cleanup_hosts_file

LOGIN_SUCCESS = click.style(
    "{} Logged in successfully!".format(Symbols.SUCCESS), fg=Colors.GREEN
)


@click.command(
    "login",
    cls=HelpColorsCommand,
    help_headers_color=Colors.YELLOW,
    help_options_color=Colors.GREEN,
)
@click.option("--email", type=str, help="Email of the rapyuta.io account")
@click.option("--password", type=str, help="Password for the rapyuta.io account")
@click.option(
    "--organization",
    type=str,
    default=None,
    help=("Context will be set to the organization after authentication"),
)
@click.option(
    "--project",
    type=str,
    default=None,
    help="Context will be set to the project after authentication",
)
@click.option(
    "--interactive/--no-interactive",
    "--interactive/--silent",
    is_flag=True,
    type=bool,
    default=True,
    help="Make login interactive",
)
@click.option("--auth-token", type=str, default=None, help="Login with auth token only")
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
    """Log into your rapyuta.io account.

    This is the first step to start using the CLI.

    You can log in with your email and password or
    just with and auth token if you already have one.
    The command works in an interactive mode by default
    and will prompt you to enter your credentials and
    select the organization and project you want to work
    with.

    You can also use the command in non-interactive mode
    by providing the email and password as arguments and
    setting the --no-interactive or --silent flag. In this
    mode, you can also set the organization and project
    using the --organization and --project flags. If you
    do not provide the organization and project, you will
    have to set them later using the `rio organization select`
    and `rio project select` commands.

    Note: If you have special characters in your password, then
    consider putting them in quotes to avoid the terminal from
    interpreting them otherwise.

    Usage Examples:

        Login interactively

        $ rio auth login

        Login interactively with email and password

        $ rio auth login --email YOUR_EMAIL --password YOUR_PASSWORD

        Login non-interactively with email and password

        $ rio auth login --email YOUR_EMAIL --password YOUR_PASSWORD --no-interactive

        Login non-interactively with email, password, organization and project

        $ rio auth login --email YOUR_EMAIL --password YOUR_PASSWORD --organization YOUR_ORG --project YOUR_PROJECT --silent

        Login with auth token

        $ rio auth login --auth-token YOUR_AUTH_TOKEN
    """
    ctx = get_root_context(ctx)
    config = get_config_from_context(ctx)

    if auth_token:
        if not validate_and_set_token(ctx, auth_token):
            raise SystemExit(1)
    else:
        if interactive:
            email = email or click.prompt("Email")
            password = password or click.prompt("Password", hide_input=True)

        if not email:
            click.secho("email not specified")
            raise SystemExit(1)

        if not password:
            click.secho("password not specified")
            raise SystemExit(1)

        config.data["email_id"] = email
        config.data["auth_token"] = get_token(email, password)

    # Save if the file does not already exist
    if not config.exists or not interactive:
        config.save()
    else:
        click.confirm(
            "{} Config already exists. Do you want to override"
            " the existing config?".format(Symbols.WARNING),
            abort=True,
        )

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
                "Please specify an organization. See `rio auth login --help`",
                fg=Colors.YELLOW,
            )
            raise SystemExit(1)

        # When just the organization is provided, we save the
        # organization name and id and the login is marked as
        # successful.
        if organization and not project:
            select_organization(config, organization=organization)
            click.secho(
                "Your organization is set to '{}'".format(
                    config.data["organization_name"]
                ),
                fg=Colors.CYAN,
            )
            config.save()
            click.echo(LOGIN_SUCCESS)
            return

    organization = select_organization(config, organization=organization)
    select_project(config, project=project, organization=organization)

    config.save()

    try:
        cleanup_hosts_file()
    except Exception as e:
        click.secho(
            f"{Symbols.WARNING} Failed to clean up hosts file: {str(e)}",
            fg=Colors.YELLOW,
        )

    click.echo(LOGIN_SUCCESS)

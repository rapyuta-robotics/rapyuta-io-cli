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
from munch import munchify

from riocli.auth.device_flow import (
    DeviceFlowError,
    discover_oidc_endpoints,
    display_user_code,
    poll_for_token,
    request_device_code,
)
from riocli.auth.util import (
    decode_jwt_claims,
    get_token,
    select_organization,
    select_project,
)
from riocli.config import get_config_from_context
from riocli.config.config import Configuration
from riocli.constants import Colors, Symbols
from riocli.utils.context import get_root_context
from riocli.vpn.util import cleanup_hosts_file

LOGIN_SUCCESS = click.style(f"{Symbols.SUCCESS} Logged in successfully!", fg=Colors.GREEN)


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
    is_flag=True,
    type=bool,
    default=True,
    help="Make login interactive",
)
@click.option(
    "--silent",
    is_flag=True,
    type=bool,
    default=False,
    help="Make login non-interactive",
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
    silent: bool,
    auth_token: str,
) -> None:
    """Log into your rapyuta.io account.

    This is the first step to start using the CLI.

    By default, login uses the OAuth 2.0 Device Authorization Flow (RFC 8628):
    the CLI displays a short URL and a user code. Open the URL in any browser,
    authenticate, and enter the code. The CLI receives the token automatically.
    This flow works with MFA/SSO and never exposes your password to the CLI.

    Use --email YOUR_EMAIL to fall back to the email/password (ROPC) flow, which prompts
    for credentials directly.  You can also log in with a pre-existing auth
    token using --auth-token.

    Usage Examples:

        Login using device authorization flow (default)

        $ rio auth login

        Login with a pre-existing auth token

        $ rio auth login --auth-token YOUR_AUTH_TOKEN

        Login using email and password (legacy flow)

        $ rio auth login --email YOUR_EMAIL --password YOUR_PASSWORD

        Non-interactive legacy login with org and project

        $ rio auth login --email YOUR_EMAIL --password YOUR_PASSWORD \\
            --organization YOUR_ORG --project YOUR_PROJECT --silent
    """
    ctx = get_root_context(ctx)
    config = get_config_from_context(ctx)

    interactive = interactive and not silent

    if auth_token:
        config.data["auth_token"] = auth_token
        v2_cli = config.new_v2_client(with_project=False, from_file=False)

        subject = munchify(v2_cli.get_subject(auth_token))

        config.data["email_id"] = subject.data.email
    elif interactive and not (email and password):
        _device_flow_login(config)
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
    if config.exists and interactive:
        click.confirm(
            f"{Symbols.WARNING} Config already exists. Do you want to override"
            " the existing config?",
            abort=True,
        )
    config.save()

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


def _device_flow_login(config: Configuration) -> None:
    """Perform OAuth 2.0 Device Authorization Flow (RFC 8628) login.

    Discovers OIDC endpoints, requests a device code, displays the user code
    and verification URL, then polls for the access token.  Extracts the
    ``rio_token`` and ``email`` claims from the id_token JWT and saves them to *config*.
    """

    try:
        endpoints = discover_oidc_endpoints(config.oidc_server)
    except DeviceFlowError as e:
        click.secho(f"{Symbols.ERROR} {e}", fg=Colors.RED)
        raise SystemExit(1)

    device_auth_endpoint = endpoints.get("device_authorization_endpoint")
    token_endpoint = endpoints.get("token_endpoint")

    if not device_auth_endpoint:
        click.secho(
            f"{Symbols.ERROR} OIDC provider does not support device authorization flow",
            fg=Colors.RED,
        )
        raise SystemExit(1)

    if not token_endpoint:
        click.secho(
            f"{Symbols.ERROR} OIDC provider is missing token_endpoint",
            fg=Colors.RED,
        )
        raise SystemExit(1)

    try:
        device_resp = request_device_code(
            device_auth_endpoint, client_id=config.device_flow_client_id
        )
    except DeviceFlowError as e:
        click.secho(f"{Symbols.ERROR} {e}", fg=Colors.RED)
        raise SystemExit(1)

    display_user_code(
        user_code=device_resp["user_code"],
        verification_uri=device_resp["verification_uri"],
        verification_uri_complete=device_resp.get("verification_uri_complete"),
    )

    try:
        token_resp = poll_for_token(
            token_endpoint=token_endpoint,
            device_code=device_resp["device_code"],
            interval=device_resp.get("interval", 5),
            expires_in=device_resp.get("expires_in", 300),
            client_id=config.device_flow_client_id,
        )
    except DeviceFlowError as e:
        click.secho(f"{Symbols.ERROR} {e}", fg=Colors.RED)
        raise SystemExit(1)

    access_token = token_resp.get("access_token")
    if not access_token:
        click.secho(
            f"{Symbols.ERROR} No access token in device flow response",
            fg=Colors.RED,
        )
        raise SystemExit(1)

    # rio_token and user claims are placed in the id_token by the RIP consent handler
    id_token = token_resp.get("id_token")
    if not id_token:
        click.secho(
            f"{Symbols.ERROR} No id_token in device flow response",
            fg=Colors.RED,
        )
        raise SystemExit(1)

    try:
        claims = decode_jwt_claims(id_token)
    except Exception as e:
        click.secho(f"{Symbols.ERROR} Failed to decode id_token: {e}", fg=Colors.RED)
        raise SystemExit(1)

    rio_token = claims.get("rio_token")
    if not rio_token:
        click.secho(
            f"{Symbols.ERROR} rio_token claim not found in id_token",
            fg=Colors.RED,
        )
        raise SystemExit(1)

    config.data["auth_token"] = rio_token
    email = claims.get("email")
    if email:
        config.data["email_id"] = email

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
from typing import Any, Optional, Tuple

import click
from click_help_colors import HelpColorsCommand
from munch import unmunchify
from yaspin.core import Yaspin

from riocli.config import get_config_from_context
from riocli.constants.colors import Colors
from riocli.constants.symbols import Symbols
from riocli.oauth2.util import sanitize_parameters
from riocli.utils import inspect_with_format
from riocli.utils.spinner import with_spinner


@click.command(
    "update",
    cls=HelpColorsCommand,
    help_headers_color=Colors.YELLOW,
    help_options_color=Colors.GREEN,
)
@click.option(
    "--access-token-strategy",
    type=click.Choice(["opaque", "jwt"]),
    help="The strategy used to generate access tokens. Valid options are opaque and `jwt`.",
)
@click.option(
    "--allowed-cors-origin",
    "allowed_cors_orogins",
    multiple=True,
    type=str,
    help="The list of URLs allowed to make CORS requests. Requires CORS_ENABLED.",
)
@click.option(
    "--audience",
    multiple=True,
    type=str,
    help="The audience this client is allowed to request.",
)
@click.option(
    "--backchannel-logout-callback",
    type=str,
    help="Client URL that will cause the client to log itself out when sent a Logout Token by Hydra.",
)
@click.option(
    "--backchannel-logout-session-required",
    is_flag=True,
    default=False,
    help="Boolean flag specifying whether the client requires that a sid (session ID) Claim be included in the Logout Token.",
)
@click.option(
    "--client-uri",
    type=str,
    help="A URL string of a web page providing information about the client",
)
@click.option(
    "--contact",
    "contacts",
    multiple=True,
    type=str,
    help="A list representing ways to contact people responsible for this client, typically email addresses.",
)
@click.option(
    "--frontchannel-logout-callback",
    type=str,
    help="Client URL that will cause the client to log itself out when rendered in an iframe by Hydra.",
)
@click.option(
    "--frontchannel-logout-session-required",
    is_flag=True,
    default=False,
    help="Boolean flag specifying whether the client requires that a sid (session ID) Claim be included in the Logout Token.",
)
@click.option(
    "--grant-type",
    "grant_types",
    multiple=True,
    default=["authorization_code"],
    type=str,
    help="A list of allowed grant types.",
)
@click.option(
    "--jwks-uri",
    type=str,
    help="Define the URL where the JSON Web Key Set should be fetched from when performing the private_key_jwt client authentication method.",
)
@click.option(
    "--keybase", type=str, help="Keybase username for encrypting client secret."
)
@click.option(
    "--logo-uri", type=str, help="A URL string that references a logo for the client"
)
@click.option(
    "--metadata",
    default="{}",
    type=str,
    help="Metadata is an arbitrary JSON String of your choosing.",
)
@click.option("--name", type=str, help="The client's name.")
@click.option(
    "--owner",
    type=str,
    help="The owner of this client, typically email addresses or a user ID.",
)
@click.option(
    "--pgp-key",
    type=str,
    help="Base64 encoded PGP encryption key for encrypting client secret.",
)
@click.option(
    "--pgp-key-url", type=str, help="PGP encryption key URL for encrypting client secret."
)
@click.option(
    "--policy-uri",
    type=str,
    help="A URL string that points to a human-readable privacy policy document.",
)
@click.option(
    "--post-logout-callback",
    "post_logout_redirect_uris",
    multiple=True,
    type=str,
    help="List of allowed URLs to be redirected to after a logout.",
)
@click.option(
    "--redirect-uri",
    "redirect_uris",
    multiple=True,
    type=str,
    help="List of allowed OAuth2 Redirect URIs.",
)
@click.option(
    "--request-object-signing-alg",
    default="RS256",
    type=str,
    help="Algorithm that must be used for signing Request Objects sent to the OP.",
)
@click.option(
    "--request-uri",
    "request_uris",
    multiple=True,
    type=str,
    help="Array of request_uri values that are pre-registered by the RP for use at the OP.",
)
@click.option(
    "--response-type",
    "response_types",
    multiple=True,
    default=["code"],
    type=str,
    help="A list of allowed response types.",
)
@click.option(
    "--scope", multiple=True, type=str, help="The scope the client is allowed to request."
)
@click.option("--secret", type=str, help="Provide the client's secret.")
@click.option(
    "--sector-identifier-uri",
    type=str,
    help="URL using the https scheme to be used in calculating Pseudonymous Identifiers by the OP.",
)
@click.option(
    "--skip-consent",
    is_flag=True,
    default=False,
    help="Boolean flag specifying whether to skip the consent screen for this client.",
)
@click.option(
    "--skip-logout-consent",
    is_flag=True,
    default=False,
    help="Boolean flag specifying whether to skip the logout consent screen for this client.",
)
@click.option(
    "--subject-type",
    default="public",
    type=click.Choice(["public", "pairwise"]),
    help="A identifier algorithm. Valid values are public and `pairwise`.",
)
@click.option(
    "--token-endpoint-auth-method",
    default="client_secret_basic",
    type=click.Choice(
        ["client_secret_post", "client_secret_basic", "private_key_jwt", "none"]
    ),
    help="Define which authentication method the client may use at the Token Endpoint.",
)
@click.option(
    "--tos-uri",
    type=str,
    help="A URL string that points to a human-readable terms of service document for the client.",
)
@click.argument(
    "client-id",
    type=str,
)
@click.pass_context
@with_spinner(text="Updating OAuth2 Client...")
def update_oauth2_client(
    ctx: click.Context, client_id: str, spinner: Yaspin, **params: dict[str, Any]
):
    params = sanitize_parameters(params)

    try:
        config = get_config_from_context(ctx)
        client = config.new_v2_client(with_project=False)
        oauth2_client = client.update_oauth2_client(client_id=client_id, client=params)
        with spinner.hidden():
            inspect_with_format(unmunchify(oauth2_client), format_type="json")
        spinner.text = click.style("OAuth2 Client updated successfully.", fg=Colors.GREEN)
        spinner.green.ok(Symbols.SUCCESS)
    except Exception as e:
        spinner.text = click.style(
            "Failed to update OAuth2 Client: {}".format(e), fg=Colors.RED
        )
        spinner.red.fail(Symbols.ERROR)
        raise SystemExit(1)


@click.command(
    "update-uri",
    cls=HelpColorsCommand,
    help_headers_color=Colors.YELLOW,
    help_options_color=Colors.GREEN,
)
@click.option(
    "--post-logout-callback",
    "post_logout_redirect_uris",
    multiple=True,
    type=str,
    help="List of allowed URLs to be redirected to after a logout.",
)
@click.option(
    "--redirect-uri",
    "redirect_uris",
    multiple=True,
    type=str,
    help="List of allowed OAuth2 Redirect URIs.",
)
@click.argument(
    "client-id",
    type=str,
)
@click.pass_context
@with_spinner(text="Updating OAuth2 Client...")
def update_oauth2_client_uri(
    ctx: click.Context,
    client_id: str,
    post_logout_redirect_uris: Optional[Tuple[str]],
    redirect_uris: Optional[Tuple[str]],
    spinner: Yaspin,
):
    payload = {
        "redirectURIs": redirect_uris,
        "postLogoutRedirectURIs": post_logout_redirect_uris,
    }

    try:
        config = get_config_from_context(ctx)
        client = config.new_v2_client(with_project=False)
        oauth2_client = client.update_oauth2_client_uris(
            client_id=client_id,
            payload=payload,
        )
        with spinner.hidden():
            inspect_with_format(unmunchify(oauth2_client), format_type="json")
        spinner.text = click.style("OAuth2 Client updated successfully.", fg=Colors.GREEN)
        spinner.green.ok(Symbols.SUCCESS)
    except Exception as e:
        spinner.text = click.style(
            "Failed to update OAuth2 Client: {}".format(e), fg=Colors.RED
        )
        spinner.red.fail(Symbols.ERROR)
        raise SystemExit(1)

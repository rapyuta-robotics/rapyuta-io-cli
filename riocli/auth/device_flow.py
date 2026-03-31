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
import time

import click
import requests

from riocli.constants import Colors


class DeviceFlowError(Exception):
    """Raised when the OAuth 2.0 Device Authorization Flow fails."""

    pass


def discover_oidc_endpoints(oidc_host: str) -> dict:
    """Fetch the OIDC discovery document from *oidc_host* and return it as a dict.

    The discovery document is fetched from
    ``https://{oidc_host}/.well-known/openid-configuration``.
    """
    url = f"{oidc_host}/.well-known/openid-configuration"
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        raise DeviceFlowError(
            f"Failed to fetch OIDC discovery document from {oidc_host}: {e}"
        ) from e


def request_device_code(
    device_authorization_endpoint: str,
    client_id: str,
    scope: str = "openid email",
) -> dict:
    """POST to the device authorization endpoint and return the response dict.

    The response includes ``device_code``, ``user_code``, ``verification_uri``,
    ``expires_in``, and ``interval``.
    """
    try:
        response = requests.post(
            device_authorization_endpoint,
            data={"client_id": client_id, "scope": scope},
            timeout=10,
        )
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        raise DeviceFlowError(f"Failed to request device code: {e}") from e


def poll_for_token(
    token_endpoint: str,
    device_code: str,
    client_id: str,
    interval: int = 5,
    expires_in: int = 300,
) -> dict:
    """Poll *token_endpoint* until the user completes authorization (RFC 8628).

    Returns the token response dict containing at least ``access_token``.

    Raises :class:`DeviceFlowError` on ``access_denied``, expiry, or any
    other unrecoverable error.
    """
    deadline = time.monotonic() + expires_in

    while time.monotonic() < deadline:
        time.sleep(interval)

        try:
            response = requests.post(
                token_endpoint,
                data={
                    "grant_type": "urn:ietf:params:oauth:grant-type:device_code",
                    "client_id": client_id,
                    "device_code": device_code,
                },
                timeout=10,
            )
            data = response.json()
        except (requests.RequestException, ValueError) as e:
            raise DeviceFlowError(f"Token polling request failed: {e}") from e

        error = data.get("error")
        if not error:
            return data

        if error == "authorization_pending":
            continue
        elif error == "slow_down":
            interval += 5
        elif error == "access_denied":
            raise DeviceFlowError("Authorization was denied by the user.")
        elif error in ("expired_token", "invalid_grant"):
            raise DeviceFlowError(
                "Device code expired. Please run `rio auth login` again."
            )
        else:
            description = data.get("error_description", "")
            raise DeviceFlowError(
                f"Unexpected error from token endpoint: {error}: {description}"
            )

    raise DeviceFlowError("Device code expired. Please run `rio auth login` again.")


def display_user_code(
    user_code: str,
    verification_uri: str,
    verification_uri_complete: str | None = None,
) -> None:
    """Print device flow instructions to the terminal."""
    url = verification_uri_complete or verification_uri
    click.echo("")
    click.secho(
        "To complete login, open the following URL in your browser:",
        fg=Colors.CYAN,
    )
    click.secho(f"  {url}", fg=Colors.YELLOW, bold=True)
    click.echo("")
    click.secho("Waiting for authorization...", fg=Colors.CYAN)
    click.launch(url, wait=False)

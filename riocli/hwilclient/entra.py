# Copyright 2026 Rapyuta Robotics
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
"""Microsoft Entra ID access tokens for the HWIL API.

HWIL accepts only Entra tokens (no username/password). There are three ways to get one:

- ``device_code``: MSAL device-code sign-in with the public "HWIL CLI" app. The MSAL token cache (refresh token)
  is stored next to the rio config, mode 0600, and refreshed silently.
- ``az``: ``az account get-access-token`` for a logged-in Azure CLI. az refreshes the token itself.
- ``token``: a ready access token, for CI (``rio hwil login --token``), or the ``RIO_HWIL_TOKEN`` env var.
"""

from __future__ import annotations

import json
import os
import subprocess
import typing

TENANT_ID = "10b7a253-2177-47d2-bd54-ad3233604067"
CLI_CLIENT_ID = "8b166b0d-532b-4aa0-83d0-c6e6353770f3"
SCOPE = "api://hwil-api/HWIL.Access"
AUTHORITY = f"https://login.microsoftonline.com/{TENANT_ID}"
TOKEN_ENV = "RIO_HWIL_TOKEN"
CACHE_FILE = "hwil_token_cache.json"


class HwilAuthError(Exception):
    pass


def cache_path(config_filepath: str) -> str:
    return os.path.join(os.path.dirname(os.path.abspath(config_filepath)), CACHE_FILE)


def _load_cache(path: str):
    import msal

    cache = msal.SerializableTokenCache()
    if os.path.isfile(path):
        with open(path) as f:
            cache.deserialize(f.read())
    return cache


def _save_cache(cache, path: str) -> None:
    if not cache.has_state_changed:
        return
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
    with os.fdopen(fd, "w") as f:
        f.write(cache.serialize())
    os.chmod(path, 0o600)


def _app(cache):
    import msal

    return msal.PublicClientApplication(
        CLI_CLIENT_ID, authority=AUTHORITY, token_cache=cache
    )


def device_code_login(path: str, echo: typing.Callable[[str], None]) -> str:
    """Interactive device-code sign-in. Returns the signed-in account (UPN)."""
    cache = _load_cache(path)
    app = _app(cache)
    flow = app.initiate_device_flow(scopes=[SCOPE])
    if "user_code" not in flow:
        raise HwilAuthError(
            f"could not start device-code sign-in: {flow.get('error_description', flow)}"
        )
    echo(flow["message"])
    result = app.acquire_token_by_device_flow(flow)
    if "access_token" not in result:
        raise HwilAuthError(
            f"sign-in failed: {result.get('error_description', result.get('error'))}"
        )
    _save_cache(cache, path)
    return result.get("id_token_claims", {}).get("preferred_username", "")


def device_code_token(path: str, account: str | None = None) -> str:
    """A valid access token from the cache, refreshed silently when it has expired."""
    cache = _load_cache(path)
    app = _app(cache)
    accounts = app.get_accounts(username=account) if account else app.get_accounts()
    result = app.acquire_token_silent([SCOPE], account=accounts[0]) if accounts else None
    if not result or "access_token" not in result:
        raise HwilAuthError("HWIL session expired. Please login again: rio hwil login")
    _save_cache(cache, path)
    return result["access_token"]


def az_token() -> str:
    try:
        out = subprocess.run(
            ["az", "account", "get-access-token", "--scope", SCOPE, "-o", "json"],
            check=True,
            capture_output=True,
            text=True,
        ).stdout
    except FileNotFoundError as e:
        raise HwilAuthError("az CLI not found") from e
    except subprocess.CalledProcessError as e:
        raise HwilAuthError(f"az could not get a HWIL token: {e.stderr.strip()}") from e
    return json.loads(out)["accessToken"]


def logout(path: str) -> None:
    if os.path.isfile(path):
        os.remove(path)


def token_provider(auth: dict | None, config_filepath: str) -> typing.Callable[[], str]:
    """Function returning a fresh access token for each request, per the stored login mode."""
    env_token = os.environ.get(TOKEN_ENV)
    if env_token:
        return lambda: env_token
    if not auth:
        raise HwilAuthError("not logged in to HWIL")
    mode = auth.get("mode")
    if mode == "device_code":
        path = cache_path(config_filepath)
        return lambda: device_code_token(path, auth.get("account"))
    if mode == "az":
        return az_token
    if mode == "token" and auth.get("token"):
        token = auth["token"]
        return lambda: token
    raise HwilAuthError(f"unknown HWIL login mode {mode!r}; please login again")

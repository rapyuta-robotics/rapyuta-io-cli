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

HWIL accepts only Entra tokens (no username/password). Ways to get one:

- ``browser`` (default): MSAL interactive sign-in with the public "HWIL CLI" app: authorization code + PKCE, the
  browser returns to a loopback ``http://localhost:<random port>``. The MSAL token cache (refresh token) is stored
  next to the rio config, mode 0600, and refreshed silently.
- ``device_code`` (opt-in): same app and cache, for boxes without a browser. The Rapyuta tenant's Conditional
  Access blocks this flow (it is the phishable one), so there it fails with a clear message; use ``az`` instead.
- ``az``: ``az account get-access-token`` for a logged-in Azure CLI. az refreshes the token itself.
- CI: the ``RIO_HWIL_TOKEN`` env var, read per invocation and never written to the config (the config file is
  exactly what was stolen in the 2026-11 incident).
"""

from __future__ import annotations

import json
import os
import subprocess
import tempfile
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
    """One token cache per rio config file: two RIO_CONFIG files in one directory must not share (or log out)
    each other's session."""
    full = os.path.abspath(config_filepath)
    return os.path.join(os.path.dirname(full), f"{os.path.basename(full)}.{CACHE_FILE}")


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
    # a fresh profile has no config directory yet (sign-in runs before the config is saved)
    directory = os.path.dirname(os.path.abspath(path))
    os.makedirs(directory, mode=0o700, exist_ok=True)
    # write a private temp file and swap it in, so a concurrent reader never sees a truncated cache
    fd, tmp = tempfile.mkstemp(prefix=".hwil_token_cache.", dir=directory)
    try:
        with os.fdopen(fd, "w") as f:
            f.write(cache.serialize())
        os.chmod(tmp, 0o600)
        os.replace(tmp, path)
    except BaseException:
        if os.path.exists(tmp):
            os.unlink(tmp)
        raise


def _app(cache):
    import msal

    return msal.PublicClientApplication(
        CLI_CLIENT_ID, authority=AUTHORITY, token_cache=cache
    )


DEVICE_CODE_BLOCKED = (
    "device-code sign-in is blocked by tenant policy (Conditional Access); "
    "use the default browser login (`rio hwil login`) or `rio hwil login --az`"
)


def _account(result: dict) -> str:
    return (result.get("id_token_claims") or {}).get("preferred_username", "")


def browser_login(path: str) -> str:
    """Interactive browser sign-in (auth code + PKCE, loopback redirect). Returns the signed-in account (UPN)."""
    cache = _load_cache(path)
    app = _app(cache)
    result = app.acquire_token_interactive(scopes=[SCOPE], prompt="select_account")
    if "access_token" not in result:
        raise HwilAuthError(
            f"sign-in failed: {result.get('error_description', result.get('error'))}"
        )
    _save_cache(cache, path)
    return _account(result)


def device_code_login(path: str, echo: typing.Callable[[str], None]) -> str:
    """Device-code sign-in (opt-in, for boxes without a browser). Returns the signed-in account (UPN)."""
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
        # AADSTS53003: blocked by Conditional Access
        if 53003 in (result.get("error_codes") or []) or "AADSTS53003" in str(
            result.get("error_description")
        ):
            raise HwilAuthError(DEVICE_CODE_BLOCKED)
        raise HwilAuthError(
            f"sign-in failed: {result.get('error_description', result.get('error'))}"
        )
    _save_cache(cache, path)
    return _account(result)


def cached_token(path: str, account: str | None = None) -> str:
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


def token_provider(
    auth: dict | None, config_filepath: str, use_env: bool = True
) -> typing.Callable[[], str]:
    """Function returning a fresh access token for each request, per the stored login mode.

    RIO_HWIL_TOKEN overrides the stored mode for ordinary commands; login passes use_env=False so it validates the
    mode it is about to save."""
    env_token = os.environ.get(TOKEN_ENV) if use_env else None
    if env_token:
        return lambda: env_token
    if not auth:
        raise HwilAuthError("not logged in to HWIL")
    mode = auth.get("mode")
    if mode in ("browser", "device_code"):  # same MSAL cache, refreshed silently
        path = cache_path(config_filepath)
        return lambda: cached_token(path, auth.get("account"))
    if mode == "az":
        return az_token
    raise HwilAuthError(f"unknown HWIL login mode {mode!r}; please login again")

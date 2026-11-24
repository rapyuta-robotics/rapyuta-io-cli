"""Regressions for the rapyuta-io-cli#627 review (first-run sign-in, token cache, proxies, login mode)."""

import json
import os
from unittest.mock import MagicMock, patch

from click.testing import CliRunner

from riocli.config import Configuration
from riocli.hwil.login import login
from riocli.hwilclient import entra


def test_cache_is_written_on_a_fresh_profile(tmp_path):
    """Sign-in writes the MSAL cache before the config is saved: the directory may not exist yet."""
    path = tmp_path / "new-profile" / "config.json.hwil_token_cache.json"
    cache = MagicMock(has_state_changed=True)
    cache.serialize.return_value = "{}"
    entra._save_cache(cache, str(path))
    assert path.read_text() == "{}"
    assert oct(path.stat().st_mode & 0o777) == "0o600"
    assert [p.name for p in path.parent.iterdir()] == [
        path.name
    ]  # no temp file left behind


def test_each_config_file_has_its_own_token_cache(tmp_path):
    a = entra.cache_path(str(tmp_path / "config.json"))
    b = entra.cache_path(str(tmp_path / "staging.json"))
    assert a != b and os.path.dirname(a) == os.path.dirname(b)


def test_loopback_hwil_never_goes_through_a_proxy(monkeypatch):
    from riocli.hwilclient.client import Client

    monkeypatch.setenv("HTTP_PROXY", "http://proxy.example:3128")
    monkeypatch.setenv("NO_PROXY", "corp.example")
    monkeypatch.delenv("no_proxy", raising=False)
    Client(token_provider=lambda: "t", hwil_host="http://127.0.0.1:8000")
    import requests

    assert requests.utils.should_bypass_proxies("http://127.0.0.1:8000/device/", None)
    assert "corp.example" in os.environ["NO_PROXY"]


def test_login_az_validates_az_even_when_an_env_token_is_exported(tmp_path, monkeypatch):
    cfg = tmp_path / "config.json"
    cfg.write_text(json.dumps({"auth_token": "rio"}))
    monkeypatch.setenv("RIO_CONFIG", str(cfg))
    monkeypatch.setenv(entra.TOKEN_ENV, "eyJ.env.tok")
    with (
        patch("riocli.hwil.login.HwilClient") as hc,
        patch(
            "riocli.hwilclient.entra.subprocess.run", side_effect=FileNotFoundError("az")
        ),
    ):
        CliRunner().invoke(login, ["--az"], obj=Configuration())
        provider = hc.call_args.kwargs["token_provider"]
        # the provider handed to the validation call is az's, not the env token's
        try:
            token = provider()
        except Exception:
            token = None
    assert token != "eyJ.env.tok"

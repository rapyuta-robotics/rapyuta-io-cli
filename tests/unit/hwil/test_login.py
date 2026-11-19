"""rio hwil login: Entra ID only (device code, az, or a ready token); never a username/password."""

import json
import os
import stat
from unittest.mock import MagicMock, patch

import pytest
from click.testing import CliRunner

from riocli.config import Configuration
from riocli.exceptions import HwilLoggedOut
from riocli.hwil.login import login, logout
from riocli.hwilclient import entra


@pytest.fixture
def cfg(tmp_path, monkeypatch):
    path = tmp_path / "config.json"
    path.write_text(json.dumps({"auth_token": "rio", "hwil_auth_token": "YW5zaWJsZTp4"}))
    monkeypatch.setenv("RIO_CONFIG", str(path))
    monkeypatch.delenv(entra.TOKEN_ENV, raising=False)
    return path


def invoke(cmd, args):
    return CliRunner().invoke(cmd, args, obj=Configuration())


def test_token_is_never_persisted(cfg, monkeypatch):
    """M1: no --token flag; CI uses RIO_HWIL_TOKEN per invocation and the config never holds a token."""
    r = invoke(login, ["--token", "eyJ.test.tok"])
    assert r.exit_code != 0 and "no such option" in r.output.lower()
    monkeypatch.setenv(entra.TOKEN_ENV, "eyJ.env.tok")
    assert (
        Configuration().new_hwil_client()._get_auth_header()["Authorization"]
        == "Bearer eyJ.env.tok"
    )
    assert "eyJ" not in cfg.read_text()


def test_az_login_drops_basic_credential(cfg):
    with patch("riocli.hwil.login.HwilClient"):
        r = invoke(login, ["--az"])
    assert r.exit_code == 0, r.output
    data = json.loads(cfg.read_text())
    assert data["hwil_auth"] == {"mode": "az"} and "hwil_auth_token" not in data


def test_login_with_az(cfg):
    with (
        patch("riocli.hwil.login.HwilClient"),
        patch("riocli.hwilclient.entra.subprocess.run") as run,
    ):
        run.return_value.stdout = json.dumps({"accessToken": "az-tok"})
        r = invoke(login, ["--az"])
        assert r.exit_code == 0, r.output
        assert entra.token_provider({"mode": "az"}, str(cfg))() == "az-tok"
    assert "--scope" in run.call_args.args[0] and entra.SCOPE in run.call_args.args[0]
    assert json.loads(cfg.read_text())["hwil_auth"] == {"mode": "az"}


def test_device_code_login_caches_privately_and_refreshes_silently(cfg):
    app = MagicMock()
    app.initiate_device_flow.return_value = {
        "user_code": "ABC",
        "message": "go to https://microsoft.com/devicelogin",
    }
    app.acquire_token_by_device_flow.return_value = {
        "access_token": "t1",
        "id_token_claims": {"preferred_username": "a@x.com"},
    }
    app.get_accounts.return_value = [{"username": "a@x.com"}]
    app.acquire_token_silent.return_value = {"access_token": "t2"}
    cache = MagicMock()
    cache.has_state_changed = True
    cache.serialize.return_value = "{}"
    with (
        patch("riocli.hwilclient.entra._app", return_value=app),
        patch("riocli.hwilclient.entra._load_cache", return_value=cache),
        patch("riocli.hwil.login.HwilClient") as client,
    ):
        r = invoke(login, [])
        assert r.exit_code == 0, r.output
        assert "devicelogin" in r.output and "a@x.com" in r.output
        assert client.call_args.kwargs["token_provider"]() == "t2"
    assert app.initiate_device_flow.call_args.kwargs["scopes"] == [entra.SCOPE]
    assert json.loads(cfg.read_text())["hwil_auth"] == {
        "mode": "device_code",
        "account": "a@x.com",
    }
    cache_file = entra.cache_path(str(cfg))
    assert stat.S_IMODE(os.stat(cache_file).st_mode) == 0o600


def test_failed_validation_does_not_save(cfg):
    with patch("riocli.hwil.login.HwilClient") as client:
        client.return_value.list_devices.side_effect = Exception("401")
        r = invoke(login, ["--az"])
    assert r.exit_code == 1 and "hwil_auth" not in json.loads(cfg.read_text())


def test_legacy_basic_credential_is_logged_out(cfg):
    with pytest.raises(HwilLoggedOut):
        Configuration().new_hwil_client()


def test_env_token_wins_and_header_is_bearer(cfg, monkeypatch):
    monkeypatch.setenv(entra.TOKEN_ENV, "env-tok")
    client = Configuration().new_hwil_client()
    assert client._get_auth_header()["Authorization"] == "Bearer env-tok"


def test_logout_removes_cache_and_login(cfg):
    path = entra.cache_path(str(cfg))
    open(path, "w").write("{}")
    d = json.loads(cfg.read_text())
    d["hwil_auth"] = {"mode": "az"}
    cfg.write_text(json.dumps(d))
    r = invoke(logout, [])
    assert r.exit_code == 0 and not os.path.exists(path)
    assert "hwil_auth" not in json.loads(
        cfg.read_text()
    ) and "hwil_auth_token" not in json.loads(cfg.read_text())

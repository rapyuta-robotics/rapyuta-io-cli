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

"""Tests for the standalone ``rio-ssh-ensure-cert`` core (riocli.ssh_ensure_cert)."""

from __future__ import annotations

import json
import subprocess
from unittest.mock import MagicMock, patch

import pytest

from riocli import ssh_ensure_cert as core

_PROJECT = "project-aaaa"
_STATE_NAME = "rio-ssh-cert.project"
_LOG_NAME = "rio-ssh-cert.log"
_CERT_NAME = "rio_ed25519-cert.pub"


@pytest.fixture(autouse=True)
def _clear_rio_config(monkeypatch):
    """Ensure an ambient RIO_CONFIG does not leak into project-id reads."""
    monkeypatch.delenv("RIO_CONFIG", raising=False)


def _sign_writes(cert_path, content="signed-cert\n"):
    """Return a sign_fn mock that writes *content* to *cert_path*."""

    def _sign():
        cert_path.write_text(content)

    return MagicMock(side_effect=_sign)


class TestResolveMargin:
    def test_default_when_unset(self, monkeypatch):
        monkeypatch.delenv(core._MARGIN_ENV, raising=False)
        assert core.resolve_margin(None) == core._DEFAULT_MARGIN

    def test_flag_takes_precedence(self, monkeypatch):
        monkeypatch.setenv(core._MARGIN_ENV, "99")
        assert core.resolve_margin(45) == 45

    def test_env_var_used(self, monkeypatch):
        monkeypatch.setenv(core._MARGIN_ENV, "120")
        assert core.resolve_margin(None) == 120

    def test_negative_flag_falls_back_to_default(self):
        assert core.resolve_margin(-5) == core._DEFAULT_MARGIN

    def test_non_numeric_env_falls_back_to_default(self, monkeypatch):
        monkeypatch.setenv(core._MARGIN_ENV, "abc")
        assert core.resolve_margin(None) == core._DEFAULT_MARGIN

    def test_negative_env_falls_back_to_default(self, monkeypatch):
        monkeypatch.setenv(core._MARGIN_ENV, "-10")
        assert core.resolve_margin(None) == core._DEFAULT_MARGIN

    @pytest.mark.parametrize("margin", [0, 20, 300])
    def test_passthrough(self, margin):
        assert core.resolve_margin(margin) == margin


class TestStatePersistence:
    def test_round_trip(self, tmp_path):
        state = tmp_path / _STATE_NAME
        assert core.save_project(state, "proj-1") is True
        assert core.read_saved_project(state) == "proj-1"

    def test_read_missing_returns_none(self, tmp_path):
        assert core.read_saved_project(tmp_path / "absent") is None

    def test_save_is_atomic_no_leftover_tmp(self, tmp_path):
        state = tmp_path / _STATE_NAME
        core.save_project(state, "proj-1")
        assert not (tmp_path / f"{_STATE_NAME}.tmp").exists()


class TestCertValid:
    def test_missing_file_is_invalid(self, tmp_path):
        assert core.cert_valid(tmp_path / "absent") is False

    def test_garbage_file_is_invalid(self, tmp_path):
        cert = tmp_path / _CERT_NAME
        cert.write_text("not a certificate")
        assert core.cert_valid(cert) is False

    def test_real_certificate_validity_and_margin(self, ssh_dir):
        # Sign the fixture's rio_ed25519 key with a throwaway CA, valid +5m.
        ca = ssh_dir / "ca"
        subprocess.run(
            ["ssh-keygen", "-t", "ed25519", "-f", str(ca), "-N", "", "-q"],
            check=True,
            capture_output=True,
        )
        subprocess.run(
            [
                "ssh-keygen",
                "-s",
                str(ca),
                "-I",
                "test-id",
                "-n",
                "rr",
                "-V",
                "+5m",
                str(ssh_dir / "rio_ed25519.pub"),
            ],
            check=True,
            capture_output=True,
        )
        cert = ssh_dir / _CERT_NAME

        assert core.cert_valid(cert) is True
        # A margin wider than the 5-minute lifetime makes it "expired".
        assert core.cert_valid(cert, margin=10_000) is False


class TestReadProjectId:
    def test_reads_project_id(self, tmp_path):
        (tmp_path / "config.json").write_text(json.dumps({"project_id": _PROJECT}))
        assert core._read_project_id(tmp_path) == _PROJECT

    def test_missing_file_returns_none(self, tmp_path):
        assert core._read_project_id(tmp_path) is None

    def test_malformed_json_returns_none(self, tmp_path):
        (tmp_path / "config.json").write_text("{not json")
        assert core._read_project_id(tmp_path) is None

    def test_absent_key_returns_none(self, tmp_path):
        (tmp_path / "config.json").write_text(json.dumps({"other": 1}))
        assert core._read_project_id(tmp_path) is None

    def test_rio_config_override(self, tmp_path, monkeypatch):
        override = tmp_path / "elsewhere.json"
        override.write_text(json.dumps({"project_id": "from-override"}))
        monkeypatch.setenv("RIO_CONFIG", str(override))
        # config_dir has no config.json; the override must win.
        assert core._read_project_id(tmp_path) == "from-override"


class TestEnsureCertificate:
    def _cert(self, tmp_path):
        return tmp_path / _CERT_NAME

    def test_no_project_id_exits_1(self, tmp_path):
        sign = MagicMock()
        rc = core.ensure_certificate(
            cert_path=self._cert(tmp_path),
            config_dir=tmp_path,
            project_id=None,
            sign_fn=sign,
            margin=0,
        )
        assert rc == 1
        sign.assert_not_called()
        assert (tmp_path / _LOG_NAME).exists()

    @patch("riocli.ssh_ensure_cert.cert_valid", return_value=True)
    def test_fast_path_skips_renewal(self, _valid, tmp_path):
        (tmp_path / _STATE_NAME).write_text(_PROJECT + "\n")
        sign = MagicMock()
        rc = core.ensure_certificate(
            cert_path=self._cert(tmp_path),
            config_dir=tmp_path,
            project_id=_PROJECT,
            sign_fn=sign,
            margin=20,
        )
        assert rc == 0
        sign.assert_not_called()

    @patch("riocli.ssh_ensure_cert.cert_valid", return_value=True)
    def test_fast_path_misses_without_saved_project(self, _valid, tmp_path):
        cert = self._cert(tmp_path)
        sign = _sign_writes(cert)
        rc = core.ensure_certificate(
            cert_path=cert,
            config_dir=tmp_path,
            project_id=_PROJECT,
            sign_fn=sign,
            margin=20,
        )
        assert rc == 0
        sign.assert_called_once()
        assert (tmp_path / _STATE_NAME).read_text().strip() == _PROJECT

    @patch(
        "riocli.ssh_ensure_cert.cert_valid",
        side_effect=[False, False, True],
    )
    def test_renews_when_cert_invalid(self, _valid, tmp_path):
        cert = self._cert(tmp_path)
        sign = _sign_writes(cert)
        rc = core.ensure_certificate(
            cert_path=cert,
            config_dir=tmp_path,
            project_id=_PROJECT,
            sign_fn=sign,
            margin=20,
        )
        assert rc == 0
        sign.assert_called_once()
        assert (tmp_path / _STATE_NAME).read_text().strip() == _PROJECT

    @patch(
        "riocli.ssh_ensure_cert.cert_valid",
        side_effect=[True, True, True],
    )
    def test_renews_when_project_changed(self, _valid, tmp_path):
        (tmp_path / _STATE_NAME).write_text("project-old\n")
        cert = self._cert(tmp_path)
        sign = _sign_writes(cert)
        rc = core.ensure_certificate(
            cert_path=cert,
            config_dir=tmp_path,
            project_id="project-new",
            sign_fn=sign,
            margin=20,
        )
        assert rc == 0
        sign.assert_called_once()
        assert (tmp_path / _STATE_NAME).read_text().strip() == "project-new"

    @patch(
        "riocli.ssh_ensure_cert.cert_valid",
        side_effect=[False, False],
    )
    def test_signing_failure_exits_1(self, _valid, tmp_path):
        sign = MagicMock(side_effect=RuntimeError("boom"))
        rc = core.ensure_certificate(
            cert_path=self._cert(tmp_path),
            config_dir=tmp_path,
            project_id=_PROJECT,
            sign_fn=sign,
            margin=20,
        )
        assert rc == 1
        assert not (tmp_path / _STATE_NAME).exists()
        assert "renewal failed" in (tmp_path / _LOG_NAME).read_text()

    @patch(
        "riocli.ssh_ensure_cert.cert_valid",
        side_effect=[False, False, False],
    )
    def test_signing_success_but_invalid_cert_exits_1(self, _valid, tmp_path):
        cert = self._cert(tmp_path)
        sign = _sign_writes(cert)
        rc = core.ensure_certificate(
            cert_path=cert,
            config_dir=tmp_path,
            project_id=_PROJECT,
            sign_fn=sign,
            margin=20,
        )
        assert rc == 1
        sign.assert_called_once()
        assert not (tmp_path / _STATE_NAME).exists()


class TestMain:
    @patch("riocli.ssh_ensure_cert.cert_valid", return_value=True)
    def test_fast_path_no_sdk_import(self, _valid, tmp_path):
        """Fast path must never call the sign_fn (which would import the SDK)."""
        (tmp_path / "config.json").write_text(json.dumps({"project_id": _PROJECT}))
        (tmp_path / _STATE_NAME).write_text(_PROJECT + "\n")
        sign = MagicMock()

        with (
            patch("riocli.ssh_ensure_cert._config_dir", return_value=tmp_path),
            patch("riocli.ssh_ensure_cert._build_sign_fn", return_value=sign),
        ):
            rc = core.main([])

        assert rc == 0
        # Fast path must never construct the (heavy) signing callable's client.
        sign.assert_not_called()

    def test_no_project_id_exits_1(self, tmp_path):
        with patch("riocli.ssh_ensure_cert._config_dir", return_value=tmp_path):
            rc = core.main([])
        assert rc == 1

    @patch("riocli.ssh_ensure_cert.cert_valid", return_value=True)
    def test_margin_flag_passed_through(self, mock_valid, tmp_path):
        (tmp_path / "config.json").write_text(json.dumps({"project_id": _PROJECT}))
        (tmp_path / _STATE_NAME).write_text(_PROJECT + "\n")

        with (
            patch("riocli.ssh_ensure_cert._config_dir", return_value=tmp_path),
            patch("riocli.ssh_ensure_cert._build_sign_fn", return_value=MagicMock()),
        ):
            rc = core.main(["--margin", "60"])

        assert rc == 0
        assert mock_valid.call_args.kwargs.get("margin") == 60

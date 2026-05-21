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

"""Tests for certificate parsing and writing functions."""

from __future__ import annotations

import subprocess
import time
from datetime import datetime, timezone
from unittest.mock import MagicMock, patch

from riocli.ssh.certificate import (
    _FOREVER,
    _load_certificate,
    format_cert_expiry,
    is_cert_valid,
    parse_cert_valid_before,
    write_certificate,
)


class TestCertificateParsing:
    """Tests for certificate parsing functions using the cryptography library."""

    def _mock_cert(self, valid_before: int) -> MagicMock:
        """Return a mock SSHCertificate with the given valid_before."""
        from cryptography.hazmat.primitives.serialization.ssh import SSHCertificate

        cert = MagicMock(spec=SSHCertificate)
        cert.valid_before = valid_before
        return cert

    @patch("riocli.ssh.certificate._load_certificate")
    def test_parse_cert_valid_before_success(self, mock_load, tmp_path):
        """parse_cert_valid_before returns a datetime from valid_before."""
        future_ts = int(time.time()) + 3600
        mock_load.return_value = self._mock_cert(future_ts)

        cert_path = tmp_path / "test-cert.pub"
        cert_path.write_text("fake cert data")

        dt = parse_cert_valid_before(cert_path)
        assert dt is not None
        assert abs(dt.timestamp() - future_ts) < 1
        mock_load.assert_called_once_with(cert_path)

    @patch("riocli.ssh.certificate._load_certificate")
    def test_parse_cert_valid_before_forever(self, mock_load, tmp_path):
        """Handle the 'forever' sentinel (0xFFFFFFFFFFFFFFFF)."""
        mock_load.return_value = self._mock_cert(_FOREVER)

        cert_path = tmp_path / "test-cert.pub"
        cert_path.write_text("fake cert data")

        dt = parse_cert_valid_before(cert_path)
        assert dt is not None
        assert dt == datetime.max.replace(tzinfo=timezone.utc)

    @patch("riocli.ssh.certificate._load_certificate")
    def test_parse_cert_valid_before_load_failure(self, mock_load, tmp_path):
        """Return None when _load_certificate fails."""
        mock_load.return_value = None

        cert_path = tmp_path / "test-cert.pub"
        cert_path.write_text("not a certificate")

        assert parse_cert_valid_before(cert_path) is None

    def test_parse_cert_missing_file(self, tmp_path):
        cert_path = tmp_path / "nonexistent-cert.pub"
        assert parse_cert_valid_before(cert_path) is None

    @patch("riocli.ssh.certificate._load_certificate")
    def test_is_cert_valid_true(self, mock_load, tmp_path):
        future_ts = int(time.time()) + 3600
        mock_load.return_value = self._mock_cert(future_ts)

        cert_path = tmp_path / "test-cert.pub"
        cert_path.write_text("fake cert data")

        assert is_cert_valid(cert_path) is True

    @patch("riocli.ssh.certificate._load_certificate")
    def test_is_cert_valid_expired(self, mock_load, tmp_path):
        past_ts = int(time.time()) - 3600
        mock_load.return_value = self._mock_cert(past_ts)

        cert_path = tmp_path / "test-cert.pub"
        cert_path.write_text("fake cert data")

        assert is_cert_valid(cert_path) is False

    def test_is_cert_valid_missing_file(self, tmp_path):
        cert_path = tmp_path / "nonexistent-cert.pub"
        assert is_cert_valid(cert_path) is False

    @patch("riocli.ssh.certificate._load_certificate")
    def test_is_cert_valid_bad_cert(self, mock_load, tmp_path):
        """is_cert_valid returns False when certificate can't be loaded."""
        mock_load.return_value = None

        cert_path = tmp_path / "cert.pub"
        cert_path.write_text("not a cert")

        assert is_cert_valid(cert_path) is False

    @patch("riocli.ssh.certificate._load_certificate")
    def test_format_cert_expiry(self, mock_load, tmp_path):
        future_ts = int(time.time()) + 3600
        mock_load.return_value = self._mock_cert(future_ts)

        cert_path = tmp_path / "test-cert.pub"
        cert_path.write_text("fake cert data")

        result = format_cert_expiry(cert_path)
        assert result is not None
        assert "T" in result

    def test_format_cert_expiry_missing(self, tmp_path):
        cert_path = tmp_path / "nonexistent-cert.pub"
        assert format_cert_expiry(cert_path) is None

    @patch("riocli.ssh.certificate._load_certificate")
    def test_format_cert_expiry_bad_cert(self, mock_load, tmp_path):
        mock_load.return_value = None

        cert_path = tmp_path / "cert.pub"
        cert_path.write_text("not a cert")

        assert format_cert_expiry(cert_path) is None

    def test_load_certificate_with_non_cert(self, tmp_path):
        """_load_certificate returns None for a plain SSH public key."""
        ssh_dir = tmp_path / "keys"
        ssh_dir.mkdir()
        # Generate a real key pair
        subprocess.run(
            ["ssh-keygen", "-t", "ed25519", "-f", str(ssh_dir / "k"), "-N", "", "-q"],
            check=True,
            capture_output=True,
        )
        pub = ssh_dir / "k.pub"
        assert _load_certificate(pub) is None

    def test_load_certificate_with_garbage(self, tmp_path):
        """_load_certificate returns None for garbage data."""
        cert_path = tmp_path / "garbage.pub"
        cert_path.write_text("this is not an SSH certificate")
        assert _load_certificate(cert_path) is None

    def test_load_certificate_missing_file(self, tmp_path):
        cert_path = tmp_path / "missing.pub"
        assert _load_certificate(cert_path) is None


class TestWriteCertificate:
    """Tests for write_certificate()."""

    def test_writes_with_newline(self, tmp_path):
        cert_path = tmp_path / "test-cert.pub"
        write_certificate(cert_path, "cert-content")
        assert cert_path.read_text() == "cert-content\n"

    def test_sets_permissions(self, tmp_path):
        cert_path = tmp_path / "test-cert.pub"
        write_certificate(cert_path, "cert-content")
        assert oct(cert_path.stat().st_mode & 0o777) == "0o644"

    def test_overwrites_existing_cert(self, tmp_path):
        cert_path = tmp_path / "test-cert.pub"
        write_certificate(cert_path, "old-cert")
        write_certificate(cert_path, "new-cert")
        assert cert_path.read_text() == "new-cert\n"

    def test_creates_file_if_missing(self, tmp_path):
        cert_path = tmp_path / "brand-new-cert.pub"
        assert not cert_path.exists()
        write_certificate(cert_path, "fresh-cert")
        assert cert_path.exists()
        assert cert_path.read_text() == "fresh-cert\n"

    def test_preserves_cert_content_exactly(self, tmp_path):
        cert_content = "ssh-ed25519-cert-v01@openssh.com AAAA+/== user@host"
        cert_path = tmp_path / "exact-cert.pub"
        write_certificate(cert_path, cert_content)
        assert cert_path.read_text() == cert_content + "\n"

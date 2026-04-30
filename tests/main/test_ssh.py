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

"""Unit, integration, and E2E tests for the ``rio ssh`` command.

Tests cover key generation, certificate parsing, agent wire-format,
SDK signing call, error paths, CLI flag behaviour, component
integration, and full end-to-end flows.
"""

from __future__ import annotations

import base64
import os
import struct
import time
from datetime import timezone
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from click.testing import CliRunner
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

from riocli.ssh.certificate import (
    format_cert_expiry,
    is_cert_valid,
    parse_cert_valid_before,
    write_certificate,
)
from riocli.ssh.keys import (
    RIO_KEY_NAME,
    ensure_rio_key_pair,
    get_rio_key_paths,
    read_public_key,
)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _generate_test_key_pair(ssh_dir: Path) -> tuple[Path, Path]:
    """Generate a real ed25519 key pair in *ssh_dir* for testing."""
    key = Ed25519PrivateKey.generate()

    priv_path = ssh_dir / "rio_ed25519"
    pub_path = ssh_dir / "rio_ed25519.pub"

    priv_path.write_bytes(
        key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.OpenSSH,
            encryption_algorithm=serialization.NoEncryption(),
        )
    )
    priv_path.chmod(0o600)

    pub_path.write_bytes(
        key.public_key().public_bytes(
            encoding=serialization.Encoding.OpenSSH,
            format=serialization.PublicFormat.OpenSSH,
        )
        + b" rio-ssh\n"
    )
    pub_path.chmod(0o644)

    return priv_path, pub_path


def _make_dummy_cert(
    valid_before_unix: int,
    cert_type: bytes = b"ssh-ed25519-cert-v01@openssh.com",
    serial: int = 1234567890,
    cert_kind: int = 1,
    valid_after_unix: int = 0,
    pk_bytes: bytes | None = None,
) -> str:
    """Build a minimal SSH certificate with given parameters.

    The certificate is structurally valid for parsing but not
    cryptographically signed.
    """
    nonce = b"\x00" * 32
    pk = pk_bytes or (b"\x00" * 32)  # fake ed25519 public key

    from riocli.ssh.certificate import _CERT_PK_FIELDS

    num_fields = _CERT_PK_FIELDS.get(cert_type, 1)

    blob = b""
    blob += struct.pack(">I", len(cert_type)) + cert_type
    blob += struct.pack(">I", len(nonce)) + nonce
    for _ in range(num_fields):
        blob += struct.pack(">I", len(pk)) + pk
    blob += struct.pack(">Q", serial)
    blob += struct.pack(">I", cert_kind)
    blob += struct.pack(">I", 0) + b""  # key_id (empty)
    blob += struct.pack(">I", 0)  # valid_principals (empty)
    blob += struct.pack(">Q", valid_after_unix)
    blob += struct.pack(">Q", valid_before_unix)

    b64 = base64.b64encode(blob).decode()
    return f"{cert_type.decode()} {b64} test"


def _mock_v2_client(certificate: str = "ssh-ed25519-cert-v01@openssh.com AAAA..."):
    """Return a mock v2 client with sign_ssh_public_key wired up."""
    client = MagicMock()
    response = MagicMock()
    response.certificate = certificate
    client.sign_ssh_public_key.return_value = response
    return client


def _fake_agent_socket(response_type: int = 6):
    """Return a mock socket that replies with *response_type*.

    Default response_type=6 is SSH_AGENT_SUCCESS.
    """
    sock = MagicMock()
    resp_bytes = struct.pack(">IB", 1, response_type)
    sock.recv.side_effect = [resp_bytes[:4], resp_bytes[4:]]
    return sock


# ---------------------------------------------------------------------------
# keys.py – unit tests
# ---------------------------------------------------------------------------


class TestKeyPaths:
    """Tests for get_rio_key_paths()."""

    def test_default_paths(self, tmp_path):
        priv, pub, cert = get_rio_key_paths(tmp_path)
        assert priv == tmp_path / "rio_ed25519"
        assert pub == tmp_path / "rio_ed25519.pub"
        assert cert == tmp_path / "rio_ed25519-cert.pub"

    def test_default_ssh_dir(self):
        """Without an override, paths should be under ~/.ssh/."""
        priv, pub, cert = get_rio_key_paths()
        expected = Path.home() / ".ssh"
        assert priv.parent == expected
        assert pub.parent == expected
        assert cert.parent == expected

    def test_key_name_constant(self, tmp_path):
        """Paths use the RIO_KEY_NAME constant."""
        priv, pub, cert = get_rio_key_paths(tmp_path)
        assert priv.name == RIO_KEY_NAME
        assert pub.name == f"{RIO_KEY_NAME}.pub"
        assert cert.name == f"{RIO_KEY_NAME}-cert.pub"


class TestEnsureRioKeyPair:
    """Tests for ensure_rio_key_pair()."""

    def test_generates_key_pair_when_missing(self, tmp_path):
        ssh_dir = tmp_path / ".ssh"
        ssh_dir.mkdir()
        priv, pub, cert, generated = ensure_rio_key_pair(ssh_dir)

        assert generated is True
        assert priv.is_file()
        assert pub.is_file()
        assert pub.read_text().strip().startswith("ssh-ed25519 ")
        assert pub.read_text().strip().endswith("rio-ssh")
        # Private key permissions
        assert oct(priv.stat().st_mode & 0o777) == "0o600"

    def test_reuses_existing_key_pair(self, tmp_path):
        ssh_dir = tmp_path / ".ssh"
        ssh_dir.mkdir()
        _generate_test_key_pair(ssh_dir)
        priv, pub, cert, generated = ensure_rio_key_pair(ssh_dir)

        assert generated is False
        assert priv.is_file()
        assert pub.is_file()

    def test_creates_ssh_dir_if_missing(self, tmp_path):
        ssh_dir = tmp_path / ".ssh"
        # ssh_dir does NOT exist yet
        priv, pub, cert, generated = ensure_rio_key_pair(ssh_dir)

        assert generated is True
        assert ssh_dir.is_dir()
        assert oct(ssh_dir.stat().st_mode & 0o777) == "0o700"

    def test_deletes_stale_cert_on_new_key_pair(self, tmp_path):
        """When a new key pair is generated, any leftover cert must be removed."""
        ssh_dir = tmp_path / ".ssh"
        ssh_dir.mkdir()
        cert = ssh_dir / "rio_ed25519-cert.pub"
        cert.write_text("stale-cert-for-old-key")

        priv, pub, returned_cert, generated = ensure_rio_key_pair(ssh_dir)

        assert generated is True
        assert not cert.exists(), "Stale cert should have been deleted"

    def test_only_private_key_exists_regenerates(self, tmp_path):
        """If only the private key exists (no public), regenerate both."""
        ssh_dir = tmp_path / ".ssh"
        ssh_dir.mkdir()
        priv_path = ssh_dir / "rio_ed25519"
        priv_path.write_text("orphaned-private-key")

        priv, pub, cert, generated = ensure_rio_key_pair(ssh_dir)

        assert generated is True
        assert priv.is_file()
        assert pub.is_file()
        # Should be overwritten with a valid key
        assert pub.read_text().strip().startswith("ssh-ed25519 ")

    def test_only_public_key_exists_regenerates(self, tmp_path):
        """If only the public key exists (no private), regenerate both."""
        ssh_dir = tmp_path / ".ssh"
        ssh_dir.mkdir()
        pub_path = ssh_dir / "rio_ed25519.pub"
        pub_path.write_text("orphaned-public-key")

        priv, pub, cert, generated = ensure_rio_key_pair(ssh_dir)

        assert generated is True
        assert priv.is_file()
        assert pub.is_file()

    def test_generated_key_is_valid_ed25519(self, tmp_path):
        """Generated key pair should be loadable as ed25519."""
        ssh_dir = tmp_path / ".ssh"
        ssh_dir.mkdir()
        priv, pub, cert, generated = ensure_rio_key_pair(ssh_dir)

        # Load private key — should not raise
        from cryptography.hazmat.primitives.serialization import load_ssh_private_key

        private_key = load_ssh_private_key(priv.read_bytes(), password=None)
        assert private_key is not None

        # Public key should be parseable
        pub_text = pub.read_text().strip()
        parts = pub_text.split()
        assert len(parts) >= 2
        assert parts[0] == "ssh-ed25519"
        # Should be valid base64
        base64.b64decode(parts[1])

    def test_idempotent_double_generate(self, tmp_path):
        """Calling ensure twice should return same key pair on second call."""
        ssh_dir = tmp_path / ".ssh"
        ssh_dir.mkdir()
        _, pub1, _, gen1 = ensure_rio_key_pair(ssh_dir)
        pub1_content = pub1.read_text()

        _, pub2, _, gen2 = ensure_rio_key_pair(ssh_dir)
        pub2_content = pub2.read_text()

        assert gen1 is True
        assert gen2 is False
        assert pub1_content == pub2_content

    def test_public_key_permissions(self, tmp_path):
        ssh_dir = tmp_path / ".ssh"
        ssh_dir.mkdir()
        _, pub, _, _ = ensure_rio_key_pair(ssh_dir)
        assert oct(pub.stat().st_mode & 0o777) == "0o644"

    def test_creates_nested_ssh_dir(self, tmp_path):
        """Deeply nested ssh dir should be created."""
        ssh_dir = tmp_path / "a" / "b" / ".ssh"
        priv, pub, cert, generated = ensure_rio_key_pair(ssh_dir)

        assert generated is True
        assert ssh_dir.is_dir()
        assert priv.is_file()


class TestReadPublicKey:
    """Tests for read_public_key()."""

    def test_reads_key_content(self, tmp_path):
        pub = tmp_path / "test.pub"
        pub.write_text("ssh-ed25519 AAAAC3... rio-ssh\n")
        assert read_public_key(pub) == "ssh-ed25519 AAAAC3... rio-ssh"

    def test_strips_trailing_whitespace(self, tmp_path):
        pub = tmp_path / "test.pub"
        pub.write_text("ssh-ed25519 AAAAC3... rio-ssh\n\n  \n")
        assert read_public_key(pub) == "ssh-ed25519 AAAAC3... rio-ssh"

    def test_reads_generated_key(self, tmp_path):
        """read_public_key should work with keys from ensure_rio_key_pair."""
        ssh_dir = tmp_path / ".ssh"
        ssh_dir.mkdir()
        _, pub, _, _ = ensure_rio_key_pair(ssh_dir)
        content = read_public_key(pub)
        assert content.startswith("ssh-ed25519 ")
        assert content.endswith("rio-ssh")

    def test_missing_file_raises(self, tmp_path):
        pub = tmp_path / "nonexistent.pub"
        with pytest.raises(FileNotFoundError):
            read_public_key(pub)


# ---------------------------------------------------------------------------
# certificate.py – unit tests
# ---------------------------------------------------------------------------


class TestCertificateParsing:
    """Tests for certificate parsing functions."""

    def test_parse_valid_cert(self, tmp_path):
        future = int(time.time()) + 3600
        cert_path = tmp_path / "test-cert.pub"
        cert_path.write_text(_make_dummy_cert(future))

        expiry = parse_cert_valid_before(cert_path)
        assert expiry is not None
        assert expiry.timestamp() == pytest.approx(future, abs=1)

    def test_parse_missing_cert(self, tmp_path):
        cert_path = tmp_path / "nonexistent-cert.pub"
        assert parse_cert_valid_before(cert_path) is None

    def test_parse_invalid_cert(self, tmp_path):
        cert_path = tmp_path / "bad-cert.pub"
        cert_path.write_text("garbage data")
        assert parse_cert_valid_before(cert_path) is None

    def test_is_cert_valid_true(self, tmp_path):
        future = int(time.time()) + 3600
        cert_path = tmp_path / "test-cert.pub"
        cert_path.write_text(_make_dummy_cert(future))
        assert is_cert_valid(cert_path) is True

    def test_is_cert_valid_expired(self, tmp_path):
        past = int(time.time()) - 3600
        cert_path = tmp_path / "test-cert.pub"
        cert_path.write_text(_make_dummy_cert(past))
        assert is_cert_valid(cert_path) is False

    def test_is_cert_valid_missing(self, tmp_path):
        cert_path = tmp_path / "nonexistent-cert.pub"
        assert is_cert_valid(cert_path) is False

    def test_format_cert_expiry(self, tmp_path):
        future = int(time.time()) + 3600
        cert_path = tmp_path / "test-cert.pub"
        cert_path.write_text(_make_dummy_cert(future))
        result = format_cert_expiry(cert_path)
        assert result is not None
        # Should be a valid ISO timestamp string
        assert "T" in result

    def test_format_cert_expiry_missing(self, tmp_path):
        cert_path = tmp_path / "nonexistent-cert.pub"
        assert format_cert_expiry(cert_path) is None

    # --- Additional edge cases ---

    def test_parse_rsa_cert_type(self, tmp_path):
        """RSA cert type should be parsed correctly (2 pk fields)."""
        future = int(time.time()) + 3600
        cert_path = tmp_path / "rsa-cert.pub"
        cert_path.write_text(
            _make_dummy_cert(
                future,
                cert_type=b"ssh-rsa-cert-v01@openssh.com",
                pk_bytes=b"\x00" * 32,
            )
        )
        expiry = parse_cert_valid_before(cert_path)
        assert expiry is not None
        assert expiry.timestamp() == pytest.approx(future, abs=1)

    def test_parse_ecdsa_cert_type(self, tmp_path):
        """ECDSA cert type should be parsed correctly (2 pk fields)."""
        future = int(time.time()) + 3600
        cert_path = tmp_path / "ecdsa-cert.pub"
        cert_path.write_text(
            _make_dummy_cert(
                future,
                cert_type=b"ecdsa-sha2-nistp256-cert-v01@openssh.com",
            )
        )
        expiry = parse_cert_valid_before(cert_path)
        assert expiry is not None

    def test_parse_unknown_cert_type(self, tmp_path):
        """Unknown cert type should return None (not crash)."""
        cert_path = tmp_path / "unknown-cert.pub"
        # Build a minimal blob with unknown type
        cert_type = b"ssh-unknown-cert-v99@example.com"
        blob = struct.pack(">I", len(cert_type)) + cert_type
        blob += struct.pack(">I", 32) + (b"\x00" * 32)  # nonce
        b64 = base64.b64encode(blob).decode()
        cert_path.write_text(f"{cert_type.decode()} {b64}")
        assert parse_cert_valid_before(cert_path) is None

    def test_is_cert_valid_just_expired(self, tmp_path):
        """Cert that expired 1 second ago should be invalid."""
        just_past = int(time.time()) - 1
        cert_path = tmp_path / "just-expired.pub"
        cert_path.write_text(_make_dummy_cert(just_past))
        assert is_cert_valid(cert_path) is False

    def test_is_cert_valid_far_future(self, tmp_path):
        """Cert with far-future expiry should be valid."""
        far_future = int(time.time()) + 86400 * 365  # 1 year
        cert_path = tmp_path / "far-future.pub"
        cert_path.write_text(_make_dummy_cert(far_future))
        assert is_cert_valid(cert_path) is True

    def test_parse_empty_file(self, tmp_path):
        """Empty file should return None."""
        cert_path = tmp_path / "empty-cert.pub"
        cert_path.write_text("")
        assert parse_cert_valid_before(cert_path) is None

    def test_parse_truncated_blob(self, tmp_path):
        """Truncated cert blob should return None (not crash)."""
        cert_path = tmp_path / "truncated-cert.pub"
        # Just a type + partial nonce
        cert_type = b"ssh-ed25519-cert-v01@openssh.com"
        blob = struct.pack(">I", len(cert_type)) + cert_type + b"\x00" * 5
        b64 = base64.b64encode(blob).decode()
        cert_path.write_text(f"{cert_type.decode()} {b64}")
        assert parse_cert_valid_before(cert_path) is None

    def test_parse_cert_with_only_one_field(self, tmp_path):
        """Cert with invalid base64 in second field should return None."""
        cert_path = tmp_path / "bad-b64-cert.pub"
        cert_path.write_text("ssh-ed25519-cert-v01@openssh.com !!!invalid-b64!!!")
        assert parse_cert_valid_before(cert_path) is None

    def test_is_cert_valid_invalid_content(self, tmp_path):
        """is_cert_valid on a file with invalid cert content returns False."""
        cert_path = tmp_path / "bad.pub"
        cert_path.write_text("not a certificate at all")
        assert is_cert_valid(cert_path) is False

    def test_format_cert_expiry_invalid_content(self, tmp_path):
        cert_path = tmp_path / "bad.pub"
        cert_path.write_text("not a certificate")
        assert format_cert_expiry(cert_path) is None

    def test_parse_host_cert_type(self, tmp_path):
        """Host cert (type=2) should parse the same way."""
        future = int(time.time()) + 3600
        cert_path = tmp_path / "host-cert.pub"
        cert_path.write_text(_make_dummy_cert(future, cert_kind=2))
        expiry = parse_cert_valid_before(cert_path)
        assert expiry is not None

    def test_valid_before_is_utc(self, tmp_path):
        """Parsed expiry should be timezone-aware UTC."""
        future = int(time.time()) + 3600
        cert_path = tmp_path / "utc-cert.pub"
        cert_path.write_text(_make_dummy_cert(future))
        expiry = parse_cert_valid_before(cert_path)
        assert expiry is not None
        assert expiry.tzinfo == timezone.utc


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
        """Cert content should not be modified (except trailing newline)."""
        cert_content = "ssh-ed25519-cert-v01@openssh.com AAAA+/== user@host"
        cert_path = tmp_path / "exact-cert.pub"
        write_certificate(cert_path, cert_content)
        assert cert_path.read_text() == cert_content + "\n"


# ---------------------------------------------------------------------------
# agent.py – wire-format unit tests
# ---------------------------------------------------------------------------


class TestAgentProtocol:
    """Verify the binary payloads sent to ssh-agent."""

    @patch("riocli.ssh.agent._connect")
    def test_add_identity_plain_payload(self, mock_connect, tmp_path):
        """add_identity without cert builds SSH_AGENTC_ADD_ID_CONSTRAINED."""
        from riocli.ssh.agent import (
            _AGENT_COMMENT,
            SSH_AGENT_CONSTRAIN_LIFETIME,
            SSH_AGENTC_ADD_ID_CONSTRAINED,
            add_identity,
        )

        priv, pub = _generate_test_key_pair(tmp_path)
        sock = _fake_agent_socket()
        mock_connect.return_value = sock

        add_identity(priv, lifetime=120)

        # Grab the raw bytes sent to the socket.
        sent = b"".join(c.args[0] for c in sock.sendall.call_args_list)

        # Outer envelope: 4‑byte length + 1‑byte msg_type.
        total_len = struct.unpack(">I", sent[:4])[0]
        msg_type = sent[4]
        assert msg_type == SSH_AGENTC_ADD_ID_CONSTRAINED
        assert len(sent) == 4 + total_len  # no trailing garbage

        # Walk the payload fields.
        payload = sent[5:]
        off = 0

        def read_string(buf, offset):
            slen = struct.unpack(">I", buf[offset : offset + 4])[0]
            return buf[offset + 4 : offset + 4 + slen], offset + 4 + slen

        key_type, off = read_string(payload, off)
        assert key_type == b"ssh-ed25519"

        pk_bytes, off = read_string(payload, off)
        assert len(pk_bytes) == 32  # ed25519 public key

        sk_bytes, off = read_string(payload, off)
        assert len(sk_bytes) == 64  # seed(32) || pk(32)
        assert sk_bytes[32:] == pk_bytes  # second half is public key

        comment, off = read_string(payload, off)
        assert comment == _AGENT_COMMENT

        # Lifetime constraint.
        constraint_type = payload[off]
        assert constraint_type == SSH_AGENT_CONSTRAIN_LIFETIME
        lifetime_val = struct.unpack(">I", payload[off + 1 : off + 5])[0]
        assert lifetime_val == 120

    @patch("riocli.ssh.agent._connect")
    def test_add_identity_with_cert_payload(self, mock_connect, tmp_path):
        """add_identity with cert includes the cert blob in the payload."""
        from riocli.ssh.agent import (
            SSH_AGENTC_ADD_ID_CONSTRAINED,
            add_identity,
        )

        priv, pub = _generate_test_key_pair(tmp_path)
        cert_path = tmp_path / "rio_ed25519-cert.pub"

        # Write a dummy cert file.
        dummy_blob = b"\x00" * 64
        cert_text = (
            f"ssh-ed25519-cert-v01@openssh.com "
            f"{base64.b64encode(dummy_blob).decode()} test"
        )
        cert_path.write_text(cert_text)

        sock = _fake_agent_socket()
        mock_connect.return_value = sock

        add_identity(priv, cert_path, lifetime=300)

        sent = b"".join(c.args[0] for c in sock.sendall.call_args_list)
        msg_type = sent[4]
        assert msg_type == SSH_AGENTC_ADD_ID_CONSTRAINED

        # First string in payload must be the cert type.
        payload = sent[5:]
        slen = struct.unpack(">I", payload[:4])[0]
        cert_type = payload[4 : 4 + slen]
        assert cert_type == b"ssh-ed25519-cert-v01@openssh.com"

    @patch("riocli.ssh.agent._connect")
    def test_add_identity_cert_payload_contains_blob(self, mock_connect, tmp_path):
        """The cert blob sent to agent should match the file content."""
        from riocli.ssh.agent import add_identity

        priv, pub = _generate_test_key_pair(tmp_path)
        cert_path = tmp_path / "rio_ed25519-cert.pub"

        dummy_blob = os.urandom(128)
        cert_text = (
            f"ssh-ed25519-cert-v01@openssh.com "
            f"{base64.b64encode(dummy_blob).decode()} comment"
        )
        cert_path.write_text(cert_text)

        sock = _fake_agent_socket()
        mock_connect.return_value = sock

        add_identity(priv, cert_path)

        sent = b"".join(c.args[0] for c in sock.sendall.call_args_list)
        payload = sent[5:]

        def read_string(buf, offset):
            slen = struct.unpack(">I", buf[offset : offset + 4])[0]
            return buf[offset + 4 : offset + 4 + slen], offset + 4 + slen

        # Skip cert_type → cert_blob is second field
        _, off = read_string(payload, 0)
        blob_in_payload, _ = read_string(payload, off)
        assert blob_in_payload == dummy_blob

    @patch("riocli.ssh.agent._connect")
    def test_add_identity_no_cert_file_uses_plain(self, mock_connect, tmp_path):
        """When cert_path is given but file doesn't exist, use plain identity."""
        from riocli.ssh.agent import add_identity

        priv, pub = _generate_test_key_pair(tmp_path)
        cert_path = tmp_path / "nonexistent-cert.pub"

        sock = _fake_agent_socket()
        mock_connect.return_value = sock

        add_identity(priv, cert_path)

        sent = b"".join(c.args[0] for c in sock.sendall.call_args_list)
        payload = sent[5:]
        slen = struct.unpack(">I", payload[:4])[0]
        key_type = payload[4 : 4 + slen]
        assert key_type == b"ssh-ed25519"  # plain, not cert type

    @patch("riocli.ssh.agent._connect")
    def test_add_identity_default_lifetime(self, mock_connect, tmp_path):
        """Default lifetime should be 300 seconds (5 minutes)."""
        from riocli.ssh.agent import SSH_AGENT_CONSTRAIN_LIFETIME, add_identity

        priv, pub = _generate_test_key_pair(tmp_path)
        sock = _fake_agent_socket()
        mock_connect.return_value = sock

        add_identity(priv)  # no lifetime arg → default 300

        sent = b"".join(c.args[0] for c in sock.sendall.call_args_list)
        # Find the lifetime constraint at the end of the payload.
        # Last 5 bytes: 1-byte constraint_type + 4-byte uint32 lifetime.
        constraint = sent[-5:]
        assert constraint[0] == SSH_AGENT_CONSTRAIN_LIFETIME
        lifetime = struct.unpack(">I", constraint[1:])[0]
        assert lifetime == 300

    @patch("riocli.ssh.agent._connect")
    def test_remove_identity_payload(self, mock_connect, tmp_path):
        """remove_identity sends SSH_AGENTC_REMOVE_IDENTITY with key blob."""
        from riocli.ssh.agent import (
            SSH_AGENTC_REMOVE_IDENTITY,
            _get_key_blob,
            remove_identity,
        )

        _generate_test_key_pair(tmp_path)
        pub_path = tmp_path / "rio_ed25519.pub"
        blob = _get_key_blob(pub_path)

        sock = _fake_agent_socket()
        mock_connect.return_value = sock

        remove_identity(blob)

        sent = b"".join(c.args[0] for c in sock.sendall.call_args_list)
        msg_type = sent[4]
        assert msg_type == SSH_AGENTC_REMOVE_IDENTITY

        # Payload must be string(key_blob).
        payload = sent[5:]
        slen = struct.unpack(">I", payload[:4])[0]
        assert payload[4 : 4 + slen] == blob

    @patch("riocli.ssh.agent._connect")
    def test_add_identity_agent_failure(self, mock_connect, tmp_path):
        """add_identity raises RuntimeError when agent returns FAILURE."""
        from riocli.ssh.agent import SSH_AGENT_FAILURE, add_identity

        priv, pub = _generate_test_key_pair(tmp_path)
        sock = _fake_agent_socket(response_type=SSH_AGENT_FAILURE)
        mock_connect.return_value = sock

        with pytest.raises(RuntimeError, match="refused"):
            add_identity(priv)

    def test_connect_raises_without_auth_sock(self, monkeypatch):
        """_connect raises RuntimeError when SSH_AUTH_SOCK is unset."""
        from riocli.ssh.agent import _connect

        monkeypatch.delenv("SSH_AUTH_SOCK", raising=False)

        with pytest.raises(RuntimeError, match="SSH_AUTH_SOCK"):
            _connect()

    @patch("riocli.ssh.agent._connect")
    def test_remove_identity_silences_errors(self, mock_connect, tmp_path):
        """remove_identity should silently ignore agent errors."""
        from riocli.ssh.agent import remove_identity

        mock_connect.side_effect = RuntimeError("agent down")
        # Should NOT raise
        remove_identity(b"\x00" * 32)

    @patch("riocli.ssh.agent._connect")
    def test_remove_rio_identities_sends_two_removes(self, mock_connect, tmp_path):
        """remove_rio_identities should send remove_identity twice."""
        from riocli.ssh.agent import (
            SSH_AGENTC_REMOVE_IDENTITY,
            remove_rio_identities,
        )

        _generate_test_key_pair(tmp_path)
        pub_path = tmp_path / "rio_ed25519.pub"

        sock = _fake_agent_socket()
        # Need two successful responses (one per remove_identity call).
        resp = struct.pack(">IB", 1, 6)
        sock.recv.side_effect = [resp[:4], resp[4:]] * 2
        mock_connect.return_value = sock

        remove_rio_identities(pub_path)

        # Should have called sendall twice (one remove per call).
        assert sock.sendall.call_count == 2
        for sendall_call in sock.sendall.call_args_list:
            sent = sendall_call.args[0]
            assert sent[4] == SSH_AGENTC_REMOVE_IDENTITY

    @patch("riocli.ssh.agent._connect")
    def test_remove_rio_identities_missing_pub_noop(self, mock_connect, tmp_path):
        """remove_rio_identities with missing public key file is a no-op."""
        from riocli.ssh.agent import remove_rio_identities

        pub_path = tmp_path / "nonexistent.pub"
        # Should NOT raise, not contact agent
        remove_rio_identities(pub_path)
        mock_connect.assert_not_called()

    @patch("riocli.ssh.agent._connect")
    def test_remove_rio_identities_agent_error_silenced(self, mock_connect, tmp_path):
        """remove_rio_identities silences all errors."""
        from riocli.ssh.agent import remove_rio_identities

        _generate_test_key_pair(tmp_path)
        pub_path = tmp_path / "rio_ed25519.pub"
        mock_connect.side_effect = RuntimeError("agent unavailable")

        # Should NOT raise
        remove_rio_identities(pub_path)

    def test_get_key_blob_valid(self, tmp_path):
        """_get_key_blob returns decodeable binary for a valid pub key."""
        from riocli.ssh.agent import _get_key_blob

        _generate_test_key_pair(tmp_path)
        pub_path = tmp_path / "rio_ed25519.pub"
        blob = _get_key_blob(pub_path)

        # Should start with the key type string
        slen = struct.unpack(">I", blob[:4])[0]
        key_type = blob[4 : 4 + slen]
        assert key_type == b"ssh-ed25519"

    def test_get_key_blob_invalid_file(self, tmp_path):
        """_get_key_blob raises for a malformed file."""
        from riocli.ssh.agent import _get_key_blob

        bad_pub = tmp_path / "bad.pub"
        bad_pub.write_text("single-word-no-space")
        with pytest.raises(RuntimeError, match="Invalid public key"):
            _get_key_blob(bad_pub)

    def test_get_cert_blob_invalid_file(self, tmp_path):
        """_get_cert_blob raises for a malformed file."""
        from riocli.ssh.agent import _get_cert_blob

        bad_cert = tmp_path / "bad-cert.pub"
        bad_cert.write_text("single-word")
        with pytest.raises(RuntimeError, match="Invalid certificate"):
            _get_cert_blob(bad_cert)

    def test_pack_string(self):
        """_pack_string should produce uint32-length prefix + data."""
        from riocli.ssh.agent import _pack_string

        result = _pack_string(b"hello")
        assert result == struct.pack(">I", 5) + b"hello"

    def test_pack_string_empty(self):
        from riocli.ssh.agent import _pack_string

        result = _pack_string(b"")
        assert result == struct.pack(">I", 0)

    @patch("riocli.ssh.agent._connect")
    def test_add_identity_closes_socket_on_success(self, mock_connect, tmp_path):
        """Socket should be closed even on success."""
        from riocli.ssh.agent import add_identity

        priv, pub = _generate_test_key_pair(tmp_path)
        sock = _fake_agent_socket()
        mock_connect.return_value = sock

        add_identity(priv)
        sock.close.assert_called_once()

    @patch("riocli.ssh.agent._connect")
    def test_add_identity_closes_socket_on_failure(self, mock_connect, tmp_path):
        """Socket should be closed even when agent returns failure."""
        from riocli.ssh.agent import SSH_AGENT_FAILURE, add_identity

        priv, pub = _generate_test_key_pair(tmp_path)
        sock = _fake_agent_socket(response_type=SSH_AGENT_FAILURE)
        mock_connect.return_value = sock

        with pytest.raises(RuntimeError):
            add_identity(priv)
        sock.close.assert_called_once()

    def test_recv_all_handles_partial_reads(self):
        """_recv_all should assemble bytes from multiple recv() calls."""
        from riocli.ssh.agent import _recv_all

        sock = MagicMock()
        sock.recv.side_effect = [b"\x00\x00", b"\x00", b"\x04"]
        result = _recv_all(sock, 4)
        assert result == b"\x00\x00\x00\x04"
        assert sock.recv.call_count == 3

    def test_recv_all_connection_closed(self):
        """_recv_all raises when connection is closed mid-read."""
        from riocli.ssh.agent import _recv_all

        sock = MagicMock()
        sock.recv.side_effect = [b"\x00\x00", b""]  # closed after 2 bytes
        with pytest.raises(RuntimeError, match="closed connection"):
            _recv_all(sock, 4)


# ---------------------------------------------------------------------------
# CLI command – integration tests (Click CliRunner)
# ---------------------------------------------------------------------------


@pytest.fixture
def ssh_dir(tmp_path):
    """Create a temporary ~/.ssh with a rio_ed25519 key pair."""
    d = tmp_path / ".ssh"
    d.mkdir()
    _generate_test_key_pair(d)
    return d


class TestSSHCommand:
    """Tests for the ``rio ssh`` click command."""

    # ---- Happy paths ----

    @patch("riocli.ssh.add_identity")
    @patch("riocli.ssh.remove_rio_identities")
    @patch("riocli.ssh.new_v2_client")
    @patch("riocli.ssh.ensure_rio_key_pair")
    def test_happy_path(self, mock_ensure, mock_v2, mock_remove, mock_add, ssh_dir):
        priv = ssh_dir / "rio_ed25519"
        pub = ssh_dir / "rio_ed25519.pub"
        cert = ssh_dir / "rio_ed25519-cert.pub"
        mock_ensure.return_value = (priv, pub, cert, False)
        mock_v2.return_value = _mock_v2_client()

        from riocli.ssh import ssh

        runner = CliRunner()
        result = runner.invoke(ssh, [], catch_exceptions=False)

        assert result.exit_code == 0
        mock_v2.return_value.sign_ssh_public_key.assert_called_once()
        assert cert.exists()
        mock_add.assert_called_once()

    @patch("riocli.ssh.add_identity")
    @patch("riocli.ssh.remove_rio_identities")
    @patch("riocli.ssh.new_v2_client")
    @patch("riocli.ssh.ensure_rio_key_pair")
    def test_first_run_generates_key(
        self, mock_ensure, mock_v2, mock_remove, mock_add, ssh_dir
    ):
        """First run should log that a new key pair was generated."""
        priv = ssh_dir / "rio_ed25519"
        pub = ssh_dir / "rio_ed25519.pub"
        cert = ssh_dir / "rio_ed25519-cert.pub"
        mock_ensure.return_value = (priv, pub, cert, True)
        mock_v2.return_value = _mock_v2_client()

        from riocli.ssh import ssh

        runner = CliRunner()
        result = runner.invoke(ssh, [], catch_exceptions=False)

        assert result.exit_code == 0
        assert "Generated dedicated key pair" in result.output

    # ---- Flag behaviour ----

    @patch("riocli.ssh.add_identity")
    @patch("riocli.ssh.remove_rio_identities")
    @patch("riocli.ssh.new_v2_client")
    @patch("riocli.ssh.ensure_rio_key_pair")
    def test_no_agent_flag_skips_agent(
        self, mock_ensure, mock_v2, mock_remove, mock_add, ssh_dir
    ):
        priv = ssh_dir / "rio_ed25519"
        pub = ssh_dir / "rio_ed25519.pub"
        cert = ssh_dir / "rio_ed25519-cert.pub"
        mock_ensure.return_value = (priv, pub, cert, False)
        mock_v2.return_value = _mock_v2_client()

        from riocli.ssh import ssh

        runner = CliRunner()
        result = runner.invoke(ssh, ["--no-agent"], catch_exceptions=False)

        assert result.exit_code == 0
        mock_add.assert_not_called()
        mock_remove.assert_not_called()

    @patch("riocli.ssh.add_identity")
    @patch("riocli.ssh.remove_rio_identities")
    @patch("riocli.ssh.new_v2_client")
    @patch("riocli.ssh.ensure_rio_key_pair")
    def test_force_re_signs(self, mock_ensure, mock_v2, mock_remove, mock_add, ssh_dir):
        priv = ssh_dir / "rio_ed25519"
        pub = ssh_dir / "rio_ed25519.pub"
        cert = ssh_dir / "rio_ed25519-cert.pub"
        cert.write_text("old-cert")
        mock_ensure.return_value = (priv, pub, cert, False)
        mock_v2.return_value = _mock_v2_client(certificate="new-cert")

        from riocli.ssh import ssh

        runner = CliRunner()
        result = runner.invoke(ssh, ["--force"], catch_exceptions=False)

        assert result.exit_code == 0
        assert cert.read_text().strip() == "new-cert"

    @patch("riocli.ssh.add_identity")
    @patch("riocli.ssh.remove_rio_identities")
    @patch("riocli.ssh.new_v2_client")
    @patch("riocli.ssh.ensure_rio_key_pair")
    def test_user_guid_passed_through(
        self, mock_ensure, mock_v2, mock_remove, mock_add, ssh_dir
    ):
        """--user-guid should be forwarded to the SDK call."""
        priv = ssh_dir / "rio_ed25519"
        pub = ssh_dir / "rio_ed25519.pub"
        cert = ssh_dir / "rio_ed25519-cert.pub"
        mock_ensure.return_value = (priv, pub, cert, False)
        mock_v2.return_value = _mock_v2_client()

        from riocli.ssh import ssh

        runner = CliRunner()
        result = runner.invoke(
            ssh, ["--user-guid", "test-guid-123"], catch_exceptions=False
        )

        assert result.exit_code == 0
        sign_call = mock_v2.return_value.sign_ssh_public_key
        sign_call.assert_called_once()
        _, kwargs = sign_call.call_args
        assert kwargs["user_guid"] == "test-guid-123"

    @patch("riocli.ssh.add_identity")
    @patch("riocli.ssh.remove_rio_identities")
    @patch("riocli.ssh.new_v2_client")
    @patch("riocli.ssh.ensure_rio_key_pair")
    def test_force_and_no_agent(
        self, mock_ensure, mock_v2, mock_remove, mock_add, ssh_dir
    ):
        """--force --no-agent: re-sign but skip agent loading."""
        priv = ssh_dir / "rio_ed25519"
        pub = ssh_dir / "rio_ed25519.pub"
        cert = ssh_dir / "rio_ed25519-cert.pub"
        cert.write_text("old-cert")
        mock_ensure.return_value = (priv, pub, cert, False)
        mock_v2.return_value = _mock_v2_client(certificate="fresh-cert")

        from riocli.ssh import ssh

        runner = CliRunner()
        result = runner.invoke(ssh, ["--force", "--no-agent"], catch_exceptions=False)

        assert result.exit_code == 0
        mock_v2.return_value.sign_ssh_public_key.assert_called_once()
        assert cert.read_text().strip() == "fresh-cert"
        mock_add.assert_not_called()
        mock_remove.assert_not_called()

    @patch("riocli.ssh.add_identity")
    @patch("riocli.ssh.remove_rio_identities")
    @patch("riocli.ssh.new_v2_client")
    @patch("riocli.ssh.ensure_rio_key_pair")
    def test_short_force_flag(self, mock_ensure, mock_v2, mock_remove, mock_add, ssh_dir):
        """-f should work the same as --force."""
        priv = ssh_dir / "rio_ed25519"
        pub = ssh_dir / "rio_ed25519.pub"
        cert = ssh_dir / "rio_ed25519-cert.pub"
        cert.write_text("old-cert")
        mock_ensure.return_value = (priv, pub, cert, False)
        mock_v2.return_value = _mock_v2_client(certificate="new-cert")

        from riocli.ssh import ssh

        runner = CliRunner()
        result = runner.invoke(ssh, ["-f"], catch_exceptions=False)

        assert result.exit_code == 0
        mock_v2.return_value.sign_ssh_public_key.assert_called_once()

    # ---- Error paths ----

    @patch("riocli.ssh.ensure_rio_key_pair")
    def test_key_generation_error(self, mock_ensure):
        mock_ensure.side_effect = FileNotFoundError("Permission denied")

        from riocli.ssh import ssh

        runner = CliRunner()
        result = runner.invoke(ssh, [])

        assert result.exit_code == 1
        assert "Permission denied" in result.output

    @patch("riocli.ssh.new_v2_client")
    @patch("riocli.ssh.ensure_rio_key_pair")
    def test_api_error_exits(self, mock_ensure, mock_v2, ssh_dir):
        priv = ssh_dir / "rio_ed25519"
        pub = ssh_dir / "rio_ed25519.pub"
        cert = ssh_dir / "rio_ed25519-cert.pub"
        mock_ensure.return_value = (priv, pub, cert, False)
        mock_v2.return_value.sign_ssh_public_key.side_effect = Exception("unauthorized")

        from riocli.ssh import ssh

        runner = CliRunner()
        result = runner.invoke(ssh, [])

        assert result.exit_code == 1
        assert "unauthorized" in result.output

    @patch("riocli.ssh.new_v2_client")
    @patch("riocli.ssh.ensure_rio_key_pair")
    def test_runtime_error_exits(self, mock_ensure, mock_v2, ssh_dir):
        """RuntimeError from SDK should exit with code 1."""
        priv = ssh_dir / "rio_ed25519"
        pub = ssh_dir / "rio_ed25519.pub"
        cert = ssh_dir / "rio_ed25519-cert.pub"
        mock_ensure.return_value = (priv, pub, cert, False)
        mock_v2.return_value.sign_ssh_public_key.side_effect = RuntimeError("timeout")

        from riocli.ssh import ssh

        runner = CliRunner()
        result = runner.invoke(ssh, [])

        assert result.exit_code == 1
        assert "timeout" in result.output

    @patch("riocli.ssh.new_v2_client")
    @patch("riocli.ssh.ensure_rio_key_pair")
    def test_network_error_shows_message(self, mock_ensure, mock_v2, ssh_dir):
        priv = ssh_dir / "rio_ed25519"
        pub = ssh_dir / "rio_ed25519.pub"
        cert = ssh_dir / "rio_ed25519-cert.pub"
        mock_ensure.return_value = (priv, pub, cert, False)
        mock_v2.return_value.sign_ssh_public_key.side_effect = ConnectionError(
            "Connection refused"
        )

        from riocli.ssh import ssh

        runner = CliRunner()
        result = runner.invoke(ssh, [])

        assert result.exit_code == 1
        assert "Connection refused" in result.output

    # ---- Agent interaction edge cases ----

    @patch("riocli.ssh.add_identity")
    @patch("riocli.ssh.remove_rio_identities")
    @patch("riocli.ssh.new_v2_client")
    @patch("riocli.ssh.ensure_rio_key_pair")
    def test_agent_failure_warns_but_succeeds(
        self, mock_ensure, mock_v2, mock_remove, mock_add, ssh_dir
    ):
        """Agent failure should print a warning, not fail the command."""
        priv = ssh_dir / "rio_ed25519"
        pub = ssh_dir / "rio_ed25519.pub"
        cert = ssh_dir / "rio_ed25519-cert.pub"
        mock_ensure.return_value = (priv, pub, cert, False)
        mock_v2.return_value = _mock_v2_client()
        mock_add.side_effect = RuntimeError("agent not running")

        from riocli.ssh import ssh

        runner = CliRunner()
        result = runner.invoke(ssh, [], catch_exceptions=False)

        assert result.exit_code == 0
        assert "agent not running" in result.output

    @patch("riocli.ssh.add_identity")
    @patch("riocli.ssh.remove_rio_identities")
    @patch("riocli.ssh.new_v2_client")
    @patch("riocli.ssh.ensure_rio_key_pair")
    def test_remove_identities_called_before_write(
        self, mock_ensure, mock_v2, mock_remove, mock_add, ssh_dir
    ):
        """remove_rio_identities must be called BEFORE writing the new cert."""
        priv = ssh_dir / "rio_ed25519"
        pub = ssh_dir / "rio_ed25519.pub"
        cert = ssh_dir / "rio_ed25519-cert.pub"
        mock_ensure.return_value = (priv, pub, cert, False)
        mock_v2.return_value = _mock_v2_client()

        call_order = []
        mock_remove.side_effect = lambda *a, **k: call_order.append("remove")

        from riocli.ssh import ssh

        # Patch write_certificate to track call order
        with patch("riocli.ssh.write_certificate") as mock_write:
            mock_write.side_effect = lambda *a, **k: call_order.append("write")
            runner = CliRunner()
            result = runner.invoke(ssh, [], catch_exceptions=False)

        assert result.exit_code == 0
        assert call_order.index("remove") < call_order.index("write")

    # ---- Cert reuse paths ----

    @patch("riocli.ssh.add_identity")
    @patch("riocli.ssh.remove_rio_identities")
    @patch("riocli.ssh.is_cert_valid", return_value=True)
    @patch("riocli.ssh.format_cert_expiry", return_value="2026-12-31T23:59:59")
    @patch("riocli.ssh.new_v2_client")
    @patch("riocli.ssh.ensure_rio_key_pair")
    def test_reuse_valid_cert_skips_api(
        self,
        mock_ensure,
        mock_v2,
        mock_expiry,
        mock_valid,
        mock_remove,
        mock_add,
        ssh_dir,
    ):
        """When a valid cert already exists, skip the API call."""
        priv = ssh_dir / "rio_ed25519"
        pub = ssh_dir / "rio_ed25519.pub"
        cert = ssh_dir / "rio_ed25519-cert.pub"
        cert.write_text("existing-valid-cert")
        mock_ensure.return_value = (priv, pub, cert, False)

        from riocli.ssh import ssh

        runner = CliRunner()
        result = runner.invoke(ssh, [], catch_exceptions=False)

        assert result.exit_code == 0
        mock_v2.return_value.sign_ssh_public_key.assert_not_called()
        mock_add.assert_called_once()
        assert "still valid" in result.output

    @patch("riocli.ssh.add_identity")
    @patch("riocli.ssh.remove_rio_identities")
    @patch("riocli.ssh.is_cert_valid", return_value=True)
    @patch("riocli.ssh.new_v2_client")
    @patch("riocli.ssh.ensure_rio_key_pair")
    def test_force_overrides_valid_cert(
        self, mock_ensure, mock_v2, mock_valid, mock_remove, mock_add, ssh_dir
    ):
        """--force should re-sign even when the existing cert is valid."""
        priv = ssh_dir / "rio_ed25519"
        pub = ssh_dir / "rio_ed25519.pub"
        cert = ssh_dir / "rio_ed25519-cert.pub"
        cert.write_text("old-cert")
        mock_ensure.return_value = (priv, pub, cert, False)
        mock_v2.return_value = _mock_v2_client(certificate="fresh-cert")

        from riocli.ssh import ssh

        runner = CliRunner()
        result = runner.invoke(ssh, ["--force"], catch_exceptions=False)

        assert result.exit_code == 0
        mock_v2.return_value.sign_ssh_public_key.assert_called_once()
        assert cert.read_text().strip() == "fresh-cert"

    @patch("riocli.ssh.add_identity")
    @patch("riocli.ssh.remove_rio_identities")
    @patch("riocli.ssh.is_cert_valid", return_value=True)
    @patch("riocli.ssh.format_cert_expiry", return_value="2026-12-31T23:59:59")
    @patch("riocli.ssh.new_v2_client")
    @patch("riocli.ssh.ensure_rio_key_pair")
    def test_reuse_valid_cert_no_agent(
        self,
        mock_ensure,
        mock_v2,
        mock_expiry,
        mock_valid,
        mock_remove,
        mock_add,
        ssh_dir,
    ):
        """Reuse valid cert with --no-agent should skip agent loading."""
        priv = ssh_dir / "rio_ed25519"
        pub = ssh_dir / "rio_ed25519.pub"
        cert = ssh_dir / "rio_ed25519-cert.pub"
        cert.write_text("existing-valid-cert")
        mock_ensure.return_value = (priv, pub, cert, False)

        from riocli.ssh import ssh

        runner = CliRunner()
        result = runner.invoke(ssh, ["--no-agent"], catch_exceptions=False)

        assert result.exit_code == 0
        mock_v2.return_value.sign_ssh_public_key.assert_not_called()
        mock_add.assert_not_called()

    @patch("riocli.ssh.add_identity")
    @patch("riocli.ssh.remove_rio_identities")
    @patch("riocli.ssh.is_cert_valid", return_value=True)
    @patch("riocli.ssh.format_cert_expiry", return_value="2026-12-31T23:59:59")
    @patch("riocli.ssh.new_v2_client")
    @patch("riocli.ssh.ensure_rio_key_pair")
    def test_reuse_with_agent_failure_warns(
        self,
        mock_ensure,
        mock_v2,
        mock_expiry,
        mock_valid,
        mock_remove,
        mock_add,
        ssh_dir,
    ):
        """Reuse path + agent failure should warn, not fail."""
        priv = ssh_dir / "rio_ed25519"
        pub = ssh_dir / "rio_ed25519.pub"
        cert = ssh_dir / "rio_ed25519-cert.pub"
        cert.write_text("existing-valid-cert")
        mock_ensure.return_value = (priv, pub, cert, False)
        mock_add.side_effect = RuntimeError("SSH_AUTH_SOCK is not set")

        from riocli.ssh import ssh

        runner = CliRunner()
        result = runner.invoke(ssh, [], catch_exceptions=False)

        assert result.exit_code == 0
        assert "SSH_AUTH_SOCK" in result.output

    @patch("riocli.ssh.add_identity")
    @patch("riocli.ssh.remove_rio_identities")
    @patch("riocli.ssh.is_cert_valid", return_value=True)
    @patch("riocli.ssh.format_cert_expiry", return_value=None)
    @patch("riocli.ssh.new_v2_client")
    @patch("riocli.ssh.ensure_rio_key_pair")
    def test_reuse_no_expiry_string(
        self,
        mock_ensure,
        mock_v2,
        mock_expiry,
        mock_valid,
        mock_remove,
        mock_add,
        ssh_dir,
    ):
        """Reuse path with unparseable expiry should still succeed."""
        priv = ssh_dir / "rio_ed25519"
        pub = ssh_dir / "rio_ed25519.pub"
        cert = ssh_dir / "rio_ed25519-cert.pub"
        cert.write_text("existing-valid-cert")
        mock_ensure.return_value = (priv, pub, cert, False)

        from riocli.ssh import ssh

        runner = CliRunner()
        result = runner.invoke(ssh, [], catch_exceptions=False)

        assert result.exit_code == 0
        assert "still valid" in result.output

    # ---- Output content tests ----

    @patch("riocli.ssh.add_identity")
    @patch("riocli.ssh.remove_rio_identities")
    @patch("riocli.ssh.new_v2_client")
    @patch("riocli.ssh.ensure_rio_key_pair")
    def test_output_contains_cert_written(
        self, mock_ensure, mock_v2, mock_remove, mock_add, ssh_dir
    ):
        """Output should mention that the cert was written."""
        priv = ssh_dir / "rio_ed25519"
        pub = ssh_dir / "rio_ed25519.pub"
        cert = ssh_dir / "rio_ed25519-cert.pub"
        mock_ensure.return_value = (priv, pub, cert, False)
        mock_v2.return_value = _mock_v2_client()

        from riocli.ssh import ssh

        runner = CliRunner()
        result = runner.invoke(ssh, [], catch_exceptions=False)

        assert result.exit_code == 0
        assert "SSH certificate written" in result.output

    @patch("riocli.ssh.add_identity")
    @patch("riocli.ssh.remove_rio_identities")
    @patch("riocli.ssh.new_v2_client")
    @patch("riocli.ssh.ensure_rio_key_pair")
    def test_output_contains_agent_loaded(
        self, mock_ensure, mock_v2, mock_remove, mock_add, ssh_dir
    ):
        """Output should mention agent loading."""
        priv = ssh_dir / "rio_ed25519"
        pub = ssh_dir / "rio_ed25519.pub"
        cert = ssh_dir / "rio_ed25519-cert.pub"
        mock_ensure.return_value = (priv, pub, cert, False)
        mock_v2.return_value = _mock_v2_client()

        from riocli.ssh import ssh

        runner = CliRunner()
        result = runner.invoke(ssh, [], catch_exceptions=False)

        assert result.exit_code == 0
        assert "Identity loaded into ssh-agent" in result.output
        assert "5m TTL" in result.output

    @patch("riocli.ssh.add_identity")
    @patch("riocli.ssh.remove_rio_identities")
    @patch("riocli.ssh.new_v2_client")
    @patch("riocli.ssh.ensure_rio_key_pair")
    def test_output_contains_public_key_path(
        self, mock_ensure, mock_v2, mock_remove, mock_add, ssh_dir
    ):
        """Output should mention the public key path."""
        priv = ssh_dir / "rio_ed25519"
        pub = ssh_dir / "rio_ed25519.pub"
        cert = ssh_dir / "rio_ed25519-cert.pub"
        mock_ensure.return_value = (priv, pub, cert, False)
        mock_v2.return_value = _mock_v2_client()

        from riocli.ssh import ssh

        runner = CliRunner()
        result = runner.invoke(ssh, [], catch_exceptions=False)

        assert result.exit_code == 0
        assert "Using SSH public key" in result.output


# ---------------------------------------------------------------------------
# E2E integration tests – full flow with real crypto, mocked SDK + socket
# ---------------------------------------------------------------------------


class TestE2ESignFlow:
    """End-to-end tests exercising the full command with real key generation,
    real cert parsing, and real agent wire-format – only the SDK API call
    and the Unix socket are mocked.

    These tests verify component interaction: keys.py ↔ certificate.py ↔
    agent.py ↔ __init__.py without stubbing any internal functions
    (except the network boundary).
    """

    def _run_ssh_e2e(
        self,
        tmp_ssh_dir: Path,
        certificate: str,
        cli_args: list[str] | None = None,
        agent_response: int = 6,
    ):
        """Run rio ssh with real crypto and mocked SDK/socket.

        Returns (CliRunner result, tmp_ssh_dir).
        """
        from riocli.ssh import ssh

        if cli_args is None:
            cli_args = []

        # Mock the SDK client
        mock_client = _mock_v2_client(certificate=certificate)

        # Mock the agent socket
        resp = struct.pack(">IB", 1, agent_response)

        with (
            patch("riocli.ssh.new_v2_client", return_value=mock_client),
            patch(
                "riocli.ssh.ensure_rio_key_pair", wraps=ensure_rio_key_pair
            ) as mock_ensure,
            patch("riocli.ssh.agent._connect") as mock_agent_connect,
        ):
            # ensure_rio_key_pair needs to use the tmp dir
            mock_ensure.side_effect = lambda: ensure_rio_key_pair(tmp_ssh_dir)

            sock = MagicMock()
            # Need enough responses for remove_identity (×2) + add_identity (×1)
            sock.recv.side_effect = [resp[:4], resp[4:]] * 10
            mock_agent_connect.return_value = sock

            runner = CliRunner()
            result = runner.invoke(ssh, cli_args, catch_exceptions=False)

        return result, mock_client, sock

    def test_first_run_full_flow(self, tmp_path):
        """First run: generate key → sign → write cert → load agent."""
        ssh_dir = tmp_path / ".ssh"
        ssh_dir.mkdir()

        cert_content = _make_dummy_cert(int(time.time()) + 3600)
        result, mock_client, sock = self._run_ssh_e2e(ssh_dir, cert_content)

        assert result.exit_code == 0

        # Key pair was generated
        assert (ssh_dir / "rio_ed25519").is_file()
        assert (ssh_dir / "rio_ed25519.pub").is_file()
        assert "Generated dedicated key pair" in result.output

        # Certificate was written
        cert_path = ssh_dir / "rio_ed25519-cert.pub"
        assert cert_path.is_file()
        assert cert_path.read_text().strip() == cert_content

        # SDK was called with the generated public key
        mock_client.sign_ssh_public_key.assert_called_once()
        call_args = mock_client.sign_ssh_public_key.call_args
        request = call_args.kwargs.get("body") or call_args.args[0]
        assert request.public_key.startswith("ssh-ed25519 ")

        # Agent was contacted (remove × 2 + add × 1 = 3 sendall calls)
        assert sock.sendall.call_count == 3

    def test_second_run_reuses_key(self, tmp_path):
        """Second run should reuse existing key pair."""
        ssh_dir = tmp_path / ".ssh"
        ssh_dir.mkdir()

        cert_content = _make_dummy_cert(int(time.time()) + 3600)

        # First run
        result1, _, _ = self._run_ssh_e2e(ssh_dir, cert_content)
        assert result1.exit_code == 0
        pub_content_1 = (ssh_dir / "rio_ed25519.pub").read_text()

        # Second run — key should be reused, not regenerated
        result2, _, _ = self._run_ssh_e2e(ssh_dir, cert_content)
        assert result2.exit_code == 0
        pub_content_2 = (ssh_dir / "rio_ed25519.pub").read_text()

        assert pub_content_1 == pub_content_2
        assert "Generated dedicated key pair" not in result2.output

    def test_valid_cert_reuse(self, tmp_path):
        """With a valid cert on disk, skip the API call."""
        ssh_dir = tmp_path / ".ssh"
        ssh_dir.mkdir()

        future_cert = _make_dummy_cert(int(time.time()) + 3600)

        # First run: generate key + sign
        result1, _, _ = self._run_ssh_e2e(ssh_dir, future_cert)
        assert result1.exit_code == 0

        # Second run: cert is still valid → reuse
        result2, mock_client2, _ = self._run_ssh_e2e(ssh_dir, "should-not-be-used")
        assert result2.exit_code == 0
        assert "still valid" in result2.output
        mock_client2.sign_ssh_public_key.assert_not_called()

    def test_expired_cert_triggers_re_sign(self, tmp_path):
        """An expired cert on disk should trigger a fresh API call."""
        ssh_dir = tmp_path / ".ssh"
        ssh_dir.mkdir()
        _generate_test_key_pair(ssh_dir)

        # Write an expired cert
        expired_cert = _make_dummy_cert(int(time.time()) - 60)
        cert_path = ssh_dir / "rio_ed25519-cert.pub"
        write_certificate(cert_path, expired_cert)

        # Run: expired cert → should call API
        fresh_cert = _make_dummy_cert(int(time.time()) + 3600)
        result, mock_client, _ = self._run_ssh_e2e(ssh_dir, fresh_cert)

        assert result.exit_code == 0
        mock_client.sign_ssh_public_key.assert_called_once()
        assert cert_path.read_text().strip() == fresh_cert

    def test_force_with_valid_cert(self, tmp_path):
        """--force should re-sign even with a valid cert."""
        ssh_dir = tmp_path / ".ssh"
        ssh_dir.mkdir()

        valid_cert = _make_dummy_cert(int(time.time()) + 3600)
        # First run to get a valid cert on disk
        result1, _, _ = self._run_ssh_e2e(ssh_dir, valid_cert)
        assert result1.exit_code == 0

        # Force re-sign
        new_cert = _make_dummy_cert(int(time.time()) + 7200)
        result2, mock_client2, _ = self._run_ssh_e2e(
            ssh_dir, new_cert, cli_args=["--force"]
        )

        assert result2.exit_code == 0
        mock_client2.sign_ssh_public_key.assert_called_once()
        cert_path = ssh_dir / "rio_ed25519-cert.pub"
        assert cert_path.read_text().strip() == new_cert

    def test_no_agent_skips_socket(self, tmp_path):
        """--no-agent should not touch the agent socket at all."""
        ssh_dir = tmp_path / ".ssh"
        ssh_dir.mkdir()

        cert_content = _make_dummy_cert(int(time.time()) + 3600)
        result, _, sock = self._run_ssh_e2e(
            ssh_dir, cert_content, cli_args=["--no-agent"]
        )

        assert result.exit_code == 0
        sock.sendall.assert_not_called()
        # Cert should still be written
        assert (ssh_dir / "rio_ed25519-cert.pub").is_file()

    def test_cert_file_permissions_after_full_flow(self, tmp_path):
        """Cert file should have 0o644 permissions after a full run."""
        ssh_dir = tmp_path / ".ssh"
        ssh_dir.mkdir()

        cert_content = _make_dummy_cert(int(time.time()) + 3600)
        result, _, _ = self._run_ssh_e2e(ssh_dir, cert_content)

        assert result.exit_code == 0
        cert_path = ssh_dir / "rio_ed25519-cert.pub"
        assert oct(cert_path.stat().st_mode & 0o777) == "0o644"

    def test_key_permissions_after_full_flow(self, tmp_path):
        """Private key should have 0o600, public 0o644."""
        ssh_dir = tmp_path / ".ssh"
        ssh_dir.mkdir()

        cert_content = _make_dummy_cert(int(time.time()) + 3600)
        result, _, _ = self._run_ssh_e2e(ssh_dir, cert_content)

        assert result.exit_code == 0
        assert oct((ssh_dir / "rio_ed25519").stat().st_mode & 0o777) == "0o600"
        assert oct((ssh_dir / "rio_ed25519.pub").stat().st_mode & 0o777) == "0o644"

    def test_public_key_sent_to_sdk_matches_file(self, tmp_path):
        """The public key sent to the SDK should match what's on disk."""
        ssh_dir = tmp_path / ".ssh"
        ssh_dir.mkdir()

        cert_content = _make_dummy_cert(int(time.time()) + 3600)
        result, mock_client, _ = self._run_ssh_e2e(ssh_dir, cert_content)

        assert result.exit_code == 0
        pub_on_disk = (ssh_dir / "rio_ed25519.pub").read_text().strip()

        sign_call = mock_client.sign_ssh_public_key.call_args
        request = sign_call.kwargs.get("body") or sign_call.args[0]
        assert request.public_key == pub_on_disk

    def test_agent_failure_does_not_affect_cert_on_disk(self, tmp_path):
        """Agent failure should still leave the cert file written."""
        ssh_dir = tmp_path / ".ssh"
        ssh_dir.mkdir()

        cert_content = _make_dummy_cert(int(time.time()) + 3600)

        from riocli.ssh import ssh

        mock_client = _mock_v2_client(certificate=cert_content)

        with (
            patch("riocli.ssh.new_v2_client", return_value=mock_client),
            patch("riocli.ssh.ensure_rio_key_pair") as mock_ensure,
            patch("riocli.ssh.add_identity", side_effect=RuntimeError("no agent")),
            patch("riocli.ssh.remove_rio_identities"),
        ):
            priv, pub = _generate_test_key_pair(ssh_dir)
            cert_path = ssh_dir / "rio_ed25519-cert.pub"
            mock_ensure.return_value = (priv, pub, cert_path, True)

            runner = CliRunner()
            result = runner.invoke(ssh, [], catch_exceptions=False)

        assert result.exit_code == 0
        assert cert_path.is_file()
        assert cert_path.read_text().strip() == cert_content

    def test_stale_cert_removed_on_key_regeneration(self, tmp_path):
        """When keys are regenerated, old cert must be deleted."""
        ssh_dir = tmp_path / ".ssh"
        ssh_dir.mkdir()

        # Simulate old cert from previous key
        old_cert = ssh_dir / "rio_ed25519-cert.pub"
        old_cert.write_text("stale-cert-for-old-key")

        # No key files → will regenerate
        cert_content = _make_dummy_cert(int(time.time()) + 3600)
        result, _, _ = self._run_ssh_e2e(ssh_dir, cert_content)

        assert result.exit_code == 0
        # The cert should now contain the NEW cert, not the stale one
        cert_on_disk = old_cert.read_text().strip()
        assert cert_on_disk == cert_content
        assert cert_on_disk != "stale-cert-for-old-key"

    def test_cert_expiry_displayed(self, tmp_path):
        """Output should display the certificate expiry time."""
        ssh_dir = tmp_path / ".ssh"
        ssh_dir.mkdir()

        future = int(time.time()) + 3600
        cert_content = _make_dummy_cert(future)
        result, _, _ = self._run_ssh_e2e(ssh_dir, cert_content)

        assert result.exit_code == 0
        assert "Certificate valid until" in result.output

    def test_sequential_runs_idempotent(self, tmp_path):
        """Multiple sequential runs should all succeed."""
        ssh_dir = tmp_path / ".ssh"
        ssh_dir.mkdir()

        for i in range(3):
            cert_content = _make_dummy_cert(int(time.time()) + 3600 + i)
            result, _, _ = self._run_ssh_e2e(ssh_dir, cert_content, cli_args=["--force"])
            assert result.exit_code == 0

        # Key pair should exist and be valid
        assert (ssh_dir / "rio_ed25519").is_file()
        assert (ssh_dir / "rio_ed25519.pub").is_file()
        assert (ssh_dir / "rio_ed25519-cert.pub").is_file()

    def test_agent_receives_correct_key_material(self, tmp_path):
        """The key material sent to agent should match the generated key."""
        ssh_dir = tmp_path / ".ssh"
        ssh_dir.mkdir()

        cert_content = _make_dummy_cert(int(time.time()) + 3600)
        result, _, sock = self._run_ssh_e2e(ssh_dir, cert_content)

        assert result.exit_code == 0

        # The last sendall call is the add_identity message.
        add_msg = sock.sendall.call_args_list[-1].args[0]
        msg_type = add_msg[4]
        assert msg_type == 25  # SSH_AGENTC_ADD_ID_CONSTRAINED

        # Extract the cert type from the payload (first string field)
        payload = add_msg[5:]
        slen = struct.unpack(">I", payload[:4])[0]
        first_field = payload[4 : 4 + slen]
        # With a cert file present, first field should be the cert type
        assert first_field == b"ssh-ed25519-cert-v01@openssh.com"

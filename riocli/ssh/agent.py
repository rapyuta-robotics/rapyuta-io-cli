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

"""SSH agent interaction for ``rio ssh``.

Speaks the SSH agent protocol (draft-miller-ssh-agent) directly over
the ``SSH_AUTH_SOCK`` Unix socket.

Only **ed25519** keys (with optional certificates) are supported,
matching the dedicated ``rio_ed25519`` key pair.
"""

from __future__ import annotations

import base64
import os
import socket
import struct
from typing import TYPE_CHECKING

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.serialization import load_ssh_private_key

if TYPE_CHECKING:
    from pathlib import Path

# ---------------------------------------------------------------------------
# SSH agent protocol constants (RFC draft-miller-ssh-agent)
# ---------------------------------------------------------------------------
SSH_AGENTC_REQUEST_IDENTITIES = 11
SSH_AGENT_IDENTITIES_ANSWER = 12
SSH_AGENTC_REMOVE_IDENTITY = 18
SSH_AGENTC_ADD_ID_CONSTRAINED = 25

SSH_AGENT_SUCCESS = 6
SSH_AGENT_FAILURE = 5

SSH_AGENT_CONSTRAIN_LIFETIME = 1

#: Default comment attached to identities added to the agent.
_AGENT_COMMENT = b"rio-ssh"


# ---------------------------------------------------------------------------
# Wire-format helpers
# ---------------------------------------------------------------------------


def _pack_string(data: bytes) -> bytes:
    """Pack *data* as a uint32-length-prefixed SSH string."""
    return struct.pack(">I", len(data)) + data


# ---------------------------------------------------------------------------
# Socket helpers
# ---------------------------------------------------------------------------


def _connect() -> socket.socket:
    """Connect to the running SSH agent via ``SSH_AUTH_SOCK``.

    Returns:
        A connected Unix-domain socket.

    Raises:
        RuntimeError: If ``SSH_AUTH_SOCK`` is unset or the connection fails.
    """
    sock_path = os.environ.get("SSH_AUTH_SOCK")
    if not sock_path:
        raise RuntimeError(
            "SSH_AUTH_SOCK is not set. Ensure ssh-agent is running (eval `ssh-agent -s`)."
        )

    try:
        sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        sock.connect(sock_path)
        return sock
    except OSError as exc:
        raise RuntimeError(
            f"Failed to connect to ssh-agent at {sock_path}: {exc}"
        ) from exc


def _recv_all(sock: socket.socket, n: int) -> bytes:
    """Read exactly *n* bytes from *sock*."""
    buf = b""
    while len(buf) < n:
        chunk = sock.recv(n - len(buf))
        if not chunk:
            raise RuntimeError("SSH agent closed connection unexpectedly")
        buf += chunk
    return buf


def _send_recv(sock: socket.socket, msg_type: int, payload: bytes) -> tuple[int, bytes]:
    """Send a message and read the agent's response.

    Args:
        sock: Connected agent socket.
        msg_type: Agent message type byte.
        payload: Message payload (without length or type header).

    Returns:
        ``(response_type, response_payload)`` tuple.
    """
    message = struct.pack(">IB", len(payload) + 1, msg_type) + payload
    sock.sendall(message)

    resp_len = struct.unpack(">I", _recv_all(sock, 4))[0]
    resp = _recv_all(sock, resp_len)
    return resp[0], resp[1:]


# ---------------------------------------------------------------------------
# Key material helpers
# ---------------------------------------------------------------------------


def _get_ed25519_raw_keys(private_key_path: Path) -> tuple[bytes, bytes]:
    """Load an ed25519 private key and return ``(seed_32, pk_32)``.

    Args:
        private_key_path: Path to the PEM/OpenSSH private key file.

    Returns:
        Tuple of ``(raw_seed, raw_public_key)`` each 32 bytes.
    """
    private_key = load_ssh_private_key(
        private_key_path.read_bytes(),
        password=None,
    )

    raw_pk = private_key.public_key().public_bytes(
        encoding=serialization.Encoding.Raw,
        format=serialization.PublicFormat.Raw,
    )
    raw_seed = private_key.private_bytes(
        encoding=serialization.Encoding.Raw,
        format=serialization.PrivateFormat.Raw,
        encryption_algorithm=serialization.NoEncryption(),
    )

    return raw_seed, raw_pk


def _get_key_blob(public_key_path: Path) -> bytes:
    """Read a public key file and return its binary blob.

    The blob is in SSH wire format: ``string(key_type) + string(data)``.
    """
    parts = public_key_path.read_text().strip().split()
    if len(parts) < 2:
        raise RuntimeError(f"Invalid public key file: {public_key_path}")
    return base64.b64decode(parts[1])


def _get_cert_blob(cert_path: Path) -> bytes:
    """Read a certificate file and return its binary blob."""
    parts = cert_path.read_text().strip().split()
    if len(parts) < 2:
        raise RuntimeError(f"Invalid certificate file: {cert_path}")
    return base64.b64decode(parts[1])


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def add_identity(
    private_key_path: Path,
    cert_path: Path | None = None,
    lifetime: int = 300,
) -> None:
    """Add an ed25519 identity (with optional certificate) to ssh-agent.

    Builds the ``SSH_AGENTC_ADD_ID_CONSTRAINED`` message and sends it
    over the agent socket.  When *cert_path* is provided and the file
    exists, the certificate is attached so the agent presents the
    cert-based identity.  The identity is automatically removed by the
    agent after *lifetime* seconds.

    Args:
        private_key_path: Path to the ed25519 private key file.
        cert_path: Optional path to the corresponding certificate.
        lifetime: Seconds until the agent removes this identity
            (default 300 = 5 minutes).

    Raises:
        RuntimeError: If the agent is unreachable or refuses the key.
    """
    raw_seed, raw_pk = _get_ed25519_raw_keys(private_key_path)

    # The agent expects the private key as seed(32) || pk(32) = 64 bytes.
    sk_field = raw_seed + raw_pk

    payload = b""

    if cert_path and cert_path.is_file():
        # Certificate identity:
        #   string  cert_type  (e.g. "ssh-ed25519-cert-v01@openssh.com")
        #   string  cert_blob  (full certificate binary)
        #   string  pk_32
        #   string  sk_64      (seed || pk)
        #   string  comment
        cert_text = cert_path.read_text().strip()
        cert_type = cert_text.split()[0].encode()
        cert_blob = _get_cert_blob(cert_path)

        payload += _pack_string(cert_type)
        payload += _pack_string(cert_blob)
        payload += _pack_string(raw_pk)
        payload += _pack_string(sk_field)
    else:
        # Plain ed25519 identity:
        #   string  "ssh-ed25519"
        #   string  pk_32
        #   string  sk_64
        #   string  comment
        payload += _pack_string(b"ssh-ed25519")
        payload += _pack_string(raw_pk)
        payload += _pack_string(sk_field)

    payload += _pack_string(_AGENT_COMMENT)

    # Append lifetime constraint.
    payload += struct.pack(">BI", SSH_AGENT_CONSTRAIN_LIFETIME, lifetime)

    sock = _connect()
    try:
        resp_type, _ = _send_recv(sock, SSH_AGENTC_ADD_ID_CONSTRAINED, payload)
    finally:
        sock.close()

    if resp_type != SSH_AGENT_SUCCESS:
        raise RuntimeError(
            "ssh-agent refused to add the identity. "
            "Ensure the agent is running and accepts new keys."
        )


def remove_identity(key_blob: bytes) -> None:
    """Remove a single identity from ssh-agent by its public key blob.

    Sends ``SSH_AGENTC_REMOVE_IDENTITY``.  Silently succeeds when the
    identity is not loaded or the agent is unreachable.

    Args:
        key_blob: The public key blob in SSH wire format.
    """
    try:
        sock = _connect()
        try:
            payload = _pack_string(key_blob)
            _send_recv(sock, SSH_AGENTC_REMOVE_IDENTITY, payload)
        finally:
            sock.close()
    except RuntimeError:
        pass


def remove_rio_identities(public_key_path: Path) -> None:
    """Remove all agent identities associated with the rio key pair.

    Removes both the certificate-based identity and the plain-key
    identity.  Because ``sshkey_equal`` in the agent matches by the
    underlying key regardless of cert, we send the plain public-key
    blob twice — once for each potential entry.

    All errors are silently ignored (the identity may not be loaded,
    the agent may not be running, files may not exist).

    Args:
        public_key_path: Path to the public key file.
    """
    # The plain public-key blob matches both plain and cert identities
    # for the same underlying key.  Remove twice to cover both entries.
    try:
        if public_key_path.is_file():
            pk_blob = _get_key_blob(public_key_path)
            remove_identity(pk_blob)
            remove_identity(pk_blob)
    except Exception:
        pass

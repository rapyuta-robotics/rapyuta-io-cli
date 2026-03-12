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

"""SSH certificate management for ``rio ssh``.

Handles writing certificates to disk and parsing certificate metadata
(expiry, validity) using pure-Python binary parsing of the SSH
certificate wire format.

The wire format is defined in the OpenSSH PROTOCOL.certkeys document.
"""

from __future__ import annotations

import base64
import struct
from datetime import datetime, timezone
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pathlib import Path

# Number of length-prefixed public-key fields that appear between the
# nonce and the serial in each certificate type.  This table is used
# to skip past the key-type-specific data when parsing the certificate.
_CERT_PK_FIELDS: dict[bytes, int] = {
    b"ssh-rsa-cert-v01@openssh.com": 2,  # e, n
    b"ssh-dss-cert-v01@openssh.com": 4,  # p, q, g, y
    b"ssh-ed25519-cert-v01@openssh.com": 1,  # pk
    b"ecdsa-sha2-nistp256-cert-v01@openssh.com": 2,  # identifier, Q
    b"ecdsa-sha2-nistp384-cert-v01@openssh.com": 2,
    b"ecdsa-sha2-nistp521-cert-v01@openssh.com": 2,
    b"sk-ssh-ed25519-cert-v01@openssh.com": 2,  # pk, application
    b"sk-ecdsa-sha2-nistp256-cert-v01@openssh.com": 3,  # id, Q, app
}


def _read_string(data: bytes, pos: int) -> tuple[bytes, int]:
    """Read a uint32 length-prefixed string from SSH wire format."""
    length = struct.unpack(">I", data[pos : pos + 4])[0]
    pos += 4
    return data[pos : pos + length], pos + length


def _read_uint64(data: bytes, pos: int) -> tuple[int, int]:
    """Read a big-endian uint64."""
    val = struct.unpack(">Q", data[pos : pos + 8])[0]
    return val, pos + 8


def _read_uint32(data: bytes, pos: int) -> tuple[int, int]:
    """Read a big-endian uint32."""
    val = struct.unpack(">I", data[pos : pos + 4])[0]
    return val, pos + 4


def write_certificate(cert_path: Path, certificate: str) -> None:
    """Write the signed certificate to disk.

    Sets file permissions to ``0o644`` (readable by all, writable by
    owner) matching OpenSSH conventions for certificate files.

    Args:
        cert_path: Destination path.
        certificate: The certificate content to write.
    """
    cert_path.write_text(certificate + "\n")
    cert_path.chmod(0o644)


def parse_cert_valid_before(cert_path: Path) -> datetime | None:
    """Parse the ``valid_before`` timestamp from an SSH certificate.

    Decodes the certificate binary blob and walks the wire format to
    extract the ``valid_before`` uint64 Unix timestamp.  Returns a
    timezone-aware UTC :class:`~datetime.datetime`, or ``None`` if
    parsing fails for any reason.

    Args:
        cert_path: Path to the certificate file.

    Returns:
        The expiry as a UTC datetime, or ``None``.
    """
    try:
        parts = cert_path.read_text().strip().split()
        if len(parts) < 2:
            return None

        cert_blob = base64.b64decode(parts[1])
        pos = 0

        # 1. cert type string
        cert_type, pos = _read_string(cert_blob, pos)

        # 2. nonce
        _, pos = _read_string(cert_blob, pos)

        # 3. skip key-type-specific public key fields
        num_fields = _CERT_PK_FIELDS.get(cert_type)
        if num_fields is None:
            return None

        for _ in range(num_fields):
            _, pos = _read_string(cert_blob, pos)

        # 4. serial (uint64)
        _, pos = _read_uint64(cert_blob, pos)

        # 5. type (uint32) — 1=user, 2=host
        _, pos = _read_uint32(cert_blob, pos)

        # 6. key_id (string)
        _, pos = _read_string(cert_blob, pos)

        # 7. valid_principals (string, nested)
        _, pos = _read_string(cert_blob, pos)

        # 8. valid_after (uint64)
        _, pos = _read_uint64(cert_blob, pos)

        # 9. valid_before (uint64) — this is what we want
        valid_before, _ = _read_uint64(cert_blob, pos)

        return datetime.fromtimestamp(valid_before, tz=timezone.utc)

    except Exception:
        return None


def is_cert_valid(cert_path: Path) -> bool:
    """Check whether the certificate exists and has not yet expired.

    Compares the ``valid_before`` field (UTC) against the current UTC
    time.

    Args:
        cert_path: Path to the certificate file.

    Returns:
        ``True`` if the certificate exists and its expiry is in the
        future, ``False`` otherwise.
    """
    if not cert_path.is_file():
        return False

    expiry = parse_cert_valid_before(cert_path)
    if expiry is None:
        return False

    return datetime.now(tz=timezone.utc) < expiry


def format_cert_expiry(cert_path: Path) -> str | None:
    """Return a human-readable local-time expiry string.

    Converts the UTC ``valid_before`` to the system's local timezone
    and formats as an ISO-8601 string without timezone suffix (matching
    what ``ssh-keygen -Lf`` would display).

    Args:
        cert_path: Path to the certificate file.

    Returns:
        Expiry string like ``"2026-04-01T10:30:00"``, or ``None``.
    """
    expiry = parse_cert_valid_before(cert_path)
    if expiry is None:
        return None

    local_expiry = expiry.astimezone().replace(tzinfo=None)
    return local_expiry.isoformat(timespec="seconds")

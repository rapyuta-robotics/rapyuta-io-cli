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
(expiry, validity) using the ``cryptography`` library's
:class:`~cryptography.hazmat.primitives.serialization.ssh.SSHCertificate`
for structured certificate introspection.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import TYPE_CHECKING

from cryptography.hazmat.primitives.serialization import load_ssh_public_identity
from cryptography.hazmat.primitives.serialization.ssh import SSHCertificate

if TYPE_CHECKING:
    from pathlib import Path

#: ``valid_before`` sentinel meaning "never expires".
_FOREVER = 0xFFFFFFFFFFFFFFFF


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


def _load_certificate(cert_path: Path) -> SSHCertificate | None:
    """Load an SSH certificate from *cert_path*.

    Returns ``None`` when the file is missing, unreadable, or does not
    contain a valid SSH certificate.
    """
    try:
        data = cert_path.read_bytes()
        identity = load_ssh_public_identity(data)
        if isinstance(identity, SSHCertificate):
            return identity
        return None
    except Exception:
        return None


def parse_cert_valid_before(cert_path: Path) -> datetime | None:
    """Parse the ``valid_before`` timestamp from an SSH certificate.

    Uses the ``cryptography`` library to load the certificate and read
    its ``valid_before`` field.  Returns a timezone-aware UTC
    :class:`~datetime.datetime`, or ``None`` if the file is missing or
    cannot be parsed.

    Args:
        cert_path: Path to the certificate file.

    Returns:
        The expiry as a UTC datetime, or ``None``.
    """
    cert = _load_certificate(cert_path)
    if cert is None:
        return None

    ts = cert.valid_before
    if ts == _FOREVER:
        return datetime.max.replace(tzinfo=timezone.utc)

    return datetime.fromtimestamp(ts, tz=timezone.utc)


def is_cert_valid(cert_path: Path) -> bool:
    """Check whether the certificate exists and has not yet expired.

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
    and formats as an ISO-8601 string without timezone suffix.

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

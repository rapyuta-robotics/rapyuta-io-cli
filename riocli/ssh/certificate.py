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
(expiry, validity) by delegating to ``ssh-keygen -L`` rather than
implementing the binary wire format directly.
"""

from __future__ import annotations

import re
import subprocess
from datetime import datetime, timezone
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pathlib import Path


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

    Runs ``ssh-keygen -L -f <cert_path>`` and extracts the end time
    from the ``Valid:`` line.  Returns a timezone-aware UTC
    :class:`~datetime.datetime`, or ``None`` if parsing fails.

    Args:
        cert_path: Path to the certificate file.

    Returns:
        The expiry as a UTC datetime, or ``None``.
    """
    try:
        result = subprocess.run(
            ["ssh-keygen", "-L", "-f", str(cert_path)],
            capture_output=True,
            text=True,
        )
        if result.returncode != 0:
            return None

        return _parse_valid_before_from_output(result.stdout)

    except Exception:
        return None


def _parse_valid_before_from_output(output: str) -> datetime | None:
    """Extract the ``valid_before`` datetime from ssh-keygen -L output.

    The ``Valid:`` line has the format::

        Valid: from 2026-04-01T10:00:00 to 2026-04-01T10:05:00

    or with ``forever`` for never-expiring certificates.

    Args:
        output: Full stdout from ``ssh-keygen -L``.

    Returns:
        The expiry as a UTC datetime, or ``None``.
    """
    for line in output.splitlines():
        line = line.strip()
        if not line.startswith("Valid:"):
            continue

        # Handle "forever" sentinel (valid_before = 0xFFFFFFFFFFFFFFFF).
        if "forever" in line.lower():
            return datetime.max.replace(tzinfo=timezone.utc)

        # Extract the "to <timestamp>" portion.
        match = re.search(r"to\s+(\S+)", line)
        if not match:
            return None

        timestamp_str = match.group(1)
        return _parse_ssh_timestamp(timestamp_str)

    return None


def _parse_ssh_timestamp(timestamp_str: str) -> datetime | None:
    """Parse a timestamp string from ssh-keygen output.

    Handles ISO-8601 format (``2026-04-01T10:05:00``) as produced by
    modern OpenSSH.

    Args:
        timestamp_str: The timestamp string to parse.

    Returns:
        A timezone-aware UTC datetime, or ``None``.
    """
    try:
        # ssh-keygen produces local-time timestamps without tz info.
        # Parse as local time and convert to UTC.
        dt = datetime.strptime(timestamp_str, "%Y-%m-%dT%H:%M:%S")
        local_dt = dt.astimezone()
        return local_dt.astimezone(timezone.utc)
    except ValueError:
        return None


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

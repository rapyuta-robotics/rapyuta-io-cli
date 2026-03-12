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

"""Utility helpers for the ``rio ssh`` command.

Handles SSH key discovery, certificate file management, ``ssh-agent``
interaction, and certificate metadata parsing.
"""

from __future__ import annotations

import re
import subprocess
from pathlib import Path

# Preferred key types in discovery order (most modern first).
_KEY_PREFERENCE = [
    "id_ed25519",
    "id_ecdsa",
    "id_rsa",
]


def discover_ssh_public_key() -> Path:
    """Auto-detect the first available SSH public key.

    Searches ``~/.ssh/`` for public keys in the preferred order:
    ed25519 → ecdsa → rsa.

    Returns:
        Path to the discovered public key file.

    Raises:
        FileNotFoundError: When no known public key is found.
    """
    ssh_dir = Path.home() / ".ssh"
    for name in _KEY_PREFERENCE:
        pub = ssh_dir / f"{name}.pub"
        if pub.is_file():
            return pub

    raise FileNotFoundError(
        "No SSH public key found in ~/.ssh/. "
        "Generate one with `ssh-keygen` or pass --key explicitly."
    )


def derive_cert_path(pubkey_path: Path) -> Path:
    """Derive the OpenSSH-conventional certificate path.

    ``~/.ssh/id_ed25519.pub`` → ``~/.ssh/id_ed25519-cert.pub``

    Args:
        pubkey_path: Path to the public key file.

    Returns:
        Path where the certificate should be written.
    """
    stem = pubkey_path.stem  # e.g. "id_ed25519"
    return pubkey_path.parent / f"{stem}-cert.pub"


def derive_private_key_path(pubkey_path: Path) -> Path:
    """Derive the private key path from a public key path.

    Simply strips the ``.pub`` suffix.

    Args:
        pubkey_path: Path to the public key file.

    Returns:
        Path to the corresponding private key.

    Raises:
        FileNotFoundError: If the private key file does not exist.
    """
    private = pubkey_path.parent / pubkey_path.stem
    if not private.is_file():
        raise FileNotFoundError(
            f"Private key not found at {private}. "
            "Ensure the key pair exists or pass --key pointing to the .pub file."
        )
    return private


def read_public_key(pubkey_path: Path) -> str:
    """Read and return the contents of an SSH public key file.

    Args:
        pubkey_path: Path to the public key.

    Returns:
        The public key string.
    """
    return pubkey_path.read_text().strip()


def write_certificate(cert_path: Path, certificate: str) -> None:
    """Write the signed certificate to disk.

    Sets file permissions to ``0o644`` (readable by all, writable by owner)
    matching OpenSSH conventions for certificate files.

    Args:
        cert_path: Destination path.
        certificate: The certificate content to write.
    """
    cert_path.write_text(certificate + "\n")
    cert_path.chmod(0o644)


def add_to_ssh_agent(private_key_path: Path, lifetime: str = "5m") -> None:
    """Load an identity (private key + associated certificate) into ssh-agent.

    Runs ``ssh-add -t <lifetime> <private_key_path>``.  OpenSSH automatically
    picks up the matching ``-cert.pub`` file when it exists beside the private
    key.  The identity is automatically removed from the agent after *lifetime*
    expires.

    Args:
        private_key_path: Path to the private key.
        lifetime: How long the identity stays in the agent (default ``"5m"``).

    Raises:
        RuntimeError: If ``ssh-add`` fails (e.g. agent not running).
    """
    result = subprocess.run(
        ["ssh-add", "-t", lifetime, str(private_key_path)],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        stderr = result.stderr.strip()
        raise RuntimeError(
            f"Failed to add key to ssh-agent: {stderr}. "
            "Ensure ssh-agent is running (eval `ssh-agent -s`)."
        )


def get_cert_validity(cert_path: Path) -> str | None:
    """Parse the certificate to extract the *Valid* time range.

    Runs ``ssh-keygen -Lf <cert_path>`` and extracts the ``Valid:`` line.

    Args:
        cert_path: Path to the certificate file.

    Returns:
        The validity string (e.g. ``from 2026-03-12T12:00:00 to 2026-03-13T12:00:00``)
        or ``None`` if parsing fails.
    """
    try:
        result = subprocess.run(
            ["ssh-keygen", "-Lf", str(cert_path)],
            capture_output=True,
            text=True,
        )
        if result.returncode != 0:
            return None

        for line in result.stdout.splitlines():
            line = line.strip()
            if line.startswith("Valid:"):
                return line.removeprefix("Valid:").strip()

        return None
    except Exception:
        return None


def get_cert_expiry(cert_path: Path) -> str | None:
    """Extract only the expiry timestamp from the certificate.

    Args:
        cert_path: Path to the certificate file.

    Returns:
        The expiry timestamp string, or ``None`` if it cannot be determined.
    """
    validity = get_cert_validity(cert_path)
    if validity is None:
        return None

    # Format: "from <start> to <end>"
    match = re.search(r"to\s+(.+)", validity)
    if match:
        return match.group(1).strip()

    return None

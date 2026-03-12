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

"""SSH key pair management for ``rio ssh``.

Generates and manages a dedicated ed25519 key pair (``rio_ed25519``)
used exclusively for rapyuta.io SSH certificate authentication.
"""

from __future__ import annotations

from pathlib import Path

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

#: Base name for the dedicated key pair.
RIO_KEY_NAME = "rio_ed25519"


def get_rio_key_paths(
    ssh_dir: Path | None = None,
) -> tuple[Path, Path, Path]:
    """Return the (private, public, cert) paths for the rio key pair.

    Args:
        ssh_dir: Override for the SSH directory (default ``~/.ssh/``).

    Returns:
        Tuple of ``(private_key_path, public_key_path, cert_path)``.
    """
    if ssh_dir is None:
        ssh_dir = Path.home() / ".ssh"

    private_path = ssh_dir / RIO_KEY_NAME
    public_path = ssh_dir / f"{RIO_KEY_NAME}.pub"
    cert_path = ssh_dir / f"{RIO_KEY_NAME}-cert.pub"

    return private_path, public_path, cert_path


def ensure_rio_key_pair(
    ssh_dir: Path | None = None,
) -> tuple[Path, Path, Path, bool]:
    """Ensure the dedicated rio ed25519 key pair exists, creating if needed.

    The key pair is stored as ``~/.ssh/rio_ed25519`` (private) and
    ``~/.ssh/rio_ed25519.pub`` (public).  If both files already exist
    they are reused; otherwise a fresh ed25519 key pair is generated.

    Args:
        ssh_dir: Override for the SSH directory (default ``~/.ssh/``).

    Returns:
        Tuple of ``(private_path, public_path, cert_path, generated)``
        where *generated* is ``True`` when a new key pair was created.
    """
    private_path, public_path, cert_path = get_rio_key_paths(ssh_dir)

    # Ensure ~/.ssh/ exists with correct permissions.
    private_path.parent.mkdir(mode=0o700, parents=True, exist_ok=True)

    if private_path.is_file() and public_path.is_file():
        return private_path, public_path, cert_path, False

    # A leftover cert from a previous key pair is invalid for the
    # new key material — removing it to avoid cert/key mismatch.
    cert_path.unlink(missing_ok=True)

    # Generate a fresh ed25519 key pair.
    private_key = Ed25519PrivateKey.generate()

    private_bytes = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.OpenSSH,
        encryption_algorithm=serialization.NoEncryption(),
    )
    private_path.write_bytes(private_bytes)
    private_path.chmod(0o600)

    public_bytes = private_key.public_key().public_bytes(
        encoding=serialization.Encoding.OpenSSH,
        format=serialization.PublicFormat.OpenSSH,
    )
    public_path.write_bytes(public_bytes + b" rio-ssh\n")
    public_path.chmod(0o644)

    return private_path, public_path, cert_path, True


def read_public_key(pubkey_path: Path) -> str:
    """Read and return the contents of an SSH public key file.

    Args:
        pubkey_path: Path to the public key.

    Returns:
        The public key string (trimmed).
    """
    return pubkey_path.read_text().strip()

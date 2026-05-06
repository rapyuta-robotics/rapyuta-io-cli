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
stored in the CLI's configuration directory (``~/.config/rio-cli/``)
alongside the existing ``config.json`` file.

Key generation uses ``ssh-keygen`` rather than a Python cryptography
library, keeping the implementation simple and auditable.
"""

from __future__ import annotations

import subprocess
from pathlib import Path

from click import get_app_dir

from riocli.config.config import Configuration

#: Base name for the dedicated key pair.
RIO_KEY_NAME = "rio_ed25519"


def get_rio_key_dir(key_dir: Path | None = None) -> Path:
    """Return the directory used for rio SSH key material.

    Defaults to the CLI's configuration directory
    (``~/.config/rio-cli/``, via :func:`click.get_app_dir`).

    Args:
        key_dir: Override for testing.
    """
    if key_dir is not None:
        return key_dir
    return Path(get_app_dir(Configuration.APP_NAME))


def get_rio_key_paths(
    key_dir: Path | None = None,
) -> tuple[Path, Path, Path]:
    """Return the (private, public, cert) paths for the rio key pair.

    Args:
        key_dir: Override for the key directory.

    Returns:
        Tuple of ``(private_key_path, public_key_path, cert_path)``.
    """
    d = get_rio_key_dir(key_dir)
    private_path = d / RIO_KEY_NAME
    public_path = d / f"{RIO_KEY_NAME}.pub"
    cert_path = d / f"{RIO_KEY_NAME}-cert.pub"
    return private_path, public_path, cert_path


def ensure_rio_key_pair(
    key_dir: Path | None = None,
) -> tuple[Path, Path, Path, bool]:
    """Ensure the dedicated rio ed25519 key pair exists, creating if needed.

    The key pair is stored in ``~/.config/rio-cli/`` by default.
    If both files already exist they are reused; otherwise a fresh
    ed25519 key pair is generated via ``ssh-keygen``.

    Args:
        key_dir: Override for the key directory.

    Returns:
        Tuple of ``(private_path, public_path, cert_path, generated)``
        where *generated* is ``True`` when a new key pair was created.
    """
    private_path, public_path, cert_path = get_rio_key_paths(key_dir)

    # Ensure directory exists with correct permissions.
    private_path.parent.mkdir(mode=0o700, parents=True, exist_ok=True)

    if private_path.is_file() and public_path.is_file():
        return private_path, public_path, cert_path, False

    # Orphaned files from a previous key pair must be removed to
    # avoid cert/key mismatch and because ssh-keygen refuses to
    # overwrite an existing private key.
    private_path.unlink(missing_ok=True)
    public_path.unlink(missing_ok=True)
    cert_path.unlink(missing_ok=True)

    # Generate a fresh ed25519 key pair using ssh-keygen.
    result = subprocess.run(
        [
            "ssh-keygen",
            "-t",
            "ed25519",
            "-f",
            str(private_path),
            "-N",
            "",
            "-C",
            "rio-ssh",
            "-q",
        ],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        raise RuntimeError(f"ssh-keygen failed: {result.stderr.strip()}")

    # Ensure correct permissions (ssh-keygen normally sets these).
    private_path.chmod(0o600)
    public_path.chmod(0o644)

    return private_path, public_path, cert_path, True

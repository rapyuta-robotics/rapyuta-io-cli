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

"""SSH agent helpers for ``rio ssh``.

Wraps ``ssh-add`` to load and remove identities from a running
ssh-agent instance.
"""

from __future__ import annotations

import subprocess
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pathlib import Path


def add_to_ssh_agent(
    private_key_path: Path,
    lifetime: int = 300,
) -> None:
    """Add an SSH identity to ssh-agent with a TTL.

    Runs ``ssh-add -t <lifetime> <private_key_path>``.  When a
    matching ``*-cert.pub`` certificate file exists alongside the
    private key, ``ssh-add`` automatically picks it up.

    Args:
        private_key_path: Path to the private key file.
        lifetime: Seconds until the agent removes this identity
            (default 300 = 5 minutes).

    Raises:
        RuntimeError: If ``ssh-add`` fails (e.g. agent not running)
            or the ``ssh-add`` binary is not found.
    """
    try:
        result = subprocess.run(
            ["ssh-add", "-t", str(lifetime), str(private_key_path)],
            capture_output=True,
            text=True,
        )
    except FileNotFoundError:
        raise RuntimeError(
            "ssh-add not found. Ensure OpenSSH is installed and on your PATH."
        )

    if result.returncode != 0:
        stderr = result.stderr.strip()
        raise RuntimeError(
            f"Failed to add key to ssh-agent: {stderr}. "
            "Ensure ssh-agent is running (eval `ssh-agent -s`)."
        )


def remove_from_ssh_agent(private_key_path: Path) -> None:
    """Remove an SSH identity from ssh-agent.

    Runs ``ssh-add -d <private_key_path>``.  Silently succeeds when
    the identity is not loaded or the agent is unreachable.

    Args:
        private_key_path: Path to the private key file.
    """
    try:
        subprocess.run(
            ["ssh-add", "-d", str(private_key_path)],
            capture_output=True,
            text=True,
        )
    except (OSError, FileNotFoundError):
        pass

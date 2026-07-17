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

"""Lightweight, fast-starting SSH certificate renewal for ``Match exec``.

This module is the *fast path* equivalent of ``rio ssh-cert``.
It is invoked on **every** SSH connection that matches the wrapper's
``Match user ... exec`` block, so startup latency matters: importing the
full ``rio`` command tree (``riocli.bootstrap``) costs ~650ms because it
eagerly pulls in both SDKs and the ``apply`` subsystem.

To keep the common (no-renewal) path fast, this module lives at the top of
the ``riocli`` package — importing it runs only the tiny ``riocli/__init__``
— and imports nothing from ``riocli.ssh`` or ``riocli.config`` at module
scope.  The heavy SDK/config imports happen lazily, only inside the renewal
branch (the rare slow path).  Result: ~56ms instead of ~1.25s per connection.

The exported ``ensure_certificate`` function holds the shared logic; both the
standalone ``main`` here and the ``rio ssh-cert`` interactive flow
delegate to its utilities, so there is a single implementation of the
wrapper behaviour.

Exit codes (consumed by SSH's ``Match exec``):

    0   -> certificate is valid (or was just renewed); SSH uses it
    !0  -> fall back to the default SSH config
"""

from __future__ import annotations

import json
import os
from datetime import datetime, timedelta, timezone
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Callable
    from pathlib import Path

#: ``valid_before`` sentinel meaning "never expires".
_FOREVER = 0xFFFFFFFFFFFFFFFF

#: Renew if the certificate expires within this many seconds, leaving headroom
#: for the SSH handshake that follows this check.
_DEFAULT_MARGIN = 20
_MARGIN_ENV = "RIO_SSH_CERT_MARGIN"

#: Application name used to locate the rio-cli config directory.
_APP_NAME = "rio-cli"

#: Managed key / state / lock / log file names within the config directory.
_CERT_NAME = "rio_ed25519-cert.pub"
_STATE_NAME = "rio-ssh-cert.project"
_LOCK_NAME = "rio-ssh-cert.lock"
_LOG_NAME = "rio-ssh-cert.log"


def resolve_margin(margin: int | None) -> int:
    """Resolve the expiry margin from the flag, env var, or default.

    A negative or non-numeric value is ignored so a bad override cannot
    silently remove the handshake headroom.
    """
    if margin is not None:
        return margin if margin >= 0 else _DEFAULT_MARGIN

    raw = os.environ.get(_MARGIN_ENV)
    if raw is None:
        return _DEFAULT_MARGIN
    try:
        value = int(raw)
    except ValueError:
        return _DEFAULT_MARGIN
    return value if value >= 0 else _DEFAULT_MARGIN


def log(log_path: Path, message: str) -> None:
    """Append a timestamped line to the log file, swallowing any error."""
    try:
        stamp = datetime.now(tz=timezone.utc).isoformat(timespec="seconds")
        with log_path.open("a") as handle:
            handle.write(f"{stamp} {message}\n")
    except OSError:
        pass


def cert_valid(cert_path: Path, margin: int = 0) -> bool:
    """Return True if *cert_path* exists and is valid beyond *margin* seconds.

    Mirrors :func:`riocli.ssh.certificate.is_cert_valid` but imports
    ``cryptography`` lazily so the fast path stays cheap to start.
    """
    if not cert_path.is_file():
        return False

    # Imported here (not at module scope) to keep startup latency low.
    from cryptography.hazmat.primitives.serialization import (
        load_ssh_public_identity,
    )
    from cryptography.hazmat.primitives.serialization.ssh import SSHCertificate

    try:
        identity = load_ssh_public_identity(cert_path.read_bytes())
    except Exception:
        return False
    if not isinstance(identity, SSHCertificate):
        return False

    valid_before = identity.valid_before
    if valid_before == _FOREVER:
        return True

    expiry = datetime.fromtimestamp(valid_before, tz=timezone.utc)
    margin = max(margin, 0)
    return datetime.now(tz=timezone.utc) < expiry - timedelta(seconds=margin)


def read_saved_project(state_path: Path) -> str | None:
    """Return the saved project id, or ``None`` if unreadable/absent."""
    try:
        return state_path.read_text().strip() or None
    except OSError:
        return None


def save_project(state_path: Path, project_id: str) -> bool:
    """Persist *project_id* atomically.  Returns ``True`` on success."""
    tmp_path = state_path.with_suffix(state_path.suffix + ".tmp")
    try:
        tmp_path.write_text(project_id + "\n")
        os.replace(tmp_path, state_path)
        return True
    except OSError:
        tmp_path.unlink(missing_ok=True)
        return False


def _renew(
    cert_path: Path,
    config_dir: Path,
    project_id: str,
    sign_fn: Callable[[], None],
    margin: int,
) -> int:
    """Renew the certificate for *project_id* under an exclusive lock.

    *sign_fn* performs the actual signing and writes the certificate to
    *cert_path*; it must raise on failure.  Returns a process exit code.
    """
    state_path = config_dir / _STATE_NAME
    lock_path = config_dir / _LOCK_NAME
    log_path = config_dir / _LOG_NAME

    # fcntl is Unix-only; on Windows we skip file locking (concurrent
    # SSH connections may both renew, which is wasteful but not harmful).
    try:
        import fcntl as _fcntl
    except ImportError:
        _fcntl = None  # type: ignore[assignment]

    try:
        lock_handle = lock_path.open("a")
    except OSError as exc:
        log(log_path, f"cannot open lock file {lock_path}: {exc}")
        return 1

    try:
        if _fcntl is not None:
            _fcntl.flock(lock_handle, _fcntl.LOCK_EX)

        # Another connection may have renewed while we waited for the lock.
        if (
            cert_valid(cert_path, margin=margin)
            and read_saved_project(state_path) == project_id
        ):
            return 0

        log(log_path, f"renewing certificate for project {project_id}")
        try:
            sign_fn()
        except Exception as exc:
            log(log_path, f"renewal failed: {exc}")
            return 1

        # Confirm the freshly written certificate is actually valid before
        # trusting it (no margin here — it was just issued).
        if not cert_valid(cert_path):
            log(log_path, "signing reported success but certificate is invalid")
            return 1

        # Persist the project id only after a confirmed successful renewal.
        if not save_project(state_path, project_id):
            log(log_path, "renewal succeeded but could not persist project id")
            return 1

        log(log_path, f"renewal succeeded for project {project_id}")
        return 0
    finally:
        if _fcntl is not None:
            _fcntl.flock(lock_handle, _fcntl.LOCK_UN)
        lock_handle.close()


def ensure_certificate(
    *,
    cert_path: Path,
    config_dir: Path,
    project_id: str | None,
    sign_fn: Callable[[], None],
    margin: int,
) -> int:
    """Ensure a valid certificate exists for *project_id*, renewing if needed.

    Shared core for both the standalone entry point and the
    ``rio ssh-cert`` interactive flow.  Returns a process exit
    code (0 = certificate ready, non-zero = fall back to default SSH config).
    """
    try:
        config_dir.mkdir(mode=0o700, parents=True, exist_ok=True)
    except OSError:
        # Match exec must never crash SSH — fall back to default config.
        return 1

    log_path = config_dir / _LOG_NAME
    state_path = config_dir / _STATE_NAME

    if not project_id:
        log(log_path, "no project_id set in rio-cli config")
        return 1

    # Fast path: a valid certificate already exists for the current project.
    if (
        cert_valid(cert_path, margin=margin)
        and read_saved_project(state_path) == project_id
    ):
        return 0

    return _renew(cert_path, config_dir, project_id, sign_fn, margin)


# --------------------------------------------------------------------------
# Standalone entry point (rio-ssh-ensure-cert) — used by the SSH Match exec.
# --------------------------------------------------------------------------


def _config_dir() -> Path:
    """Resolve the rio-cli config directory without importing the CLI tree."""
    from pathlib import Path

    import click  # light (~50ms); only here, not at module scope.

    return Path(click.get_app_dir(_APP_NAME))


def _read_project_id(config_dir: Path) -> str | None:
    """Read ``project_id`` directly from ``config.json`` (no SDK import).

    Honours the ``RIO_CONFIG`` override the same way the CLI does.
    """
    config_path = config_dir / "config.json"
    override = os.environ.get("RIO_CONFIG")
    if override:
        from pathlib import Path

        config_path = Path(override)

    try:
        data = json.loads(config_path.read_text())
    except (OSError, ValueError):
        return None
    project_id = data.get("project_id")
    return project_id or None


def _build_sign_fn(cert_path: Path) -> Callable[[], None]:
    """Return a callable that signs the managed key (lazy SDK import)."""

    def sign() -> None:
        # Heavy imports confined to the slow path (actual renewal only).
        from rapyuta_io_sdk_v2 import SSHKeySignRequest

        from riocli.config.config import Configuration
        from riocli.ssh.certificate import write_certificate

        config = Configuration()
        config.ensure_ssh_keys()
        public_key = config.ssh_public_key.read_text().strip()
        client = config.new_v2_client()
        response = client.sign_ssh_public_key(
            body=SSHKeySignRequest(publicKey=public_key)
        )
        write_certificate(cert_path, response.certificate)

    return sign


def main(argv: list[str] | None = None) -> int:
    """Standalone CLI entry point for ``rio-ssh-ensure-cert``."""
    import argparse

    parser = argparse.ArgumentParser(
        prog="rio-ssh-ensure-cert",
        description="Silently ensure a valid rio SSH certificate (fast path).",
    )
    parser.add_argument(
        "--margin",
        type=int,
        default=None,
        help=(
            "Renew if the certificate expires within this many seconds "
            f"(default {_DEFAULT_MARGIN}; overridable via ${_MARGIN_ENV})."
        ),
    )
    args = parser.parse_args(argv)

    config_dir = _config_dir()
    cert_path = config_dir / _CERT_NAME
    project_id = _read_project_id(config_dir)

    return ensure_certificate(
        cert_path=cert_path,
        config_dir=config_dir,
        project_id=project_id,
        sign_fn=_build_sign_fn(cert_path),
        margin=resolve_margin(args.margin),
    )


if __name__ == "__main__":
    raise SystemExit(main())

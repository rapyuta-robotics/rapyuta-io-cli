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

"""``rio ssh-cert install-wrapper`` – install the transparent SSH cert-renewal wrapper."""

from __future__ import annotations

import re
import shutil
from pathlib import Path

import click
from click_help_colors import HelpColorsCommand

from riocli.constants import Colors, Symbols

_SSH_USER_RE = re.compile(r"^[A-Za-z0-9._-]+$")

# Sentinel written inside ~/.ssh/config so we can detect a managed block.
_INCLUDE_LINE = "Include config.d/rio-ssh.conf"
_MANAGED_BEGIN = "# >>> rio ssh-cert (managed) >>>"
_MANAGED_END = "# <<< rio ssh-cert (managed) <<<"

_CONF_TEMPLATE = """\
# Managed by rio ssh-cert install-wrapper. Do not edit by hand.
#
# For the matching login accounts, run cert renewal before connecting.
# If it exits 0 the certificate is valid (or was just renewed) and SSH
# uses it; otherwise SSH falls back to defaults.
Match user {ssh_user} exec "rio ssh-cert --no-agent"
    IdentityFile    {identity_file}
    CertificateFile {certificate_file}
    IdentitiesOnly  yes
"""


@click.command(
    "install-wrapper",
    cls=HelpColorsCommand,
    help_headers_color=Colors.YELLOW,
    help_options_color=Colors.GREEN,
)
@click.option(
    "--ssh-user",
    "ssh_user",
    default="rr",
    show_default=True,
    help="Remote username to match in the SSH config (the account you ssh into).",
)
@click.option(
    "--force",
    is_flag=True,
    default=False,
    help="Overwrite an existing rio-ssh.conf even if one is already present.",
)
def install_wrapper(ssh_user: str, force: bool) -> None:
    """Install the transparent SSH certificate-renewal wrapper.

    Writes ``~/.ssh/config.d/rio-ssh.conf`` and injects an ``Include``
    directive into ``~/.ssh/config`` so that every ``ssh <ssh-user>@<host>``
    automatically renews the certificate when needed — no manual
    ``rio ssh-cert`` required.

    The SSH ``Match exec`` clause calls ``rio ssh-cert --no-agent`` directly.
    For a more robust wrapper with project-id tracking, flock-based concurrency
    protection, and expiry-margin support, see the standalone shell wrapper at
    https://github.com/rapyuta-robotics/rr-rio-ssh-wrapper.

    \b
    Examples:
        $ rio ssh-cert install-wrapper
        $ rio ssh-cert install-wrapper --ssh-user rr
        $ rio ssh-cert install-wrapper --force
    """
    if not _SSH_USER_RE.match(ssh_user):
        click.secho(
            f"{Symbols.ERROR} Invalid --ssh-user value '{ssh_user}'. "
            "Only letters, digits, '.', '_', and '-' are allowed.",
            fg=Colors.RED,
        )
        raise SystemExit(1)

    if shutil.which("rio") is None:
        click.secho(
            f"{Symbols.ERROR} rio not found on PATH. "
            "Ensure the rio-cli package is installed and on your PATH.",
            fg=Colors.RED,
        )
        raise SystemExit(1)

    ssh_dir = Path.home() / ".ssh"
    conf_dir = ssh_dir / "config.d"
    conf_file = conf_dir / "rio-ssh.conf"
    ssh_config = ssh_dir / "config"

    # Resolve identity/cert paths from the cli config directory.
    app_dir = Path(click.get_app_dir("rio-cli"))
    identity_file = app_dir / "rio_ed25519"
    certificate_file = app_dir / "rio_ed25519-cert.pub"

    # ----- 1. Create config.d/ directory ----- #
    conf_dir.mkdir(mode=0o700, parents=True, exist_ok=True)

    # ----- 2. Write rio-ssh.conf ----- #
    if conf_file.exists() and not force:
        click.secho(
            f"{Symbols.INFO} {conf_file} already exists; use --force to overwrite.",
            fg=Colors.CYAN,
        )
    else:
        conf_file.write_text(
            _CONF_TEMPLATE.format(
                ssh_user=ssh_user,
                identity_file=identity_file,
                certificate_file=certificate_file,
            )
        )
        conf_file.chmod(0o600)
        click.secho(
            f"{Symbols.SUCCESS} Written: {conf_file}",
            fg=Colors.GREEN,
        )

    # ----- 3. Inject Include into ~/.ssh/config ----- #
    _inject_include(ssh_config)

    click.secho(
        f"\n{Symbols.SUCCESS} Installation complete. "
        f"SSH connections as '{ssh_user}' will now auto-renew the certificate.",
        fg=Colors.GREEN,
    )


def _inject_include(ssh_config: Path) -> None:
    """Ensure the managed Include block exists in *ssh_config*.

    Idempotent — does nothing if the block is already present.
    """
    managed_block = f"{_MANAGED_BEGIN}\n{_INCLUDE_LINE}\n{_MANAGED_END}\n"

    if ssh_config.exists():
        existing = ssh_config.read_text()
        if _MANAGED_BEGIN in existing:
            click.secho(
                f"{Symbols.INFO} {ssh_config} already contains the managed block; skipping.",
                fg=Colors.CYAN,
            )
            return
        # Prepend so the Include is processed before any other rules.
        ssh_config.write_text(managed_block + "\n" + existing)
    else:
        ssh_config.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
        ssh_config.write_text(managed_block + "\n")
        ssh_config.chmod(0o600)

    click.secho(
        f"{Symbols.SUCCESS} Injected Include directive into {ssh_config}",
        fg=Colors.GREEN,
    )

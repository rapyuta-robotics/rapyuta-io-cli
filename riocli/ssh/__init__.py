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

"""``rio ssh-cert`` – sign an SSH public key and optionally install the wrapper.

When invoked with no subcommand, signs the SSH public key and loads the
certificate into ssh-agent.  Pass ``install-wrapper`` as a subcommand to
set up transparent automatic renewal.
"""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

import click
from rapyuta_io_sdk_v2 import SSHKeySignRequest

from riocli.config import get_config_from_context

if TYPE_CHECKING:
    from yaspin.api import Yaspin
from riocli.constants import Colors, Symbols
from riocli.ssh.certificate import (
    format_cert_expiry,
    is_cert_valid,
    write_certificate,
)
from riocli.ssh.install_wrapper import install_wrapper
from riocli.ssh.util import (
    add_to_ssh_agent,
    is_ssh_agent_available,
    remove_from_ssh_agent,
)
from riocli.ssh_ensure_cert import (
    _STATE_NAME,
    read_saved_project,
    resolve_margin,
    save_project,
)
from riocli.utils import AliasedGroup
from riocli.utils.spinner import with_spinner

_SYSTEM_KEY_NAMES = ("id_ed25519", "id_ecdsa", "id_rsa")


def _resolve_key_paths(key_path, use_system_key, config):
    """Return (private_path, public_path, cert_path, should_generate).

    should_generate=True means the caller must invoke config.ensure_ssh_keys().
    """
    if key_path is None and not use_system_key:
        return config.ssh_private_key, config.ssh_public_key, config.ssh_certificate, True

    if use_system_key:
        ssh_dir = Path.home() / ".ssh"
        for name in _SYSTEM_KEY_NAMES:
            priv = ssh_dir / name
            pub = ssh_dir / f"{name}.pub"
            if priv.is_file() and pub.is_file():
                return priv, pub, ssh_dir / f"{name}-cert.pub", False
        # No system key found — fall back to the rio-cli managed key.
        return config.ssh_private_key, config.ssh_public_key, config.ssh_certificate, True

    priv = Path(key_path)
    pub = priv.parent / f"{priv.name}.pub"
    cert = priv.parent / f"{priv.name}-cert.pub"
    return priv, pub, cert, False


@with_spinner(text="Signing SSH public key...")
def _do_sign_cert(
    ctx: click.Context,
    agent: bool,
    force: bool,
    use_system_key: bool,
    key_path: str | None,
    spinner: Yaspin = None,  # type: ignore[assignment]  # injected by @with_spinner
) -> None:
    try:
        config = get_config_from_context(ctx)

        # ----- 1. Resolve key paths ----- #
        private_path, public_path, cert_path, should_generate = _resolve_key_paths(
            key_path, use_system_key, config
        )

        if use_system_key and not should_generate:
            spinner.write(
                click.style(
                    f"{Symbols.INFO} Using system key: {private_path}",
                    fg=Colors.CYAN,
                )
            )
        elif use_system_key and should_generate:
            spinner.write(
                click.style(
                    f"{Symbols.INFO} No system keys found in ~/.ssh/; "
                    "falling back to rio-cli managed key.",
                    fg=Colors.CYAN,
                )
            )

        if should_generate:
            generated = config.ensure_ssh_keys()
            if generated:
                spinner.write(
                    click.style(
                        f"{Symbols.SUCCESS} Generated dedicated key pair: {public_path}",
                        fg=Colors.GREEN,
                    )
                )
        else:
            if not private_path.is_file():
                raise FileNotFoundError(f"SSH private key not found: {private_path}")
            if not public_path.is_file():
                raise FileNotFoundError(f"SSH public key not found: {public_path}")

        # ----- 2. Check ssh-agent availability once ----- #
        # For --use-system-key and --key-path, agent loading is opt-in: only load
        # if --agent was explicitly passed.  The vanilla managed-key case loads by
        # default (agent=True unless --no-agent is given).
        using_custom_key = use_system_key or key_path is not None
        agent_explicitly_set = (
            ctx.get_parameter_source("agent") == click.core.ParameterSource.COMMANDLINE
        )
        use_agent = agent if not using_custom_key else (agent and agent_explicitly_set)
        agent_available = use_agent and is_ssh_agent_available()
        if use_agent and not agent_available:
            spinner.write(
                click.style(
                    f"{Symbols.INFO} No ssh-agent detected (SSH_AUTH_SOCK not set); "
                    "skipping agent load.",
                    fg=Colors.CYAN,
                )
            )

        # ----- 3. Reuse existing cert if still valid ----- #
        # Project-id tracking: detect when the user switches projects.
        app_dir = config.ssh_certificate.parent
        state_path = app_dir / _STATE_NAME
        project_id = config.data.get("project_id")
        margin = resolve_margin(None)

        project_matches = (not project_id) or read_saved_project(state_path) == project_id
        if not force and is_cert_valid(cert_path, margin=margin) and project_matches:
            expiry = format_cert_expiry(cert_path)
            spinner.write(
                click.style(
                    f"{Symbols.INFO} Existing certificate is still valid"
                    + (f" (until {expiry})" if expiry else ""),
                    fg=Colors.CYAN,
                )
            )

            if agent_available:
                try:
                    remove_from_ssh_agent(private_path)
                    add_to_ssh_agent(private_path)
                    spinner.write(
                        click.style(
                            f"{Symbols.SUCCESS} Identity loaded into ssh-agent "
                            f"(5m TTL): {private_path}",
                            fg=Colors.GREEN,
                        )
                    )
                except RuntimeError as agent_err:
                    spinner.write(
                        click.style(
                            f"{Symbols.WARNING} {agent_err}",
                            fg=Colors.YELLOW,
                        )
                    )

            spinner.ok(Symbols.SUCCESS)
            return

        # ----- 4. Read the public key ----- #
        public_key = public_path.read_text().strip()

        spinner.write(
            click.style(
                f"{Symbols.INFO} Using SSH public key: {public_path}",
                fg=Colors.CYAN,
            )
        )

        # ----- 5. Call the SDK to sign the key ----- #
        client = config.new_v2_client()
        request = SSHKeySignRequest(publicKey=public_key)
        response = client.sign_ssh_public_key(body=request)

        # ----- 6. Remove old identity & write the new certificate ----- #
        # Remove BEFORE overwriting the cert file so the old identity
        # still matches what is loaded in the agent.
        if agent_available:
            remove_from_ssh_agent(private_path)

        write_certificate(cert_path, response.certificate)

        # Save project id after successful renewal so next run can fast-path.
        if project_id:
            save_project(state_path, project_id)

        spinner.write(
            click.style(
                f"{Symbols.SUCCESS} SSH certificate written: {cert_path}",
                fg=Colors.GREEN,
            )
        )

        # ----- 7. Load into ssh-agent with 5-minute TTL ----- #
        if agent_available:
            try:
                add_to_ssh_agent(private_path)
                spinner.write(
                    click.style(
                        f"{Symbols.SUCCESS} Identity loaded into ssh-agent "
                        f"(5m TTL): {private_path}",
                        fg=Colors.GREEN,
                    )
                )
            except RuntimeError as agent_err:
                spinner.write(
                    click.style(
                        f"{Symbols.WARNING} {agent_err}",
                        fg=Colors.YELLOW,
                    )
                )

        # ----- 8. Print certificate expiry ----- #
        expiry = format_cert_expiry(cert_path)
        if expiry:
            spinner.write(
                click.style(
                    f"{Symbols.INFO} Certificate valid until: {expiry}",
                    fg=Colors.CYAN,
                )
            )

        spinner.ok(Symbols.SUCCESS)

    except (FileNotFoundError, RuntimeError) as e:
        spinner.fail(Symbols.ERROR)
        click.secho(str(e), fg=Colors.RED)
        raise SystemExit(1) from e
    except Exception as e:
        spinner.fail(Symbols.ERROR)
        click.secho(
            f"Failed to generate or load SSH certificate: {e}",
            fg=Colors.RED,
        )
        raise SystemExit(1) from e


@click.group(
    "ssh-cert",
    cls=AliasedGroup,
    help_headers_color=Colors.YELLOW,
    help_options_color=Colors.GREEN,
    invoke_without_command=True,
)
@click.option(
    "--agent/--no-agent",
    "agent",
    default=True,
    help="Load (or skip loading) the identity into ssh-agent.",
)
@click.option(
    "--force",
    "-f",
    is_flag=True,
    default=False,
    help="Re-sign the certificate even if the existing one is still valid.",
)
@click.option(
    "--use-system-key",
    "use_system_key",
    is_flag=True,
    default=False,
    help=(
        "Search ~/.ssh/ for an existing key pair (id_ed25519, id_ecdsa, id_rsa) "
        "and sign that instead of the rio-cli managed key. "
        "Falls back to the managed key if no system key is found. "
        "Does not load into ssh-agent unless --agent is also passed."
    ),
)
@click.option(
    "--key-path",
    "key_path",
    default=None,
    type=click.Path(exists=True, file_okay=True, dir_okay=False, resolve_path=True),
    help=(
        "Path to a specific SSH private key to sign. "
        "Expects PATH.pub alongside it; errors if either file is missing. "
        "Does not load into ssh-agent unless --agent is also passed."
    ),
)
@click.pass_context
def ssh_cert(
    ctx: click.Context,
    agent: bool,
    force: bool,
    use_system_key: bool,
    key_path: str | None,
) -> None:
    """Sign your SSH public key and optionally load the certificate into ssh-agent.

    Uses a dedicated ``rio_ed25519`` key pair by default (auto-generated
    on first run).  Pass ``--use-system-key`` to sign an existing key from
    ``~/.ssh/``, or ``--key-path PATH`` to sign a specific key.

    Agent loading is enabled by default for the managed key, but opt-in
    (requires explicit ``--agent``) when ``--use-system-key`` or
    ``--key-path`` is used.

    \b
    Examples:
        $ rio ssh-cert
        $ rio ssh-cert --use-system-key
        $ rio ssh-cert --use-system-key --agent
        $ rio ssh-cert --key-path ~/.ssh/id_ed25519
        $ rio ssh-cert --key-path ~/.ssh/id_ed25519 --agent
        $ rio ssh-cert --no-agent
        $ rio ssh-cert --force
        $ rio ssh-cert install-wrapper
        $ rio ssh-cert install-wrapper --ssh-user rr
    """
    if ctx.invoked_subcommand is not None:
        return

    if use_system_key and key_path is not None:
        ctx.fail("--use-system-key and --key-path are mutually exclusive.")

    _do_sign_cert(ctx, agent, force, use_system_key, key_path)


ssh_cert.add_command(install_wrapper)


def refresh_ssh_cert(ctx: click.Context) -> None:
    """Re-issue the SSH certificate for the currently selected project.

    Shared by ``rio project select`` and ``rio organization select`` so a
    project/org switch always carries a matching certificate. Failure is
    non-fatal: a warning is shown so the caller's own success message
    still stands even if cert renewal fails.
    """
    try:
        ctx.invoke(ssh_cert, force=True, agent=True, use_system_key=False, key_path=None)
    except SystemExit as e:
        if e.code != 0:
            click.secho(
                f"{Symbols.WARNING} SSH certificate renewal failed. "
                "Run 'rio ssh-cert --force' manually.",
                fg=Colors.YELLOW,
            )

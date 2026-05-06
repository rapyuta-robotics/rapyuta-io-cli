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

"""``rio ssh`` – sign an SSH public key and load the certificate into ssh-agent.

Generates a dedicated ``rio_ed25519`` key pair (if not already present),
requests a signed SSH user certificate from rapyuta.io, writes it to
``<app-dir>/rio_ed25519-cert.pub``, and loads the identity into
``ssh-agent`` with a 5-minute TTL for immediate use.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import click
from click_help_colors import HelpColorsCommand
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
from riocli.ssh.keys import ensure_rio_key_pair
from riocli.ssh.util import add_to_ssh_agent, remove_from_ssh_agent
from riocli.utils.spinner import with_spinner


@click.command(
    "ssh",
    cls=HelpColorsCommand,
    help_headers_color=Colors.YELLOW,
    help_options_color=Colors.GREEN,
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
@click.pass_context
@with_spinner(text="Signing SSH public key...")
def ssh(
    ctx: click.Context,
    agent: bool,
    force: bool,
    spinner: Yaspin = None,  # type: ignore[assignment]  # injected by @with_spinner
) -> None:
    """Sign your SSH public key and load the certificate into ssh-agent.

    Uses a dedicated ``rio_ed25519`` key pair (auto-generated on first
    run).  The signed certificate and key are loaded into ssh-agent
    with a 5-minute TTL so they expire automatically without affecting
    your other SSH identities.

    \b
    Examples:
        $ rio ssh
        $ rio ssh --no-agent
        $ rio ssh --force
    """
    try:
        # ----- 1. Ensure dedicated key pair exists ----- #
        private_path, public_path, cert_path, generated = ensure_rio_key_pair()

        if generated:
            spinner.write(
                click.style(
                    f"{Symbols.SUCCESS} Generated dedicated key pair: {public_path}",
                    fg=Colors.GREEN,
                )
            )

        # ----- 2. Reuse existing cert if still valid ----- #
        if is_cert_valid(cert_path) and not force:
            expiry = format_cert_expiry(cert_path)
            spinner.write(
                click.style(
                    f"{Symbols.INFO} Existing certificate is still valid"
                    + (f" (until {expiry})" if expiry else ""),
                    fg=Colors.CYAN,
                )
            )

            if agent:
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

        # ----- 3. Read the public key ----- #
        public_key = public_path.read_text().strip()

        spinner.write(
            click.style(
                f"{Symbols.INFO} Using SSH public key: {public_path}",
                fg=Colors.CYAN,
            )
        )

        # ----- 4. Call the SDK to sign the key ----- #
        config = get_config_from_context(ctx)
        client = config.new_v2_client()
        request = SSHKeySignRequest(publicKey=public_key)
        response = client.sign_ssh_public_key(body=request)

        # ----- 5. Remove old identity & write the new certificate ----- #
        # Remove BEFORE overwriting the cert file so the old identity
        # still matches what is loaded in the agent.
        if agent:
            remove_from_ssh_agent(private_path)

        write_certificate(cert_path, response.certificate)

        spinner.write(
            click.style(
                f"{Symbols.SUCCESS} SSH certificate written: {cert_path}",
                fg=Colors.GREEN,
            )
        )

        # ----- 6. Load into ssh-agent with 5-minute TTL ----- #
        if agent:
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

        # ----- 7. Print certificate expiry ----- #
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

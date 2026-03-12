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

Discovers the user's SSH key pair, requests a signed SSH user certificate
from rapyuta.io, writes it to the conventional ``<key>-cert.pub`` path, and
loads the identity into ``ssh-agent`` for immediate use.
"""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

import click
from click_help_colors import HelpColorsCommand
from rapyuta_io_sdk_v2 import SSHKeySignRequest

from riocli.config import new_v2_client

if TYPE_CHECKING:
    from yaspin.api import Yaspin
from riocli.constants import Colors, Symbols
from riocli.ssh.util import (
    add_to_ssh_agent,
    derive_cert_path,
    derive_private_key_path,
    discover_ssh_public_key,
    get_cert_expiry,
    read_public_key,
    write_certificate,
)
from riocli.utils.spinner import with_spinner


@click.command(
    "ssh",
    cls=HelpColorsCommand,
    help_headers_color=Colors.YELLOW,
    help_options_color=Colors.GREEN,
)
@click.option(
    "--key",
    "key_file",
    type=click.Path(exists=True, dir_okay=False),
    default=None,
    help="Path to the SSH public key file. "
    "Auto-detects ed25519/ecdsa/rsa from ~/.ssh/ when omitted.",
)
@click.option(
    "--no-agent",
    "no_agent",
    is_flag=True,
    default=False,
    help="Skip loading the identity into ssh-agent.",
)
@click.option(
    "--force",
    "-f",
    is_flag=True,
    default=False,
    help="Overwrite an existing certificate without prompting.",
)
@click.option(
    "--user-guid",
    "user_guid",
    type=str,
    default=None,
    hidden=True,
    help="Sign the key on behalf of a specific user (admin use).",
)
@click.pass_context
@with_spinner(text="Signing SSH public key...")
def ssh(
    ctx: click.Context,
    key_file: str | None,
    no_agent: bool,
    force: bool,
    user_guid: str | None,
    spinner: Yaspin = None,
) -> None:
    """Sign your SSH public key and load the certificate into ssh-agent.

    Discovers your SSH key pair, sends the public key to rapyuta.io for
    signing, writes the certificate next to the key, and loads the
    identity into ssh-agent so you can SSH immediately.

    \b
    Examples:
        $ rio ssh
        $ rio ssh --key ~/.ssh/id_ed25519.pub
        $ rio ssh --no-agent
        $ rio ssh --force
    """
    try:
        # ----- 1. Discover / validate key paths ----- #
        if key_file:
            pubkey_path = Path(key_file).expanduser().resolve()
        else:
            pubkey_path = discover_ssh_public_key()

        private_key_path = derive_private_key_path(pubkey_path)
        cert_path = derive_cert_path(pubkey_path)

        # Guard against silent overwrite.
        if cert_path.exists() and not force:
            spinner.write(
                click.style(
                    f"{Symbols.WARNING} Certificate already exists at {cert_path}",
                    fg=Colors.YELLOW,
                )
            )
            click.confirm("Overwrite?", abort=True, default=True)

        # ----- 2. Read the public key ----- #
        public_key = read_public_key(pubkey_path)

        spinner.write(
            click.style(
                f"{Symbols.INFO} Using SSH public key: {pubkey_path}",
                fg=Colors.CYAN,
            )
        )

        # ----- 3. Call the SDK to sign the key ----- #
        client = new_v2_client()
        request = SSHKeySignRequest(publicKey=public_key)
        response = client.sign_ssh_public_key(body=request, user_guid=user_guid)

        # ----- 4. Write the certificate ----- #
        write_certificate(cert_path, response.certificate)

        spinner.write(
            click.style(
                f"{Symbols.SUCCESS} SSH certificate written: {cert_path}",
                fg=Colors.GREEN,
            )
        )

        # ----- 5. Load into ssh-agent ----- #
        if not no_agent:
            try:
                add_to_ssh_agent(private_key_path)
                spinner.write(
                    click.style(
                        f"{Symbols.SUCCESS} Identity loaded into ssh-agent: {private_key_path}",
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

        # ----- 6. Print certificate expiry ----- #
        expiry = get_cert_expiry(cert_path)
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
    except click.Abort:
        spinner.fail(Symbols.ERROR)
        click.secho("Aborted.", fg=Colors.YELLOW)
        raise SystemExit(1)
    except Exception as e:
        spinner.fail(Symbols.ERROR)
        click.secho(f"Failed to sign SSH key: {e}", fg=Colors.RED)
        raise SystemExit(1) from e

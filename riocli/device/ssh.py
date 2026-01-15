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
# riocli/device/ssh.py

import os
import subprocess
import tempfile
import sys

import click
from click_help_colors import HelpColorsCommand

from riocli.config import get_config_from_context
from riocli.constants import Colors
from riocli.device.util import get_ephemeral_creds


@click.command(
    "ssh",
    cls=HelpColorsCommand,
    help_headers_color=Colors.YELLOW,
    help_options_color=Colors.GREEN,
)
@click.argument("target", type=str)
@click.pass_context
def ssh(ctx: click.Context, target: str) -> None:
    """
    SSH into a device using ephemeral certificates.

    This command expects the standard SSH target format:
    
        rio device ssh <username>@<device-ip>

    Example:
        rio device ssh root@10.81.1.50

        
        rio device ssh rapyuta@192.168.0.105

    It authenticates you via OIDC for your current project, issues a
    short-lived certificate, and connects immediately.
    """
    # 1. Strict Validation of Input Format
    if "@" not in target:
        click.secho(
            "Error: Invalid format. Please use '<username>@<ip-address>'.", 
            fg=Colors.RED
        )
        click.secho("Example: rio device ssh root@192.168.1.10", fg=Colors.YELLOW)
        sys.exit(1)

    username, host = target.split("@", 1)

    if not username or not host:
        click.secho("Error: Missing username or host.", fg=Colors.RED)
        sys.exit(1)

    try:
        # 2. Get Project Context
        config = get_config_from_context(ctx)
        project_id = config.data.get("project_id")

        if not project_id:
            raise Exception("No Project ID found in the current context. Please login or set a project.")

        click.secho(f"Authenticating for Project: {project_id}...", fg=Colors.YELLOW)

        # 3. Get Ephemeral Credentials
        # This triggers the OIDC browser login + Step CA signing flow
        key_pem, cert_pem = get_ephemeral_creds(project_id=project_id)

        # 4. SSH Session
        # We use TemporaryDirectory to ensure keys are wiped even if the script crashes
        with tempfile.TemporaryDirectory() as tmp_dir:
            key_path = os.path.join(tmp_dir, "id_ec")
            cert_path = key_path + "-cert.pub"

            # Write keys to secure temp files
            with open(key_path, "w") as f:
                f.write(key_pem)
            with open(cert_path, "w") as f:
                f.write(cert_pem)
            
            # CRITICAL: SSH requires private keys to be read-only (0600)
            os.chmod(key_path, 0o600)

            click.secho(f"Connecting to {username}@{host}...", fg=Colors.GREEN)
            
            ssh_cmd = [
                "ssh", 
                "-i", key_path,                       # Use ephemeral private key
                "-o", f"CertificateFile={cert_path}", # Use signed certificate
                "-o", "IdentitiesOnly=yes",           # Ignore other keys in ssh-agent
                "-o", "StrictHostKeyChecking=no",     # Suppress "Unknown Host" prompts for ephemeral IPs
                "-o", "UserKnownHostsFile=/dev/null", # Don't pollute known_hosts
                f"{username}@{host}"
            ]
            # ... after writing the cert_path ...
            click.secho("DEBUG: Inspecting the issued certificate:", fg=Colors.CYAN)
            # This command prints the certificate details to your terminal
            subprocess.run(["ssh-keygen", "-Lf", cert_path])
            
            click.secho(f"Connecting to {username}@{host}...", fg=Colors.GREEN)
            # ... followed by your subprocess.run(ssh_cmd) ...
            
            # Pass control to SSH
            subprocess.run(ssh_cmd)

            click.secho("\nSession closed. Credentials destroyed.", fg=Colors.YELLOW)

    except Exception as e:
        click.secho(str(e), fg=Colors.RED)
        raise SystemExit(1) from e

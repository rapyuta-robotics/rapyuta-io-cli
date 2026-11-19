# Copyright 2024 Rapyuta Robotics
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
import os
import subprocess

import click
import requests
from click_help_colors import HelpColorsCommand

from riocli.config import new_hwil_client
from riocli.constants import Colors, Symbols
from riocli.hwil.util import name_to_id

# Sources HWIL's NSG always allows (HWIL_SSH_ALLOWED_SOURCES defaults). From anywhere else,
# `rio hwil ssh` opens just-in-time access for the caller's public IP first.
OFFICE_SOURCES = ("121.2.38.2", "14.195.117.58", "111.93.196.126")
PUBLIC_IP_URL = "https://api.ipify.org"

DEFAULT_PUBLIC_KEYS = (
    "~/.ssh/id_ed25519.pub",
    "~/.ssh/id_ecdsa.pub",
    "~/.ssh/id_rsa.pub",
)


def find_public_key(path: str | None = None) -> str:
    """The public key file to use: the given one, else the first default that exists."""
    candidates = [path] if path else DEFAULT_PUBLIC_KEYS
    for candidate in candidates:
        full = os.path.expanduser(candidate)
        if os.path.isfile(full):
            return full
    raise FileNotFoundError(
        f"no ssh public key found (tried {', '.join(candidates)}); "
        "create one with `ssh-keygen -t ed25519` or pass --key"
    )


def detect_public_ip() -> str:
    try:
        return requests.get(PUBLIC_IP_URL, timeout=10).text.strip()
    except requests.RequestException as e:
        raise Exception(f"could not detect your public IP ({e}); pass --source-ip") from e


@click.command(
    "ssh",
    cls=HelpColorsCommand,
    help_headers_color=Colors.YELLOW,
    help_options_color=Colors.GREEN,
)
@click.option(
    "--key",
    "key_path",
    type=str,
    default=None,
    help="Your ssh public key file. Default: ~/.ssh/id_ed25519.pub, id_ecdsa.pub or id_rsa.pub",
)
@click.option(
    "--source-ip",
    type=str,
    default=None,
    help="Your public IPv4. Default: detected via " + PUBLIC_IP_URL,
)
@click.option(
    "--duration",
    type=int,
    default=None,
    help="Minutes of ssh access from outside the office (default 120, max 480)",
)
@click.argument("device-name", required=True, type=str)
@name_to_id
def ssh(
    device_name: str,
    device_id: str,
    key_path: str = None,
    source_ip: str = None,
    duration: int = None,
    spinner=None,
) -> None:
    """SSH into a hardware-in-the-loop device.

    HWIL VMs are key-only and port 22 is open only to the offices. From
    anywhere else this command first opens just-in-time access for your
    public IP (it expires; re-running extends it). It then adds your own
    public key to the device (adding it again is a no-op) and runs ``ssh``
    with the matching private key. No password is involved.
    """
    try:
        client = new_hwil_client()
        device = client.get_device(device_id)

        if not device.get("ip_address"):
            click.secho(
                f"{Symbols.ERROR} Device does not have a static IP address",
                fg=Colors.RED,
            )
            raise SystemExit(1)

        ip = source_ip or detect_public_ip()
        if ip not in OFFICE_SOURCES:
            access = client.grant_ssh_access(device_id, ip, duration)
            click.secho(
                f"{Symbols.INFO} ssh access from {ip} to {device.name} until {access.expires_at}",
                fg=Colors.BRIGHT_CYAN,
            )

        public_key = find_public_key(key_path)
        with open(public_key) as f:
            added = client.add_ssh_key(device_id, f.read().strip())
        click.secho(
            f"{Symbols.INFO} Key {added.fingerprint} authorized for {added.username}@{device.name}",
            fg=Colors.BRIGHT_CYAN,
        )

        cmd = ["ssh", "-o", "IdentitiesOnly=yes"]
        private_key = public_key[: -len(".pub")] if public_key.endswith(".pub") else None
        if private_key and os.path.isfile(private_key):
            cmd += ["-i", private_key]
        cmd.append(f"{device.username}@{device['ip_address']}")
        raise SystemExit(subprocess.call(cmd))
    except Exception as e:
        click.secho(str(e), fg=Colors.RED)
        raise SystemExit(1)

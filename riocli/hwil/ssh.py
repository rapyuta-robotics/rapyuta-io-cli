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
import re
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


KNOWN_HOSTS = "~/.config/rio-cli/hwil_known_hosts"
_DEVICE_NAME = re.compile(r"[A-Za-z0-9][A-Za-z0-9._-]{0,99}")  # same rule as HWIL


def pin_host_key(device_name: str, host_key: str, path: str = KNOWN_HOSTS) -> str:
    """Write `<device_name> <ssh-ed25519 key>` into rio's own known_hosts, replacing any older entry for that
    device. ssh then checks the VM against the key HWIL recorded at first boot (HostKeyAlias=<device_name>), not
    against whatever answers on a reused IP. Returns the file path."""
    # the name becomes a known_hosts host pattern: refuse wildcards, negation, lists, markers and whitespace
    if not _DEVICE_NAME.fullmatch(device_name or ""):
        raise ValueError(
            f"refusing to pin a host key for unexpected device name {device_name!r}"
        )
    parts = (host_key or "").split()
    if len(parts) < 2 or parts[0] != "ssh-ed25519":
        raise ValueError(f"HWIL returned no valid host key for {device_name}")
    full = os.path.expanduser(path)
    os.makedirs(os.path.dirname(full), mode=0o700, exist_ok=True)
    lines = []
    if os.path.isfile(full):
        with open(full) as f:
            lines = [ln for ln in f if ln.split(" ", 1)[0] != device_name]
    lines.append(f"{device_name} {parts[0]} {parts[1]}\n")
    with open(full, "w") as f:
        f.writelines(lines)
    return full


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
        if device.get("ssh_host_key"):
            # pinned: only the host key HWIL recorded at first boot is accepted (no trust-on-first-use, and no
            # known_hosts clash when Azure hands a VM's IP to another VM)
            known = pin_host_key(device.name, device.ssh_host_key)
            cmd += [
                "-o",
                f"HostKeyAlias={device.name}",
                "-o",
                f"UserKnownHostsFile={known}",
                "-o",
                "StrictHostKeyChecking=yes",
                "-o",
                "HostKeyAlgorithms=ssh-ed25519",
            ]
        else:
            click.secho(
                f"{Symbols.WARNING} HWIL has no host key for {device.name} (created before host-key pinning); "
                "ssh will ask you to verify it",
                fg=Colors.YELLOW,
            )
        private_key = public_key[: -len(".pub")] if public_key.endswith(".pub") else None
        if private_key and os.path.isfile(private_key):
            cmd += ["-i", private_key]
        cmd.append(f"{device.username}@{device['ip_address']}")
        raise SystemExit(subprocess.call(cmd))
    except Exception as e:
        click.secho(str(e), fg=Colors.RED)
        raise SystemExit(1)

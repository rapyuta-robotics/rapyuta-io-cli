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
import getpass
import json
import os
import socket
import tempfile
import time
from datetime import datetime, timedelta
from os.path import exists, join
from shutil import move, which
from sys import platform
from tempfile import NamedTemporaryFile
from typing import Optional

import click
from munch import Munch
from python_hosts import Hosts, HostsEntry

from riocli.config import get_config_from_context, new_client, new_v2_client
from riocli.constants import Colors, Symbols
from riocli.utils import run_bash, run_bash_with_return_code
from riocli.v2client import Client as v2Client

HOSTS_FILE_COMMENT = "riovpn"


def get_host_ip() -> str:
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
        s.connect(("8.8.8.8", 80))
        return s.getsockname()[0]


def get_host_name() -> str:
    return socket.gethostname()


def is_linux() -> bool:
    return platform.lower() == "linux"


def is_windows() -> bool:
    return platform.lower() == "win32"


def is_curl_installed() -> bool:
    return which("curl") is not None


def is_tailscale_installed() -> bool:
    return which("tailscale") is not None


def is_tailscale_up() -> bool:
    _, code = run_bash_with_return_code("tailscale status")
    return code == 0


def get_tailscale_ip() -> str:
    return run_bash("tailscale ip")


def stop_tailscale() -> bool:
    _, code = run_bash_with_return_code(priviledged_command("tailscale down"))
    if code != 0:
        return False

    output, code = run_bash_with_return_code(priviledged_command("tailscale logout"))
    if code != 0 and "no nodekey to log out" not in output:
        return False

    return True


def get_tailscale_status() -> dict:
    output, _ = run_bash_with_return_code("tailscale status --json")
    return json.loads(output)


def install_vpn_tools() -> None:
    if is_tailscale_installed():
        return

    click.confirm(
        click.style(
            "{} VPN tools are not installed. Do you want " "to install them now?".format(
                Symbols.INFO
            ),
            fg=Colors.YELLOW,
        ),
        default=True,
        abort=True,
    )

    if not is_linux():
        click.secho("Only linux is supported", fg=Colors.YELLOW)
        raise SystemExit(1)

    if is_tailscale_installed():
        click.secho("VPN tools already installed", fg=Colors.GREEN)
        return

    if not is_curl_installed():
        click.secho("Please install `curl`", fg=Colors.RED)
        raise SystemExit(1)

    # download the tailscale install script
    run_bash("curl -sLO https://tailscale.com/install.sh")

    with tempfile.TemporaryDirectory() as tmp_dir:
        script_path = join(tmp_dir, "install.sh")

        # move it to the tmp directory
        move("install.sh", script_path)

        if not exists(script_path):
            raise FileNotFoundError

        run_bash("sh {}".format(script_path))

    if not is_tailscale_installed():
        raise Exception("{} Failed to install VPN tools".format(Symbols.ERROR))

    click.secho("{} VPN tools installed".format(Symbols.SUCCESS), fg=Colors.GREEN)


def tailscale_ping(tailscale_peer_ip):
    cmd = "tailscale ping --icmp --tsmp --peerapi {}".format(tailscale_peer_ip)
    return run_bash_with_return_code(cmd)


def is_vpn_enabled_in_project(client: v2Client, project_guid: str) -> bool:
    project = client.get_project(project_guid)
    return (
        project.status.status.lower() == "success"
        and project.status.vpn.lower() == "success"
    )


def priviledged_command(cmd: str) -> str:
    """Returns an effective command to execute."""
    if is_windows() or (is_linux() and os.geteuid() == 0):
        return cmd

    return "sudo {}".format(cmd)


def create_binding(
    ctx: click.Context,
    name: str = "",
    machine: str = "",
    labels: dict = None,
    delta: Optional[timedelta] = None,
    ephemeral: bool = True,
    throwaway: bool = True,
) -> Munch:
    vpn_instance = "rio-internal-headscale"
    if name == "":
        name = "{}-{}".format(ctx.obj.machine_id, int(time.time()))

    body = {
        "metadata": {
            "name": name,
            "labels": labels or {},
        },
        "spec": {
            "instance": vpn_instance,
            "provider": "headscalevpn",
            "throwaway": throwaway,
            "config": {
                "ephemeral": ephemeral,
                "expirationTime": get_key_expiry_time(delta),
                "nodeKey": machine,
            },
        },
    }

    client = get_config_from_context(ctx).new_v2_client()

    # We may end up creating multiple throwaway tokens in the database.
    # But that's okay and something that we can live with
    binding = client.create_instance_binding(vpn_instance, binding=body)
    return binding.spec.get("environment", {})


def get_key_expiry_time(delta: Optional[timedelta]) -> Optional[str]:
    if delta is None:
        return None

    expiry = datetime.utcnow() + delta
    return expiry.isoformat("T") + "Z"


def get_binding_labels() -> dict:
    return {
        "creator": "riocli",
        "hostname": get_host_name(),
        "ip_address": str(get_host_ip()),
        "username": getpass.getuser(),
        "rapyuta.io/internal": "true",
    }


def update_hosts_file():
    """Update the hosts file with the VPN peers to allow access to them by hostname.

    This is a helper method that fetches the local tailscale status and the list of
    online devices in the project. It then filters the online devices based on the
    status of the VPN daemon running on it.

    It then matches the hostname of the tailscale peers with the hostname of the devices
    and creates an entry in the system's hosts file.
    """
    v1_client = new_client(with_project=True)
    v2_client = new_v2_client(with_project=True)

    device_host_to_name = {}
    for device in v1_client.get_all_devices(online_device=True):
        device_daemon = v2_client.get_device_daemons(device_guid=device.get("uuid"))
        vpn_status = device_daemon.status.get("vpn")
        if vpn_status is not None and vpn_status.get("enable", False) and vpn_status.get("status") == "running":
            device_host_to_name[device.get("host")] = device.name

    status = get_tailscale_status()
    peers = status.get("Peer", {})

    hosts = Hosts()

    # Cleanup previous entries, if any.
    hosts.remove_all_matching(comment=HOSTS_FILE_COMMENT)

    entries = []
    for _, node in peers.items():
        if not node.get("Online"):
            continue

        if node.get("HostName") in device_host_to_name:
            tailscale_hostname = node.get("HostName")
            rio_device_name = device_host_to_name[tailscale_hostname]
            entries.append(
                HostsEntry(
                    entry_type="ipv4",
                    address=node.get("TailscaleIPs")[0],
                    names=[tailscale_hostname, rio_device_name],
                    comment=HOSTS_FILE_COMMENT,
                )
            )

    # Nothing to add if there are no
    # devices with VPN enabled.
    if len(entries) == 0:
        return

    hosts.add(entries)
    write_hosts_file(hosts)


def cleanup_hosts_file():
    """Cleanup any entries from the hosts file created during connect.

    We add a pre-defined comment to the entries that we add to the hosts file
    during the connect operation. This method removes all entries that have
    the comment 'riovpn' from the hosts file.
    """
    hosts = Hosts()
    before = list(hosts.entries)
    hosts.remove_all_matching(comment=HOSTS_FILE_COMMENT)
    after = list(hosts.entries)

    # Skip if nothing to remove.
    if len(before) == len(after):
        return

    write_hosts_file(hosts)


def write_hosts_file(hosts: Hosts) -> None:
    """Write the hosts file to the system.

    Since writing to the host file requires privileged access,
    this helper function does that by taking the platform into
    account and performing the set of steps required to write
    the hosts file.

    The assumption here is that users will run the vpn command
    as administrators on Windows machines and hence, we don't
    need to explicitly elevate privileges.
    """
    if is_windows():
        hosts.write()
        return

    temp = NamedTemporaryFile(delete=False)
    hosts.write(path=temp.name)
    temp.close()

    run_bash(priviledged_command(f"cp {hosts.path} {hosts.path}.bak"))
    _, code = run_bash_with_return_code(
        priviledged_command(f"mv {temp.name} {hosts.path}")
    )

    if code != 0:
        raise Exception("failed to write hosts file")

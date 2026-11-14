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
"""`rio hwil pool`: inspect and tear down HWIL device pools. Pools are created with `rio apply` (kind: DevicePool)."""

from __future__ import annotations

import click
from click_help_colors import HelpColorsCommand
from munch import unmunchify

from riocli.config import new_client, new_hwil_client, new_v2_client
from riocli.config.config import Configuration
from riocli.constants import Colors
from riocli.devicepool.util import cleanup_pool, wait_for_pool
from riocli.utils import AliasedGroup, inspect_with_format, tabulate_data


def _hint(p) -> None:
    if p.get("leftovers"):
        click.secho(
            f"device pool {p.name} left devices or deployments in rapyuta.io: run `rio hwil pool cleanup {p.name}`",
            fg=Colors.YELLOW,
        )


@click.group(
    name="pool",
    invoke_without_command=False,
    cls=AliasedGroup,
    help_headers_color=Colors.YELLOW,
    help_options_color=Colors.GREEN,
)
def pool():
    """Manage HWIL device pools.

    A device pool is a set of emulated rapyuta.io devices, each running the
    same deployments, built by HWIL on Azure VMs for scale testing. Create
    one with `rio apply` and a manifest of kind DevicePool; pools work only
    against dev and pr<N> environments.
    """


@pool.command(
    "list",
    cls=HelpColorsCommand,
    help_headers_color=Colors.YELLOW,
    help_options_color=Colors.GREEN,
)
def list_pools() -> None:
    """List device pools."""
    try:
        pools = new_hwil_client().list_pools()
        headers = (
            "ID",
            "Name",
            "State",
            "Mode",
            "Devices",
            "Deps/Device",
            "Devices Ready",
            "Deployments Ready",
            "Expiry",
        )
        rows = [
            [
                p.id,
                p.name,
                p.state,
                p.get("mode"),
                p.get("devices"),
                p.get("deployments_per_device"),
                (p.get("progress") or {}).get("devices_ready"),
                (p.get("progress") or {}).get("deployments_ready"),
                p.get("expiry_at"),
            ]
            for p in pools
        ]
        tabulate_data(rows, headers)
    except Exception as e:
        click.secho(str(e), fg=Colors.RED)
        raise SystemExit(1)


@pool.command(
    "inspect",
    cls=HelpColorsCommand,
    help_headers_color=Colors.YELLOW,
    help_options_color=Colors.GREEN,
)
@click.option(
    "--format",
    "-f",
    "format_type",
    default="yaml",
    type=click.Choice(["json", "yaml"], case_sensitive=False),
)
@click.argument("pool-name", type=str)
def inspect_pool(format_type: str, pool_name: str) -> None:
    """Print a device pool: state, progress, per-VM phase and host load."""
    try:
        p = new_hwil_client().get_pool(pool_name)
        inspect_with_format(unmunchify(p), format_type)
        _hint(p)
    except Exception as e:
        click.secho(str(e), fg=Colors.RED)
        raise SystemExit(1)


@pool.command(
    "delete",
    cls=HelpColorsCommand,
    help_headers_color=Colors.YELLOW,
    help_options_color=Colors.GREEN,
)
@click.option("--force", "-f", is_flag=True, default=False, help="Skip the confirmation")
@click.option(
    "--wait", "-w", is_flag=True, default=False, help="Wait until the pool is DELETED"
)
@click.argument("pool-name", type=str)
def delete_pool(force: bool, wait: bool, pool_name: str) -> None:
    """Delete a device pool: its devices, deployments and VMs."""
    try:
        client = new_hwil_client()
        p = client.get_pool(pool_name)
        if not force:
            click.confirm(
                f"Delete device pool {p.name} ({p.get('devices')} devices, state {p.state})?",
                abort=True,
            )
        client.delete_pool(p.id)
        click.secho(f"device pool {p.name} is being deleted", fg=Colors.GREEN)
        if wait:
            _hint(wait_for_pool(client, p.id, ("DELETED",)))
    except click.exceptions.Abort:
        raise
    except Exception as e:
        click.secho(str(e), fg=Colors.RED)
        raise SystemExit(1)


@pool.command(
    "cleanup",
    cls=HelpColorsCommand,
    help_headers_color=Colors.YELLOW,
    help_options_color=Colors.GREEN,
)
@click.option("--force", "-f", is_flag=True, default=False, help="Skip the confirmation")
@click.argument("pool-name", type=str)
def cleanup(force: bool, pool_name: str) -> None:
    """Delete what a deleted pool left in rapyuta.io.

    When a pool VM could not be reached during teardown, HWIL deletes the VMs
    and reports leftovers: devices and deployments labelled pool=<id> that
    only your own token can remove. This deletes them, in the pool's own
    environment and project only.
    """
    try:
        p = new_hwil_client().get_pool(pool_name)
        if not force:
            click.confirm(
                f"Delete every deployment and device labelled pool={p.id} in {p.environment}/{p.project_guid}?",
                abort=True,
            )
        r = cleanup_pool(
            p,
            Configuration(),
            new_v2_client(with_project=True),
            new_client(with_project=True),
        )
        click.secho(
            f"deleted {r['deployments']} deployments and {r['devices']} devices "
            f"({r['already_gone']} already gone, {r['deployments_failed']} deployments and {r['devices_failed']} devices failed)",
            fg=Colors.GREEN
            if not (r["deployments_failed"] or r["devices_failed"])
            else Colors.YELLOW,
        )
        if r["deployments_failed"] or r["devices_failed"]:
            raise SystemExit(1)
    except (click.exceptions.Abort, SystemExit):
        raise
    except Exception as e:
        click.secho(str(e), fg=Colors.RED)
        raise SystemExit(1)

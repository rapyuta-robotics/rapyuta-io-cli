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
"""DevicePool helpers: the HWIL request body built from a manifest and the CLI config, waiting on a pool, and the
label-based cleanup of objects a pool's teardown could not remove."""

from __future__ import annotations

import re
import time
from concurrent.futures import ThreadPoolExecutor
from typing import TYPE_CHECKING, Any

import click
from rapyuta_io_sdk_v2 import walk_pages

if TYPE_CHECKING:
    from collections.abc import Callable, Iterable

    from munch import Munch

# HWIL only builds pools against these rapyuta.io environments (its serializer and the VM agent check the same rule).
ENV_RE = re.compile(r"^(dev|pr[0-9]+)$")
UP_TERMINAL = ("READY", "DEGRADED", "FAILED")


class PoolEnvironmentError(Exception):
    """The CLI points at an environment or project the pool cannot (or does not) live in."""


class PoolStateError(Exception):
    """The pool is in a state the operation does not apply to."""


def cli_environment(config) -> str:
    # a ga login has no "environment" key
    return config.data.get("environment", "ga")


def pool_body(pool, config) -> dict[str, Any]:
    """POST /pool/ body: the manifest's spec plus the `rio` block from the CLI config (users never type tokens)."""
    env = cli_environment(config)
    if not ENV_RE.match(env or ""):
        raise PoolEnvironmentError(
            f"device pools run only against dev or pr<N> environments, not {env!r} (switch with `rio auth environment`)"
        )
    spec, metadata = pool.spec, pool.metadata
    labels = dict(metadata.get("labels") or {})
    labels.update(
        {
            "expiry_after": spec.expireAfter,
            "product": "scale",
            "user": config.data.get("email_id", "").split("@")[0],
        }
    )
    body = {
        "name": metadata.name,
        "devices": spec.devices,
        "deployments_per_device": spec.deploymentsPerDevice,
        "mode": spec.mode,
        "rio": {
            "environment": env,
            "project_guid": config.data["project_id"],
            "organization_guid": config.data["organization_id"],
            "token": config.data["auth_token"],
        },
        "labels": labels,
    }
    if spec.get("deviceNamePrefix"):
        body["device_name_prefix"] = spec.deviceNamePrefix
    if spec.get("deployment"):
        d = spec.deployment
        body["deployment"] = {"package": d.package, "version": d.version}
        if d.get("namePrefix"):
            body["deployment"]["name_prefix"] = d.namePrefix
    if spec.get("vm"):
        body["vm"] = {
            api: spec.vm[key]
            for key, api in (("cpu", "cpu"), ("devicesPerVm", "devices_per_vm"))
            if key in spec.vm
        }
    return body


def wait_for_pool(
    client,
    name_or_id,
    until: Iterable[str],
    timeout: float = 3 * 3600,
    interval: float = 10,
) -> Munch:
    """Poll a pool until its state is one of `until`, echoing each change of state or progress."""
    deadline, last = time.monotonic() + timeout, None
    while True:
        p = client.get_pool(name_or_id)
        progress = p.get("progress") or {}
        line = (
            f"{p.name}: {p.state} devices_ready={progress.get('devices_ready', 0)}/{p.get('devices', '?')} "
            f"deployments_ready={progress.get('deployments_ready', 0)}"
        )
        if line != last:
            click.echo(line)
            last = line
        if p.state in until:
            return p
        if time.monotonic() > deadline:
            raise TimeoutError(
                f"device pool {p.name} still {p.state} after {int(timeout)}s"
            )
        time.sleep(interval)


def _delete_all(
    items: list, delete: Callable[[Any], Any], parallel: int
) -> tuple[int, int, int]:
    """Delete in parallel. Returns (deleted, already_gone, failed): a not-found answer is not a deletion."""

    def one(item) -> str:
        try:
            delete(item)
            return "deleted"
        except Exception as e:  # the v1 and v2 SDKs raise different not-found types
            gone = "not found" in str(e).lower() or type(e).__name__ in (
                "HttpNotFoundError",
                "ResourceNotFoundError",
            )
            return "gone" if gone else "failed"

    with ThreadPoolExecutor(max_workers=max(1, parallel)) as ex:
        results = list(ex.map(one, items))
    return results.count("deleted"), results.count("gone"), results.count("failed")


def cleanup_pool(
    pool: Munch, config, v2_client, v1_client, parallel: int = 16
) -> dict[str, int]:
    """Delete the rapyuta.io deployments, then devices, labelled pool=<id> with the user's own token.

    Only for the pool's own environment and project: the CLI must point there, so a label match can never reach
    another project's objects.
    """
    if pool.state != "DELETED":
        raise PoolStateError(
            f"device pool {pool.name} is {pool.state}: cleanup removes what a finished teardown left behind, "
            f"delete the pool first (`rio hwil pool delete {pool.name}`)"
        )
    env, project = cli_environment(config), config.data.get("project_id")
    if pool.environment != env or pool.project_guid != project:
        raise PoolEnvironmentError(
            f"device pool {pool.name} lives in {pool.environment}/{pool.project_guid}, the CLI points at {env}/{project}: "
            "switch environment and project first"
        )
    selector = f"pool={pool.id}"
    # the listing also returns Stopped deployments: those are deleted already (riocli e2e 2026-11-01)
    names = [
        d.metadata.name
        for page in walk_pages(v2_client.list_deployments, label_selector=[selector])
        for d in page
        if d.status.phase != "Stopped"
    ]
    dep_ok, dep_gone, dep_failed = _delete_all(
        names, v2_client.delete_deployment, parallel
    )

    def labelled(device) -> bool:
        return any(
            lbl.key == "pool" and str(lbl.value) == str(pool.id)
            for lbl in (device.labels or [])
        )

    uuids = [d.uuid for d in v1_client.get_all_devices() if labelled(d)]
    dev_ok, dev_gone, dev_failed = _delete_all(uuids, v1_client.delete_device, parallel)
    return {
        "deployments": dep_ok,
        "deployments_failed": dep_failed,
        "devices": dev_ok,
        "devices_failed": dev_failed,
        "already_gone": dep_gone + dev_gone,
    }

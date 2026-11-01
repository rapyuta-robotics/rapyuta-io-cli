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
from __future__ import annotations

from typing import TYPE_CHECKING

import click
from typing_extensions import override

from riocli.config.config import Configuration
from riocli.constants import ApplyResult, Colors, DeleteResult
from riocli.devicepool import util
from riocli.exceptions import ResourceNotFound
from riocli.hwilclient.client import PoolNotFound
from riocli.model import Model

if TYPE_CHECKING:
    from munch import Munch


class DevicePool(Model):
    """A pool of emulated rapyuta.io devices with deployments, built by HWIL on Azure VMs (kind: DevicePool)."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.update(*args, **kwargs)
        self.validate(self)

    @override
    def create_object(self, *args, **kwargs) -> Munch | None:
        raise NotImplementedError

    @override
    def update_object(self, *args, **kwargs) -> Munch | None:
        raise NotImplementedError

    @override
    def delete_object(self, *args, **kwargs) -> None:
        raise NotImplementedError

    @override
    def list_dependencies(self) -> list[str] | None:
        return None

    @override
    def apply(self, *args, config: Configuration | None = None, **kwargs) -> ApplyResult:
        config = config or Configuration()
        client = config.new_hwil_client()
        name = self.metadata.name
        try:
            existing = client.get_pool(name)
        except PoolNotFound:
            existing = None

        if existing is not None:
            if existing.state == "DELETED":
                raise Exception(
                    f"device pool {name} was deleted and HWIL keeps pool names unique: apply it under a new name"
                )
            changed = self._changed(existing)
            if changed:
                self.exists_reason = (
                    f"device pool {name} exists with {changed}; pools cannot be resized: delete it and apply it "
                    "under a new name"
                )
            return ApplyResult.EXISTS

        created = client.create_pool(util.pool_body(self, config))
        if self.spec.wait:
            p = util.wait_for_pool(client, created.id, util.UP_TERMINAL)
            if p.state == "FAILED":
                raise Exception(
                    f"device pool {name} FAILED: {p.get('reason') or 'no reason given'}"
                )
        return ApplyResult.CREATED

    @override
    def delete(
        self, *args, config: Configuration | None = None, **kwargs
    ) -> DeleteResult:
        config = config or Configuration()
        client = config.new_hwil_client()
        name = self.metadata.name
        try:
            p = client.get_pool(name)
        except PoolNotFound:
            raise ResourceNotFound
        if p.state == "DELETED":
            raise ResourceNotFound

        client.delete_pool(p.id)
        if self.spec.wait:
            p = util.wait_for_pool(client, p.id, ("DELETED",))
            if p.get("leftovers"):
                click.secho(
                    f"device pool {name} left devices or deployments in rapyuta.io: run `rio hwil pool cleanup {name}`",
                    fg=Colors.YELLOW,
                )
        return DeleteResult.DELETED

    def _changed(self, existing: Munch) -> str:
        """What the manifest asks for that the existing pool does not have (pools are immutable)."""
        wanted = {
            "devices": self.spec.devices,
            "deployments_per_device": self.spec.deploymentsPerDevice,
            "mode": self.spec.mode,
        }
        diffs = [
            f"{k}={existing[k]} (manifest: {v})"
            for k, v in wanted.items()
            if k in existing and existing[k] != v
        ]
        return ", ".join(diffs)

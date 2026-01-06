# Copyright 2025 Rapyuta Robotics
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
import time

from munch import Munch
from rapyuta_io_sdk_v2 import Client
from rapyuta_io_sdk_v2 import Deployment as DeploymentModel
from typing_extensions import override

from riocli.constants import Status
from riocli.model import Model
from riocli.utils.error import (
    RetriesExhausted,
)


class Deployment(Model):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.update(*args, **kwargs)
        self._obj = DeploymentModel.model_validate(self)

    @override
    def create_object(
        self, v2_client: Client, retry_count: int, retry_interval: int, *args, **kwargs
    ) -> DeploymentModel:
        hard_dependencies = [
            getattr(d, "name_or_guid", None)
            for d in (getattr(self._obj.spec, "depends", None) or [])
            if d is not None and getattr(d, "wait", False)
        ]

        if hard_dependencies:
            wait_for_dependencies(
                v2_client,
                hard_dependencies,
                retry_count=retry_count,
                retry_interval=retry_interval,
            )

        return v2_client.create_deployment(self._obj)  # pyright:ignore[reportArgumentType]

    @override
    def update_object(self, *args, **kwargs) -> Munch | None:
        raise NotImplementedError

    @override
    def delete_object(self, v2_client: Client, *args, **kwargs) -> None:
        _ = v2_client.delete_deployment(self._obj.metadata.name)

    @override
    def list_dependencies(self) -> list[str] | None:
        return self._obj.list_dependencies()


def wait_for_dependencies(
    client: Client,
    deployment_names: list[str],
    retry_count: int = 50,
    retry_interval: int = 6,
) -> None:
    """Waits until all deployment_names are in RUNNING state."""
    for _ in range(retry_count):
        deployments = client.list_deployments(
            names=deployment_names,
            phases=["InProgress", "Provisioning", "Succeeded"],
        )

        if all(d.status.status == Status.RUNNING for d in deployments.items):
            return

        time.sleep(retry_interval)

    raise RetriesExhausted(
        f"Retries exhausted waiting for dependencies: {deployment_names}"
    )

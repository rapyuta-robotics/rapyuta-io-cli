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
import time
import typing

from munch import unmunchify

from riocli.config import new_v2_client
from riocli.constants import Status, ApplyResult
from riocli.exceptions import ResourceNotFound
from riocli.model import Model
from riocli.v2client import Client
from riocli.v2client.error import (
    HttpAlreadyExistsError,
    HttpNotFoundError,
    RetriesExhausted,
)


class Deployment(Model):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.update(*args, **kwargs)

    def apply(self, *args, **kwargs) -> ApplyResult:
        hard_dependencies = [
            d.nameOrGUID for d in self.spec.get("depends", []) if d.get("wait", False)
        ]

        client = new_v2_client()

        # Block until all hard dependencies are in RUNNING state
        if hard_dependencies:
            wait_for_dependencies(client, hard_dependencies)

        self.metadata.createdAt = None
        self.metadata.updatedAt = None

        try:
            client.create_deployment(unmunchify(self))
            return ApplyResult.CREATED
        except HttpAlreadyExistsError:
            return ApplyResult.EXISTS

    def delete(self, *args, **kwargs):
        client = new_v2_client()

        try:
            client.delete_deployment(self.metadata.name)
        except HttpNotFoundError:
            raise ResourceNotFound


def wait_for_dependencies(
    client: Client,
    deployment_names: typing.List[str],
    retry_count: int = 50,
    retry_interval: int = 6,
) -> None:
    """Waits until all deployment_names are in RUNNING state."""
    for _ in range(retry_count):
        deployments = client.list_deployments(
            query={
                "names": deployment_names,
                "phases": ["InProgress", "Provisioning", "Succeeded"],
            }
        )

        if all(d.status.status == Status.RUNNING for d in deployments):
            return

        time.sleep(retry_interval)

    raise RetriesExhausted(
        f"Retries exhausted waiting for dependencies: {deployment_names}"
    )

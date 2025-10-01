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

from munch import Munch, unmunchify
from rapyuta_io_sdk_v2 import Client
from rapyuta_io_sdk_v2.exceptions import HttpNotFoundError
from typing_extensions import Any, override
from waiting import wait

from riocli.auth.util import find_project_guid
from riocli.config import Configuration
from riocli.constants import ApplyResult
from riocli.exceptions import ProjectNotFound
from riocli.model import Model

from riocli.project.util import check_project_name

PROJECT_READY_TIMEOUT = 150


class Project(Model):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.update(*args, **kwargs)

    @override
    def create_object(self, *args, **kwargs) -> Munch | None:
        raise NotImplementedError

    @override
    def update_object(self, *args, **kwargs) -> Munch | None:
        raise NotImplementedError

    @override
    def delete_object(
        self, v2_client: Client, config: Configuration, *args, **kwargs
    ) -> None:
        guid = self._get_guid(v2_client, config)
        _ = v2_client.delete_project(guid)

    @override
    def list_dependencies(self) -> list[str] | None:
        return None

    @override
    def apply(
        self,
        v2_client: Client,
        config: Configuration,
        retry_count: int,
        retry_interval: int,
        *args,
        **kwargs,
    ) -> ApplyResult:
        project = unmunchify(self)

        # set organizationGUID irrespective of it being present in the manifest
        self._set_organization(project, config)

        try:
            # We try to update before creating in Project. The DockerCache
            # feature is only available in the Update API. If we instead try to
            # create the Project with DockerCache feature enabled then the API
            # will return BadRequest error.
            guid = self._get_guid(v2_client, config)

            client.update_project(project_guid=guid, body=project)
            wait(
                self._is_ready,
                timeout_seconds=retry_count * retry_interval,
                sleep_seconds=(1, 30, 2),
            )
            return ApplyResult.UPDATED
        except (HttpNotFoundError, ProjectNotFound):
            project_name = project["metadata"]["name"]
            check_project_name(project_name=project_name)
            _ = v2_client.create_project(project)  # pyright:ignore[reportArgumentType]

            return ApplyResult.CREATED
        except Exception as e:
            raise e

    def delete(self, *args, **kwargs) -> None:
        client = new_v2_client()

        try:
            guid = find_project_guid(
                client, self.metadata.name, Configuration().data["organization_id"]
            )
            client.delete_project(guid)
        except (HttpNotFoundError, ProjectNotFound):
            raise ResourceNotFound

    def is_ready(self) -> bool:
        client = new_v2_client()
        projects = client.list_projects(name=self.metadata.name)
        return projects.items[0].status.status == "Success"

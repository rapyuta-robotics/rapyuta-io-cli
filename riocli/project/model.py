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

from munch import unmunchify
from waiting import wait

from riocli.config import Configuration, new_v2_client
from riocli.constants import ApplyResult
from riocli.exceptions import ResourceNotFound
from riocli.model import Model
from riocli.project.util import ProjectNotFound, find_project_guid
from riocli.v2client.error import HttpNotFoundError

PROJECT_READY_TIMEOUT = 150


class Project(Model):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.update(*args, **kwargs)

    def apply(self, *args, **kwargs) -> ApplyResult:
        client = new_v2_client()

        project = unmunchify(self)

        # set organizationGUID irrespective of it being present in the manifest
        project["metadata"]["organizationGUID"] = Configuration().organization_guid

        try:
            # We try to update before creating in Project. The DockerCache
            # feature is only available in the Update API. If we instead try to
            # create the Project with DockerCache feature enabled then the API
            # will return BadRequest error.
            guid = find_project_guid(
                client, self.metadata.name, Configuration().organization_guid
            )

            client.update_project(guid, project)
            wait(
                self.is_ready,
                timeout_seconds=PROJECT_READY_TIMEOUT,
                sleep_seconds=(1, 30, 2),
            )
            return ApplyResult.UPDATED
        except (HttpNotFoundError, ProjectNotFound):
            client.create_project(project)
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
        projects = client.list_projects(query={"name": self.metadata.name})
        return projects[0].status.status == "Success"

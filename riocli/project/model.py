# Copyright 2022 Rapyuta Robotics
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
import typing

from munch import unmunchify
from rapyuta_io import Client
from waiting import wait, TimeoutExpired

from riocli.config import new_v2_client, Configuration
from riocli.jsonschema.validate import load_schema
from riocli.model import Model

PROJECT_READY_TIMEOUT = 150


class Project(Model):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.update(*args, **kwargs)

    def find_object(self, client: Client) -> bool:
        guid, obj = self.rc.find_depends(
            {"kind": "project", "nameOrGUID": self.metadata.name})
        if not guid:
            return False

        return obj

    def create_object(self, client: Client, **kwargs) -> typing.Any:
        client = new_v2_client()

        # convert to a dict and remove the ResolverCache
        # field since it's not JSON serializable
        project = unmunchify(self)
        project.pop("rc", None)

        # set organizationGUID irrespective of it being present in the manifest
        project['metadata']['organizationGUID'] = Configuration().data[
            'organization_id']

        r = client.create_project(project)

        try:
            wait(self.is_ready, timeout_seconds=PROJECT_READY_TIMEOUT,
                 sleep_seconds=(1, 30, 2))
        except TimeoutExpired as e:
            raise e

        return unmunchify(r)

    def update_object(self, client: Client, obj: typing.Any) -> typing.Any:
        client = new_v2_client()

        project = unmunchify(self)
        project.pop("rc", None)

        # set organizationGUID irrespective of it being present in the manifest
        project['metadata']['organizationGUID'] = Configuration().data[
            'organization_id']

        client.update_project(obj.metadata.guid, project)

    def delete_object(self, client: Client, obj: typing.Any) -> typing.Any:
        client = new_v2_client()
        client.delete_project(obj.metadata.guid)

    def is_ready(self) -> bool:
        client = new_v2_client()
        projects = client.list_projects(query={"name": self.metadata.name})
        return projects[0].status.status == 'Success'

    @classmethod
    def pre_process(cls, client: Client, d: typing.Dict) -> None:
        pass

    @staticmethod
    def validate(data):
        """
        Validates if project data is matching with its corresponding schema
        """
        schema = load_schema('project')
        schema.validate(data)

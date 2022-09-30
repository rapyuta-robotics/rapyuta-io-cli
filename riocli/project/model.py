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

import click
from rapyuta_io import Project as v1Project, Client

from riocli.model import Model
from riocli.project.util import find_project_guid, ProjectNotFound
from riocli.project.validation import validate


class Project(Model):

    def __init__(self, *args, **kwargs):
        self.update(*args, **kwargs)

    def find_object(self, client: Client) -> bool:
        guid, obj = self.rc.find_depends({"kind": "project", "nameOrGUID": self.metadata.name})
        if not guid:
            return False

        return obj

    def create_object(self, client: Client) -> v1Project:
        project = client.create_project(self.to_v1())
        return project

    def update_object(self, client: Client, obj: typing.Any) -> typing.Any:
        pass

    def delete_object(self, client: Client, obj: typing.Any) -> typing.Any:
        obj.delete()

    def to_v1(self) -> v1Project:
        return v1Project(self.metadata.name)

    @classmethod
    def pre_process(cls, client: Client, d: typing.Dict) -> None:
        pass

    @staticmethod
    def validate(data) -> None:
        validate(data)

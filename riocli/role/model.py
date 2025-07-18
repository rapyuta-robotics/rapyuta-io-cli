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

from munch import unmunchify

from riocli.config import new_v2_client
from riocli.constants import ApplyResult
from riocli.exceptions import ResourceNotFound
from riocli.model import Model
from riocli.v2client.error import HttpAlreadyExistsError, HttpNotFoundError


class Role(Model):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.update(*args, **kwargs)

    def apply(self, *args, **kwargs) -> ApplyResult:
        client = new_v2_client()

        self.metadata.createdAt = None
        self.metadata.updatedAt = None

        try:
            client.create_role(unmunchify(self))
            return ApplyResult.CREATED
        except HttpAlreadyExistsError:
            return ApplyResult.EXISTS
        except Exception as e:
            raise e

    def delete(self, *args, **kwargs) -> None:
        client = new_v2_client()



        try:
            client.delete_role(role_name=self.metadata.name)
        except HttpNotFoundError:
            raise ResourceNotFound


class RoleBinding(Model):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.update(*args, **kwargs)

    def apply(self, *args, **kwargs) -> ApplyResult:
        client = new_v2_client()

        self.metadata.createdAt = None
        self.metadata.updatedAt = None

        try:
            client.create_role_binding(unmunchify(self))
            return ApplyResult.CREATED
        except HttpAlreadyExistsError:
            return ApplyResult.EXISTS
        except Exception as e:
            raise e

    def delete(self, *args, **kwargs) -> None:
        client = new_v2_client()

        try:
            client.delete_role_binding(binding_name=self.metadata.name)
        except HttpNotFoundError:
            raise ResourceNotFound

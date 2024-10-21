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

from riocli.config import Configuration, new_v2_client
from riocli.constants import ApplyResult
from riocli.exceptions import ResourceNotFound
from riocli.model import Model
from riocli.v2client.error import HttpAlreadyExistsError, HttpNotFoundError


class StaticRoute(Model):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.update(*args, **kwargs)

    def apply(self, *args, **kwargs) -> ApplyResult:
        client = new_v2_client()

        static_route = unmunchify(self)

        try:
            client.create_static_route(static_route)
            return ApplyResult.CREATED
        except HttpAlreadyExistsError:
            client.update_static_route(self.metadata.name, static_route)
            return ApplyResult.UPDATED

    def delete(self, *args, **kwargs) -> None:
        client = new_v2_client()

        short_id = Configuration().organization_short_id

        try:
            client.delete_static_route(f"{self.metadata.name}-{short_id}")
        except HttpNotFoundError:
            raise ResourceNotFound

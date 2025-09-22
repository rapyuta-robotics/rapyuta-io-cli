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
from typing_extensions import override

from riocli import static_route
from riocli.model import Model
from rapyuta_io_sdk_v2 import Client


class StaticRoute(Model):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.update(*args, **kwargs)

    def apply(self, *args, **kwargs) -> ApplyResult:
        client = new_v2_client()

        static_route = unmunchify(self)

        try:
            client.create_staticroute(body=static_route)
            return ApplyResult.CREATED
        except HttpAlreadyExistsError:
            client.update_staticroute(name=self.metadata.name, body=static_route)
            return ApplyResult.UPDATED

    def delete(self, *args, **kwargs) -> None:
        client = new_v2_client()

        short_id = Configuration().organization_short_id

        try:
            client.delete_staticroute(f"{self.metadata.name}-{short_id}")
        except HttpNotFoundError:
            raise ResourceNotFound

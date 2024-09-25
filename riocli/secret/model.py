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

from riocli.config import new_v2_client
from riocli.constants import ApplyResult
from riocli.exceptions import ResourceNotFound
from riocli.model import Model
from riocli.v2client.error import HttpAlreadyExistsError, HttpNotFoundError


class Secret(Model):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.update(*args, **kwargs)

    def apply(self, *args, **kwargs) -> None:
        client = new_v2_client()

        secret = unmunchify(self)

        try:
            client.create_secret(unmunchify(self))
            return ApplyResult.CREATED
        except HttpAlreadyExistsError:
            client.update_secret(self.metadata.name, secret)
            return ApplyResult.UPDATED

    def delete(self, *args, **kwargs) -> None:
        client = new_v2_client()

        try:
            client.delete_secret(self.metadata.name)
        except HttpNotFoundError:
            raise ResourceNotFound

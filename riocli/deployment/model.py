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
import typing

from munch import unmunchify

from riocli.config import new_v2_client
from riocli.model import Model
from riocli.v2client.error import HttpAlreadyExistsError
from riocli.v2client.error import HttpNotFoundError


class Deployment(Model):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.update(*args, **kwargs)

    def apply(self, *args, **kwargs) -> typing.Any:
        client = new_v2_client()

        self.metadata.createdAt = None
        self.metadata.updatedAt = None

        try:
            client.create_deployment(unmunchify(self))
        except HttpAlreadyExistsError:
            pass

    def delete(self, *args, **kwargs):
        client = new_v2_client()

        try:
            client.delete_deployment(self.metadata.name)
        except HttpNotFoundError:
            pass

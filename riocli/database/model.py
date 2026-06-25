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

from rapyuta_io_sdk_v2 import Client as v2Client
from rapyuta_io_sdk_v2 import Database as DatabaseModel
from typing_extensions import override

from riocli.model import Model


class Database(Model):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.update(*args, **kwargs)
        self._obj = DatabaseModel.model_validate(self)

    @override
    def create_object(
        self, v2_client: v2Client, retry_count: int, retry_interval: int, *args, **kwargs
    ) -> DatabaseModel:
        return v2_client.create_database(body=self._obj)  # pyright:ignore[reportArgumentType]

    @override
    def update_object(
        self, v2_client: v2Client, retry_count: int, retry_interval: int, *args, **kwargs
    ) -> DatabaseModel:
        return v2_client.update_database(name=self._obj.metadata.name, body=self._obj)  # pyright:ignore[reportArgumentType]

    @override
    def delete_object(self, v2_client: v2Client, *args, **kwargs) -> None:
        _ = v2_client.delete_database(self._obj.metadata.name)

    @override
    def list_dependencies(self) -> list[str] | None:
        return None

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

from rapyuta_io_sdk_v2 import Backup as BackupModel
from rapyuta_io_sdk_v2 import Client as v2Client
from typing_extensions import override

from riocli.model import Model


class Backup(Model):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.update(*args, **kwargs)
        self._obj = BackupModel.model_validate(self)

    @override
    def create_object(self, v2_client: v2Client, *args, **kwargs) -> BackupModel:
        return v2_client.create_backup(body=self._obj)  # pyright:ignore[reportArgumentType]

    @override
    def update_object(self, v2_client: v2Client, *args, **kwargs) -> BackupModel:
        # Backups are immutable; the API exposes no update operation.
        raise NotImplementedError

    @override
    def delete_object(self, v2_client: v2Client, *args, **kwargs) -> None:
        _ = v2_client.delete_backup(self._obj.metadata.name)

    @override
    def list_dependencies(self) -> list[str] | None:
        # The source database is the backup's only dependency.
        return [f"database:{self._obj.spec.database}"]

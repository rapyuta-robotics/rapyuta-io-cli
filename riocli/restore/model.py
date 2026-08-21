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
from rapyuta_io_sdk_v2 import Restore as RestoreModel
from typing_extensions import override

from riocli.model import Model


class Restore(Model):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.update(*args, **kwargs)
        self._obj = RestoreModel.model_validate(self)

    @override
    def create_object(self, v2_client: v2Client, *args, **kwargs) -> RestoreModel:
        return v2_client.create_restore(body=self._obj)  # pyright:ignore[reportArgumentType]

    @override
    def update_object(self, v2_client: v2Client, *args, **kwargs) -> RestoreModel:
        # A restore is a one-shot operation: its spec is immutable and the API
        # exposes no update. Re-applying an existing restore does not re-run it.
        raise NotImplementedError

    @override
    def delete_object(self, v2_client: v2Client, *args, **kwargs) -> None:
        # The API exposes no restore delete: a restore runs to a terminal phase
        # and stays as an audit record. Deleting the target database is what
        # stops one that is still in flight.
        raise NotImplementedError

    @override
    def list_dependencies(self) -> list[str] | None:
        # The target database must exist and be running before a restore can run.
        deps = [f"database:{self._obj.spec.database}"]

        # A named backup is ordering information only — the archive is addressed
        # by its own GUID or filename, and a dataDirectory source is a path on
        # the device with no manifest to depend on.
        if self._obj.spec.source.type == "backup" and self._obj.spec.source.backup_name:
            deps.append(f"backup:{self._obj.spec.source.backup_name}")

        return deps

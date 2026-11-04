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

from riocli.database.util import wait_until_deleted, wait_until_listed
from riocli.model import Model


class Database(Model):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.update(*args, **kwargs)
        self._obj = DatabaseModel.model_validate(self)

    @override
    def create_object(self, v2_client: v2Client, *args, **kwargs) -> DatabaseModel:
        for name in self._secret_names():
            wait_until_listed(v2_client.get_secret, "secret", name)
        return v2_client.create_database(body=self._obj)  # pyright:ignore[reportArgumentType]

    @override
    def update_object(self, v2_client: v2Client, *args, **kwargs) -> DatabaseModel:
        return v2_client.update_database(name=self._obj.metadata.name, body=self._obj)  # pyright:ignore[reportArgumentType]

    @override
    def delete_object(self, v2_client: v2Client, *args, **kwargs) -> None:
        _ = v2_client.delete_database(self._obj.metadata.name)
        wait_until_deleted(v2_client.get_database, "database", self._obj.metadata.name)

    @override
    def list_dependencies(self) -> list[str] | None:
        return [f"secret:{name}" for name in self._secret_names()] or None

    def _secret_names(self) -> list[str]:
        postgres = self._obj.spec.postgres
        users = postgres.users if postgres is not None else None
        if users is None:
            return []

        names: set[str] = set()
        for creds in (users.primary, users.backup, users.replication):
            if creds is None:
                continue
            for ref in (creds.username, creds.password):
                if ref is not None and ref.name:
                    names.add(ref.name)

        return sorted(names)

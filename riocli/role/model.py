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

from munch import Munch
from rapyuta_io_sdk_v2 import Client
from rapyuta_io_sdk_v2 import Role as RoleModel
from rapyuta_io_sdk_v2 import RoleBinding as RoleBindingModel
from typing_extensions import override

from riocli.model import Model


class Role(Model):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.update(*args, **kwargs)
        self._obj = RoleModel.model_validate(self)

    @override
    def create_object(self, v2_client: Client, *args, **kwargs) -> Munch | None:
        return v2_client.create_role(self._obj)  # pyright:ignore[reportArgumentType]

    @override
    def update_object(self, v2_client: Client, *args, **kwargs) -> Munch | None:
        return v2_client.update_role(self._obj)  # pyright:ignore[reportArgumentType]

    @override
    def delete_object(self, v2_client: Client, *args, **kwargs) -> None:
        _ = v2_client.delete_role(self._obj.metadata.name)

    @override
    def list_dependencies(self) -> list[str] | None:
        return None


class RoleBinding(Model):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.update(*args, **kwargs)
        self._obj = RoleBindingModel.model_validate(self)

    @override
    def create_object(self, v2_client: Client, *args, **kwargs) -> Munch | None:
        return v2_client.update_role_binding(self._obj)  # pyright:ignore[reportArgumentType]

    @override
    def update_object(self, v2_client: Client, *args, **kwargs) -> Munch | None:
        return v2_client.update_role_binding(self._obj)  # pyright:ignore[reportArgumentType]

    @override
    def delete_object(self, v2_client: Client, *args, **kwargs) -> None:
        _ = v2_client.update_role_binding(self._obj)

    @override
    def list_dependencies(self) -> list[str] | None:
        return self._obj.list_dependencies()

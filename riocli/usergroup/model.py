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
from rapyuta_io_sdk_v2 import UserGroupCreate as UserGroupModel
from typing_extensions import override

from riocli.model import Model
from riocli.usergroup.util import find_usergroup_guid

USER_GUID = "guid"
USER_EMAIL = "emailID"


class UserGroup(Model):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.update(*args, **kwargs)
        self._obj = UserGroupModel.model_validate(self)

    @override
    def create_object(self, v2_client: Client, *args, **kwargs) -> Munch | None:
        return v2_client.create_user_group(user_group=self._obj)  # pyright:ignore[reportArgumentType]

    @override
    def update_object(self, v2_client: Client, *args, **kwargs) -> Munch | None:
        group_guid = self._obj.metadata.guid or None
        if group_guid is None:
            group_guid = find_usergroup_guid(v2_client, self._obj.metadata.name)
        self._obj.metadata.guid = group_guid
        return v2_client.update_user_group(
            user_group=self._obj,  # pyright:ignore[reportArgumentType]
        )

    @override
    def delete_object(self, v2_client: Client, *args, **kwargs) -> None:
        group_guid = self._obj.metadata.guid or None
        if group_guid is None:
            group_guid = find_usergroup_guid(
                v2_client, group_name=self._obj.metadata.name
            )

        _ = v2_client.delete_user_group(
            group_guid=group_guid, group_name=self._obj.metadata.name
        )

    @override
    def list_dependencies(self) -> list[str] | None:
        self._obj.list_dependencies()

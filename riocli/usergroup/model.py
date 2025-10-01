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
from rapyuta_io_sdk_v2 import Client
from typing_extensions import override

from riocli.model import Model
from riocli.usergroup.util import UserGroupNotFound, find_usergroup_guid
from rapyuta_io_sdk_v2.utils import walk_pages

USER_GUID = "guid"
USER_EMAIL = "emailID"


class UserGroup(Model):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.update(*args, **kwargs)

    @override
    def create_object(self, v2_client: Client, *args, **kwargs) -> Munch | None:
        return v2_client.create_usergroup(unmunchify(self))  # pyright:ignore[reportArgumentType]

    @override
    def update_object(self, v2_client: Client, *args, **kwargs) -> Munch | None:
        group_guid = self.metadata.get("guid")
        if group_guid is None:
            group_guid = find_usergroup_guid(v2_client, self.metadata.name)

        return v2_client.update_usergroup(
            group_guid,
            self.metadata.name,
            unmunchify(self),  # pyright:ignore[reportArgumentType]
        )

    @override
    def delete_object(self, v2_client: Client, *args, **kwargs) -> None:
        group_guid = self.metadata.get("guid")
        if group_guid is None:
            group_guid = find_usergroup_guid(v2_client, self.metadata.name)

        _ = v2_client.delete_usergroup(group_guid, self.metadata.name)

    @override
    def list_dependencies(self) -> list[str] | None:
        dependencies: list[str] = []

        for member in self.spec.members:
            subject = f"{member.subject.kind.lower()}:{member.subject.name}"
            dependencies.append(subject)

            for role in member.roles:
                dependencies.append(f"role:{role}")

        for group_role in self.spec.roles:
            domain = f"{group_role.domain.kind.lower()}:{group_role.domain.name}"
            dependencies.append(domain)

            for role in group_role.roles:
                dependencies.append(f"role:{role}")

        return dependencies

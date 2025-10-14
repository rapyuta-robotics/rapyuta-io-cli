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
import json
import typing

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

        org = v2client.get_organization(organization_guid=organization_id)
        user_projects = []
        for page in walk_pages(
            v2client.list_projects, organizations=[organization_id], limit=100
        ):
            user_projects.extend(page)

        self.project_name_to_guid_map = {
            p.metadata.name: p.metadata.guid for p in user_projects
        }
        self.user_email_to_guid_map = {
            self._sanitize_email(user.emailID): user.guid for user in org.spec.users
        }

        for member in self.spec.members:
            subject = f"{member.subject.kind.lower()}:{member.subject.name}"
            dependencies.append(subject)

        if not existing:
            try:
                payload["spec"]["name"] = sanitized["metadata"]["name"]
                v1client.create_usergroup(org_guid=self.metadata.organization, usergroup=payload["spec"])
                return ApplyResult.CREATED
            except Exception as e:
                raise e

        for group_role in self.spec.roles:
            domain = f"{group_role.domain.kind.lower()}:{group_role.domain.name}"
            dependencies.append(domain)

            for role in group_role.roles:
                dependencies.append(f"role:{role}")

        return dependencies

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
from typing import override
from munch import Munch, unmunchify

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
                v1client.create_usergroup(
                    org_guid=self.metadata.organization, usergroup=payload["spec"]
                )
                return ApplyResult.CREATED
            except Exception as e:
                raise e

        for group_role in self.spec.roles:
            domain = f"{group_role.domain.kind.lower()}:{group_role.domain.name}"
            dependencies.append(domain)

            for role in group_role.roles:
                dependencies.append(f"role:{role}")

        organization_id = self.metadata.organization or Configuration().organization_guid

        try:
            guid = find_usergroup_guid(v1client, organization_id, self.metadata.name)
            v1client.delete_usergroup(organization_id, guid)
        except UserGroupNotFound:
            raise ResourceNotFound
        except Exception as e:
            raise e

    def _sanitize(self) -> dict:
        u = unmunchify(self)
        u.pop("project_name_to_guid_map", None)
        u.pop("user_email_to_guid_map", None)

        return u

    def _modify_payload(self, group: dict) -> dict:
        group["spec"]["userGroupRoleInProjects"] = []
        for entity in ("members", "admins"):
            for u in group["spec"].get(entity, []):
                if USER_GUID in u:
                    continue
                email = self._sanitize_email(u[USER_EMAIL])
                u[USER_GUID] = self.user_email_to_guid_map.get(email)
                u.pop(USER_EMAIL)

        for p in group["spec"].get("projects", []):
            if "guid" not in p:
                p["guid"] = self.project_name_to_guid_map.get(p["name"])
                p.pop("name")

            if "role" in p:
                group["spec"]["userGroupRoleInProjects"].append(
                    {
                        "projectGUID": p["guid"],
                        "groupRole": p["role"],
                    }
                )
                p.pop("role")

        return group

    @staticmethod
    def _generate_update_payload(old: typing.Any, new: dict) -> dict:
        payload = {
            "name": old.name,
            "guid": old.guid,
            "description": new["spec"]["description"],
            "update": {
                "members": {"add": [], "remove": []},
                "projects": {"add": [], "remove": []},
                "admins": {"add": [], "remove": []},
            },
            "userGroupRoleInProjects": new["spec"].get("userGroupRoleInProjects", []),
        }

        entity_sets = {
            "members": {
                "old": set(),
                "new": set(),
            },
            "admins": {
                "old": set(),
                "new": set(),
            },
            "projects": {
                "old": set(),
                "new": set(),
            },
        }

        for entity in ("members", "projects", "admins"):
            # Assure that the group creator is not removed
            old_set = {
                i.guid for i in (getattr(old, entity) or []) if i.guid != old.creator
            }
            new_set = {i["guid"] for i in new["spec"].get(entity, [])}

            entity_sets[entity]["old"] = old_set
            entity_sets[entity]["new"] = new_set

        for entity in ("projects", "admins"):
            new = entity_sets[entity]["new"]
            old = entity_sets[entity]["old"]
            added = new - old
            removed = old - new

            payload["update"][entity]["add"] = [{"guid": guid} for guid in added]
            payload["update"][entity]["remove"] = [{"guid": guid} for guid in removed]

        # Handle special cases in the members section separately
        new_members = entity_sets["members"]["new"]
        old_members = entity_sets["members"]["old"]
        added_members = new_members - old_members
        removed_members = old_members - new_members

        # Additional handling to avoid active admins becoming a part of
        # removed members set which leads to their removal altogether.
        removed_members = removed_members - entity_sets["admins"]["new"]

        payload["update"]["members"]["add"] = [{"guid": guid} for guid in added_members]
        payload["update"]["members"]["remove"] = [
            {"guid": guid} for guid in removed_members
        ]

        # This is a special case where admins are not added to the membership list
        # And as a consequence they don't show up in the group. This will fix that.
        payload["update"]["members"]["add"].extend(payload["update"]["admins"]["add"])

        return dependencies

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
import typing

from munch import unmunchify

from riocli.config import Configuration, new_client, new_v2_client
from riocli.constants import ApplyResult
from riocli.exceptions import ResourceNotFound
from riocli.model import Model
from riocli.usergroup.util import UserGroupNotFound, find_usergroup_guid

USER_GUID = "guid"
USER_EMAIL = "emailID"


class UserGroup(Model):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.update(*args, **kwargs)

        self.user_email_to_guid_map = {}
        self.project_name_to_guid_map = {}

    def apply(self, *args, **kwargs) -> ApplyResult:
        v1client = new_client()
        v2client = new_v2_client()

        organization_id = self.metadata.organization or Configuration().organization_guid
        existing = None

        try:
            guid = find_usergroup_guid(v1client, organization_id, self.metadata.name)
            existing = v1client.get_usergroup(organization_id, guid)
        except UserGroupNotFound:
            pass
        except Exception as e:
            raise e

        org = v2client.get_organization(organization_id)
        user_projects = v2client.list_projects(organization_id)

        self.project_name_to_guid_map = {
            p["metadata"]["name"]: p["metadata"]["guid"] for p in user_projects
        }
        self.user_email_to_guid_map = {
            self._sanitize_email(user[USER_EMAIL]): user[USER_GUID] for user in org.spec.users
        }

        sanitized = self._sanitize()
        payload = self._modify_payload(sanitized)

        if not existing:
            try:
                payload["spec"]["name"] = sanitized["metadata"]["name"]
                v1client.create_usergroup(self.metadata.organization, payload["spec"])
                return ApplyResult.CREATED
            except Exception as e:
                raise e

        payload = self._generate_update_payload(existing, payload)
        v1client.update_usergroup(organization_id, existing.guid, payload)
        return ApplyResult.UPDATED

    def delete(self, *args, **kwargs) -> None:
        v1client = new_client()

        organization_id = self.metadata.organization or Configuration().organization_guid

        try:
            guid = find_usergroup_guid(v1client, organization_id, self.metadata.name)
            v1client.delete_usergroup(organization_id, guid)
        except UserGroupNotFound:
            raise ResourceNotFound
        except Exception as e:
            raise e

    def _sanitize(self) -> typing.Dict:
        u = unmunchify(self)
        u.pop("project_name_to_guid_map", None)
        u.pop("user_email_to_guid_map", None)

        return u

    def _modify_payload(self, group: typing.Dict) -> typing.Dict:
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
    def _generate_update_payload(old: typing.Any, new: typing.Dict) -> typing.Dict:
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

        return payload

    @staticmethod
    def _sanitize_email(email:str) -> str:
        return email.lower().strip()

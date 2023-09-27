# Copyright 2023 Rapyuta Robotics
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
from rapyuta_io import Client

from riocli.config import new_v2_client
from riocli.jsonschema.validate import load_schema
from riocli.model import Model
from riocli.organization.utils import get_organization_details

USER_GUID = 'guid'
USER_EMAIL = 'emailID'


class UserGroup(Model):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        v2client = new_v2_client()
        organization_details = get_organization_details(self.metadata.organization)
        user_projects = v2client.list_projects(self.metadata.organization)

        self.project_name_to_guid_map = {p['metadata']['name']: p['metadata']['guid'] for p in user_projects}
        self.user_email_to_guid_map = {user[USER_EMAIL]: user[USER_GUID] for user in organization_details['users']}

    def unmunchify(self) -> typing.Dict:
        """Unmuchify self"""
        usergroup = unmunchify(self)
        usergroup.pop('rc', None)
        usergroup.pop('project_name_to_guid_map', None)
        usergroup.pop('user_email_to_guid_map', None)

        return usergroup

    def find_object(self, client: Client) -> typing.Any:
        group_guid, usergroup = self.rc.find_depends({
            'kind': self.kind.lower(),
            'nameOrGUID': self.metadata.name,
            'organization': self.metadata.organization
        })

        if not usergroup:
            return False

        return usergroup

    def create_object(self, client: Client, **kwargs) -> typing.Any:
        usergroup = self.unmunchify()
        payload = self._modify_payload(usergroup)
        # Inject the user group name in the payload
        payload['spec']['name'] = usergroup['metadata']['name']
        return client.create_usergroup(self.metadata.organization, payload['spec'])

    def update_object(self, client: Client, obj: typing.Any) -> typing.Any:
        payload = self._modify_payload(self.unmunchify())
        payload = self._create_update_payload(obj, payload)
        return client.update_usergroup(self.metadata.organization, obj.guid, payload)

    def delete_object(self, client: Client, obj: typing.Any) -> typing.Any:
        return client.delete_usergroup(self.metadata.organization, obj.guid)

    def _modify_payload(self, group: typing.Dict) -> typing.Dict:
        group['spec']['userGroupRoleInProjects'] = []
        for entity in ('members', 'admins'):
            for u in group['spec'].get(entity, []):
                if USER_GUID in u:
                    continue
                u[USER_GUID] = self.user_email_to_guid_map.get(u[USER_EMAIL])
                u.pop(USER_EMAIL)

        for p in group['spec'].get('projects', []):
            if 'guid' not in p:
                p['guid'] = self.project_name_to_guid_map.get(p['name'])
                p.pop('name')

            if 'role' in p:
                group['spec']['userGroupRoleInProjects'].append({
                    'projectGUID': p['guid'],
                    'groupRole': p['role'],
                })
                p.pop('role')

        return group

    @classmethod
    def pre_process(cls, client: Client, d: typing.Dict) -> None:
        pass

    @staticmethod
    def validate(data):
        schema = load_schema('usergroup')
        schema.validate(data)

    @staticmethod
    def _create_update_payload(old: typing.Any, new: typing.Dict) -> typing.Dict:
        payload = {
            'name': old.name,
            'guid': old.guid,
            'description': new['spec']['description'],
            'update': {
                'members': {'add': [], 'remove': []},
                'projects': {'add': [], 'remove': []},
                'admins': {'add': [], 'remove': []}
            },
            'userGroupRoleInProjects': new['spec'].get('userGroupRoleInProjects', []),
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
            }
        }

        for entity in ('members', 'projects', 'admins'):
            # Assure that the group creator is not removed
            old_set = {i.guid for i in (getattr(old, entity) or []) if i.guid != old.creator}
            new_set = {i['guid'] for i in new['spec'].get(entity, [])}

            entity_sets[entity]["old"] = old_set
            entity_sets[entity]["new"] = new_set

        for entity in ('projects', 'admins'):
            new = entity_sets[entity]['new']
            old = entity_sets[entity]['old']
            added = new - old
            removed = old - new

            payload['update'][entity]['add'] = [{'guid': guid} for guid in added]
            payload['update'][entity]['remove'] = [{'guid': guid} for guid in removed]

        # Handle special cases in the members section separately
        new_members = entity_sets['members']['new']
        old_members = entity_sets['members']['old']
        added_members = new_members - old_members
        removed_members = old_members - new_members

        # Additional handling to avoid active admins becoming a part of
        # removed members set which leads to their removal altogether.
        removed_members = removed_members - entity_sets['admins']['new']

        payload['update']['members']['add'] = [{'guid': guid} for guid in added_members]
        payload['update']['members']['remove'] = [{'guid': guid} for guid in removed_members]

        # This is a special case where admins are not added to the membership list
        # And as a consequence they don't show up in the group. This will fix that.
        payload['update']['members']['add'].extend(payload['update']['admins']['add'])

        return payload

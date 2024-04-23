# Copyright 2024 Rapyuta Robotics
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
import functools
import json
import re
import typing

from munch import munchify
from rapyuta_io import DeploymentPhaseConstants
from rapyuta_io.utils.rest_client import HttpMethod, RestClient

from riocli.config import new_v2_client
from riocli.config.config import Configuration
from riocli.deployment.model import Deployment
from riocli.device.model import Device
from riocli.disk.model import Disk
from riocli.managedservice.model import ManagedService
from riocli.network.model import Network
from riocli.package.model import Package
from riocli.project.model import Project
from riocli.secret.model import Secret
from riocli.static_route.model import StaticRoute
from riocli.usergroup.model import UserGroup


class _Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(
                _Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class ResolverCache(object, metaclass=_Singleton):
    KIND_TO_CLASS = {
        'Project': Project,
        'Secret': Secret,
        'Device': Device,
        'Network': Network,
        'StaticRoute': StaticRoute,
        'Package': Package,
        'Disk': Disk,
        'Deployment': Deployment,
        "ManagedService": ManagedService,
        'UserGroup': UserGroup,
    }

    KIND_REGEX = {
        "organization": "^org-[a-z]{24}$",
        "project": "^project-[a-z]{24}$",
        "secret": "^secret-[a-z]{24}$",
        "package": "^pkg-[a-z0-9]{20}$",
        "staticroute": "^staticroute-[a-z]{24}$",
        "disk": "^disk-[a-z]{24}$",
        "deployment": "^dep-[a-z]{24}$",
        "network": "^net-[a-z]{24}$",
        "device": "^[a-fA-F0-9]{8}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{12}$",
        "user": "^[a-fA-F0-9]{8}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{12}$",
        "managedservice": "^[a-zA-Z][a-zA-Z0-9_-]$"
    }

    GUID_KEYS = ['guid', 'GUID', 'deploymentId', 'uuid', 'ID', 'Id', 'id']
    NAME_KEYS = ['name', 'urlPrefix']

    def __init__(self, client):
        self.client = client
        self.v2client = new_v2_client()

    @functools.lru_cache()
    def list_objects(self, kind):
        return self._list_functors(kind)()

    @functools.lru_cache()
    def find_guid(self, name, kind, *args):
        obj_list = self.list_objects(kind)
        obj_match = list(self._find_functors(kind)(name, obj_list, *args))
        if obj_match and isinstance(obj_match, list) and len(obj_match) > 0:
            return obj_match[0]
        else:
            return None

    def find_depends(self, depends, *args):
        if 'depGuid' in depends and depends['kind'] == 'disk':
            return depends['depGuid'], None
        elif 'guid' in depends and depends['kind'] not in ('network', 'managedservice'):
            return depends['guid'], None
        elif 'nameOrGUID' in depends:
            if depends['kind'] == 'usergroup':
                org_guid = depends['organization']
                obj_list = self._list_functors(depends['kind'])(org_guid)
            else:
                obj_list = self._list_functors(depends['kind'])()

            obj_match = list(self._find_functors(depends['kind'])(
                depends['nameOrGUID'], obj_list, *args))
            if not obj_list or (isinstance(obj_list, list) and len(obj_list) == 0):
                return None, None
            if obj_match and isinstance(obj_match, list) and len(obj_match) > 0:
                return self._guid_functor(depends['kind'])(obj_match[0]), obj_match[0]
            else:
                return None, None
        return None, None

    def _guid_functor(self, kind):
        mapping = {
            'secret': lambda x: munchify(x).metadata.guid,
            "project": lambda x: munchify(x).metadata.guid,
            "package": lambda x: munchify(x)['metadata']['guid'],
            "staticroute": lambda x: munchify(x)['metadata']['guid'],
            "deployment": lambda x: munchify(x)['metadata']['guid'],
            "network": lambda x: munchify(x)['metadata']['guid'],
            # This is only temporarily like this
            "disk": lambda x: munchify(x)['metadata']['guid'],
            "device": lambda x: munchify(x)['uuid'],
            "managedservice": lambda x: munchify(x)['metadata']['name'],
            "usergroup": lambda x: munchify(x).guid
        }
        return mapping[kind]

    def _list_functors(self, kind):
        mapping = {
            'secret': self.v2client.list_secrets,
            "project": self.v2client.list_projects,
            "package": self.v2client.list_packages,
            "staticroute": self.v2client.list_static_routes,
            "disk": self.v2client.list_disks,
            "network": self.v2client.list_networks,
            "deployment": functools.partial(self.v2client.list_deployments),
            "device": self.client.get_all_devices,
            "managedservice": self._list_managedservices,
            "usergroup": self.client.list_usergroups
        }

        return mapping[kind]

    def _find_functors(self, kind):
        mapping = {
            'secret': lambda name, secrets: filter(lambda i: i.metadata.name == name, secrets),
            "project": lambda name, projects: filter(lambda i: i.metadata.name == name, projects),
            "package": lambda name, obj_list, version: filter(
                lambda x: name == x.metadata.name and version == x.metadata.version, obj_list),
            "staticroute": lambda name, obj_list: filter(
                lambda x: name == x.metadata.name.rsplit('-', 1)[0], obj_list),
            "network": lambda name, obj_list, network_type: filter(
                lambda x: name == x.metadata.name and network_type == x.spec.type,  obj_list),
            "deployment": lambda name, obj_list: filter(
                lambda x: name == x.metadata.name, obj_list),
            "disk": lambda name, obj_list: filter(
                lambda x: name == x.metadata.name,  obj_list),
            "device": self._generate_find_guid_functor(),
            "managedservice": lambda name, instances: filter(lambda i: i.metadata.name == name, instances),
            "usergroup": lambda name, groups: filter(lambda i: i.name == name, groups),
        }

        return mapping[kind]

    def _generate_find_guid_functor(self, name_field='name'):
        return lambda name, obj_list: filter(lambda x: name == getattr(x, name_field), obj_list)

    def _list_networks(self):
        native = self.client.list_native_networks()
        routed = self.client.get_all_routed_networks()

        networks = []
        if native:
            networks.extend(native)

        if routed:
            networks.extend(routed)

        return networks

    def _list_managedservices(self):
        instances = ManagedService.list_instances()
        return munchify(instances)

    @classmethod
    def _maybe_guid(cls, kind: str, name_or_guid: str) -> typing.Union[str, None]:
        if re.fullmatch(cls.KIND_REGEX[kind], name_or_guid):
            return name_or_guid

    @classmethod
    def get_model(cls, data: dict) -> typing.Any:
        kind = data.get('kind', None)
        if not kind:
            raise Exception('kind is missing')

        kind_cls = cls.KIND_TO_CLASS.get(kind, None)
        if not kind_cls:
            raise Exception('invalid kind {}'.format(kind))

        return kind_cls

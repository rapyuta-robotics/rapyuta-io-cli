# Copyright 2022 Rapyuta Robotics
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
from graphlib import TopologicalSorter

import click
import yaml
from munch import munchify
from rapyuta_io import DeploymentPhaseConstants
from rapyuta_io.utils.rest_client import HttpMethod, RestClient

from riocli.build.model import Build
from riocli.config import Configuration
from riocli.deployment.model import Deployment
from riocli.device.model import Device
from riocli.disk.model import Disk
from riocli.network.model import Network
from riocli.package.model import Package
from riocli.project.model import Project
from riocli.secret.model import Secret
from riocli.static_route.model import StaticRoute
from riocli.secret.util import find_secret_guid

class _Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(_Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]

class Applier(object):
    KIND_TO_CLASS = {
        'Project': Project,
        'Secret': Secret,
        'Build': Build,
        'Device': Device,
        'Network': Network,
        'StaticRoute': StaticRoute,
        'Package': Package,
        'Disk': Disk,
        'Deployment': Deployment,
    }
    KIND_REGEX = {
        "organization": "^org-[a-z]{24}$",
        "project": "^project-[a-z]{24}$",
        "secret": "^secret-[a-z]{24}$",
        "package": "^pkg-[a-z]{24}$",
        "staticroute": "^staticroute-[a-z]{24}$",
        "build": "^build-[a-z]{24}$",
        "disk": "^disk-[a-z]{24}$",
        "deployment": "^dep-[a-z]{24}$",
        "network": "^net-[a-z]{24}$",
        "device": "^[a-fA-F0-9]{8}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{12}$",
        "user": "^[a-fA-F0-9]{8}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{12}$",
    }
    GUID_KEYS = ['guid', 'GUID', 'uuid', 'ID', 'Id', 'id']
    NAME_KEYS = ['name', 'urlPrefix']

    def __init__(self, files: typing.List):
        self.input_file_paths = files
        self.config = Configuration()
        self.client = self.config.new_client()
        self.dependencies = {}
        self.objects = {}
        self.resolved_objects = {}
        self.files = {}
        self.graph = TopologicalSorter()
        self.rc = ResolverCache(self.client)
        self._read_files(files)

    def parse_dependencies(self):
        for f, data in self.files.items():
            for model in data:
                key = self._get_object_key(model)
                self._parse_dependency(key, model)
                self.graph.add(key)

        self.graph.prepare()

        missing_resources = []
        for key, item in self.resolved_objects.items():
            if 'src' in item and item['src'] == 'missing':
                missing_resources.append(key)

        if(missing_resources):
            click.secho("missing resources found in yaml. " + \
                            "Plese ensure the following are either available in your yaml" + \
                            "or created on the server. {}".format(set(missing_resources))
                        , fg="red")
            exit(1)

    def apply(self):
        while self.graph.is_active():
            for obj in self.graph.get_ready():
                if obj in self.resolved_objects and 'manifest' in self.resolved_objects[obj]:
                    self._apply_manifest(obj)
                self.graph.done(obj)    

    def delete(self):
        delete_order = list(self.graph.static_order()).reverse()

    def _apply_manifest(self, obj_key):
        obj = self.objects[obj_key]
        cls = self.get_model(obj)
        ist = cls.from_dict(self.client, obj)
        setattr(ist, 'rc', ResolverCache(self.client))
        ist.apply(self.client)
    
    def _apply_manifest(self, obj_key):
        obj = self.objects[obj_key]
        cls = self.get_model(obj)
        ist = cls.from_dict(self.client, obj)
        setattr(ist, 'rc', ResolverCache(self.client))
        ist.apply(self.client)

    def _read_files(self, files):
        for f in files:
            with open(f) as opened:
                data = opened.read()

            loaded_data = []
            if f.endswith("json"):
                # FIXME: Handle for JSON List.
                loaded = json.loads(data)
                loaded_data.append(loaded)
            elif f.endswith('yaml') or f.endswith('yml'):
                loaded = yaml.safe_load_all(data)
                loaded_data = list(loaded)

            if not loaded_data:
                click.secho('{} file is empty', f)
                continue

            for obj in loaded_data:
                self._register_object(obj)

            self.files[f] = loaded_data

    def _register_object(self, data):
        try:
            key = self._get_object_key(data)
            self.objects[key] = data
            self.resolved_objects[key] = {'src' : 'local', 'manifest': data}
        except KeyError:
            print("key error {}".format(data))
            return

    def _parse_dependency(self, dependent_key, model):
        for key, value in model.items():
            if key == "depends" :
                if 'kind' in value and value.get('kind'):
                    self._resolve_dependency(dependent_key, value)
                if isinstance(value, list):
                    for each in value:
                        if isinstance(each, dict) and each.get('kind'):
                            self._resolve_dependency(dependent_key, each)

                continue

            if isinstance(value, dict):
                self._parse_dependency(dependent_key, value)
                continue

            if isinstance(value, list):
                for each in value:
                    if isinstance(each, dict):
                        self._parse_dependency(dependent_key, each)


    def _add_remote_object_to_resolve_tree(self, dependent_key, guid, dependency, obj):
        kind = dependency.get('kind')
        name_or_guid = dependency.get('nameOrGUID')
        key = '{}:{}'.format(kind, name_or_guid)

        self.dependencies[kind][name_or_guid] = {'guid': guid, 'raw': obj, 'local': False}
        if key not in self.resolved_objects:
            self.resolved_objects[key] = {} 
        self.resolved_objects[key]['guid'] = guid
        self.resolved_objects[key]['raw'] = obj
        self.resolved_objects[key]['src'] = 'remote'

        self.graph.add(dependent_key, key)
        dependency['guid'] = guid
        if kind.lower() == "disk":
            dependency['depGuid'] = obj['internalDeploymentGUID']
        
        if kind.lower() == "deployment":
            dependency['guid'] = obj['deploymentId']
            

    def _resolve_dependency(self, dependent_key, dependency):
        kind = dependency.get('kind')
        name_or_guid = dependency.get('nameOrGUID')
        key = '{}:{}'.format(kind, name_or_guid)

        self._initialize_kind_dependency(kind)
        guid = self._maybe_guid(kind, name_or_guid)

        obj_list = self.rc.list_objects(kind)
        for obj in obj_list:
            obj_guid = self._get_attr(obj, self.GUID_KEYS)
            obj_name = self._get_attr(obj, self.NAME_KEYS)
            
            
            if kind == 'package':
                if (guid and obj_guid == guid):
                    self._add_remote_object_to_resolve_tree(dependent_key, obj_guid, dependency, obj)
                
                if (name_or_guid == obj_name) and ('version' in dependency and obj['packageVersion'] == dependency.get('version')):
                    self._add_remote_object_to_resolve_tree(dependent_key, obj_guid, dependency, obj)
            
            # Special handling for Static route since it doesn't have a name field.
            # StaticRoute sends a URLPrefix field with name being the prefix along with short org guid.
            elif kind == 'staticroute' and name_or_guid in obj_name:
                self._add_remote_object_to_resolve_tree(dependent_key, obj_guid, dependency, obj)

            elif (guid and obj_guid == guid) or (name_or_guid == obj_name):
                self._add_remote_object_to_resolve_tree(dependent_key, obj_guid, dependency, obj)
                

        self.dependencies[kind][name_or_guid] = {'local': True}
        self.graph.add(dependent_key, key)
        
        if key not in self.resolved_objects:
            self.resolved_objects[key] = {'src' : 'missing'}


    def order(self):
        return self.graph.static_order()

    @staticmethod
    def _get_attr(obj, accept_keys):
        for key in accept_keys:
            if hasattr(obj, key):
                return getattr(obj, key)

        raise Exception('guid resolve failed')

    @staticmethod
    def _get_object_key(obj: dict) -> str:
        kind = obj.get('kind').lower()
        name_or_guid = obj['metadata']['name']

        return '{}:{}'.format(kind, name_or_guid)

    def _initialize_kind_dependency(self, kind):
        if not self.dependencies.get(kind):
            self.dependencies[kind] = {}

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


class ResolverCache(object, metaclass=_Singleton):
    def __init__(self, client):
        self.client = client

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
        elif 'guid' in depends :
            return depends['guid'], None
        
        elif 'nameOrGUID' in depends:
            obj_list =  self._list_functors(depends['kind'])()
            obj_match = list(self._find_functors(depends['kind'])(depends['nameOrGUID'], obj_list, *args))
            if not obj_list or (isinstance(obj_list, list) and len(obj_list) == 0):
                return None
            if obj_match and isinstance(obj_match, list) and len(obj_match) > 0:
                return self._guid_functor(depends['kind'])(obj_match[0]), obj_match[0]
            else:
                return None
        return None

    def _guid_functor(self, kind):
        mapping = {
            'secret': lambda x: munchify(x).guid,
            "project": lambda x: munchify(x).guid,
            "package": lambda x: munchify(x)['id'],
            "staticroute": lambda x: munchify(x)['guid'],
            "build": lambda x: munchify(x)['guid'],
            "deployment": lambda x: munchify(x)['deploymentId'],
            "network": lambda x: munchify(x)['guid'],
            "disk": lambda x: munchify(x)['internalDeploymentGUID'], #This is only temporarity like this
            "device": lambda x: munchify(x)['uuid']
        }
        return mapping[kind]

    def _list_functors(self, kind):
        mapping = {
            'secret': self.client.list_secrets,
            "project": self.client.list_projects,
            "package": self.client.get_all_packages,
            "staticroute": self.client.get_all_static_routes,
            "build": self.client.list_builds,
            "deployment": functools.partial(self.client.get_all_deployments,
                                            phases=[DeploymentPhaseConstants.SUCCEEDED,
                                                    DeploymentPhaseConstants.PROVISIONING]),
            "network": self._list_networks,
            "disk": self._list_disks,
            "device": self.client.get_all_devices,
        }

        return mapping[kind]

    def _find_functors(self, kind):
        mapping = {
            'secret': self._generate_find_guid_functor(),
            "project": self._generate_find_guid_functor(),
            "package": lambda name, obj_list, version: filter(lambda x: name == x.name and version == x['packageVersion'], obj_list),
            "staticroute": lambda name, obj_list: filter(lambda x: name == '-'.join(x.urlPrefix.split('-')[:-1]), obj_list),
            "build": self._generate_find_guid_functor(),
            "deployment": self._generate_find_guid_functor(),
            "network": self._generate_find_guid_functor(),
            "disk": self._generate_find_guid_functor(),
            "device": self._generate_find_guid_functor(),
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

    def _list_disks(self):
        config = Configuration()
        catalog_host = config.data.get('catalog_host', 'https://gacatalog.apps.rapyuta.io')
        url = '{}/disk'.format(catalog_host)
        headers = config.get_auth_header()
        response = RestClient(url).method(HttpMethod.GET).headers(headers).execute()
        data = json.loads(response.text)
        if not response.ok:
            err_msg = data.get('error')
            raise Exception(err_msg)
        return munchify(data)


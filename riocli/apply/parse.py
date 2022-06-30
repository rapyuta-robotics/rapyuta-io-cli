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
import copy
import json
import typing
from graphlib import TopologicalSorter
from requests import head
from tabulate import tabulate

import click
import jinja2
import yaml

from riocli.apply.resolver import ResolverCache
from riocli.config import Configuration

class Applier(object):
    def __init__(self, files: typing.List, values):
        self.environment = None
        self.input_file_paths = files
        self.config = Configuration()
        self.client = self.config.new_client()
        self.dependencies = {}
        self.objects = {}
        self.resolved_objects = {}
        self.files = {}
        self.graph = TopologicalSorter()
        self.rc = ResolverCache(self.client)
        if values:
            self.values = self._read_file(values)[0]
            self.environment = jinja2.Environment()
        self._read_files(files)

    def parse_dependencies(self, check_missing=True):
        
        number_of_objects = 0
        for f, data in self.files.items():
            for model in data:
                key = self._get_object_key(model)
                self._parse_dependency(key, model)
                self.graph.add(key)
                number_of_objects = number_of_objects + 1

        EXPECTED_TIME = {
            "organization": 3,
            "project": 3,
            "secret": 3,
            "package": 3,
            "staticroute": 3,
            "build": 180,
            "disk": 180,
            "deployment": 240,
            "network": 120,
            "device": 5,
            "user": 3,

        }
        resource_list = []
        total_time = 0
        for node in copy.deepcopy(self.graph).static_order():
            action = 'CREATE' if not self.resolved_objects[node]['src'] == 'remote' else 'UPDATE'
            kind = node.split(":")[0]
            expected_time = round(EXPECTED_TIME.get(kind.lower(), 5)/60, 2)
            total_time = total_time + expected_time
            resource_list.append([node, action, expected_time])

        total_time = round(total_time, 2)
        click.secho("rapyuta.io Apply context", bg='white', fg="black")
        click.secho("Expected Runtime : {} mins".format(total_time) , fg="red")
        click.secho("File             : "+ str(len(self.files)), fg="yellow")
        click.secho("YAML object      : "+ str(number_of_objects), fg="yellow")
        
        click.secho("           Inventory", fg="yellow")
        click.secho(" "*50, bg='blue')
        click.secho(tabulate(resource_list, headers=["Resource", "Action", "Expected Time (mins)"]), fg='white')
        click.secho(" "*50, bg='blue')

        if check_missing:
            missing_resources = []
            for key, item in self.resolved_objects.items():
                if 'src' in item and item['src'] == 'missing':
                    missing_resources.append(key)

            if missing_resources:
                click.secho("missing resources found in yaml. " + \
                            "Plese ensure the following are either available in your yaml" + \
                            "or created on the server. {}".format(set(missing_resources)), fg="red")
                exit(1)

    def apply(self, *args, **kwargs):
        self.graph.prepare()
        while self.graph.is_active():
            for obj in self.graph.get_ready():
                if obj in self.resolved_objects and 'manifest' in self.resolved_objects[obj]:
                    self._apply_manifest(obj, *args, **kwargs)
                self.graph.done(obj)

    def _apply_manifest(self, obj_key, *args, **kwargs):
        obj = self.objects[obj_key]
        cls = ResolverCache.get_model(obj)
        ist = cls.from_dict(self.client, obj)
        setattr(ist, 'rc', ResolverCache(self.client))
        ist.apply(self.client, *args, **kwargs)

    def delete(self, *args, **kwargs):
        delete_order = list(self.graph.static_order())
        delete_order.reverse()
        for obj in delete_order:
            if obj in self.resolved_objects and 'manifest' in self.resolved_objects[obj]:
                self._delete_manifest(obj, *args, **kwargs)

    def _delete_manifest(self, obj_key, *args, **kwargs):
        obj = self.objects[obj_key]
        cls = ResolverCache.get_model(obj)
        ist = cls.from_dict(self.client, obj)
        setattr(ist, 'rc', ResolverCache(self.client))
        ist.delete(self.client, obj, *args, **kwargs)

    def _read_files(self, files):
        for f in files:
            data = self._read_file(f)
            for obj in data:
                self._register_object(obj)

            self.files[f] = data

    def _read_file(self, file_name):
        with open(file_name) as opened:
            data = opened.read()

        if self.environment:
            template = self.environment.from_string(data)
            data = template.render(**self.values)

        loaded_data = []
        if file_name.endswith("json"):
            # FIXME: Handle for JSON List.
            loaded = json.loads(data)
            loaded_data.append(loaded)
        elif file_name.endswith('yaml') or file_name.endswith('yml'):
            loaded = yaml.safe_load_all(data)
            loaded_data = list(loaded)

        if not loaded_data:
            click.secho('{} file is empty', file_name)

        return loaded_data

    def _register_object(self, data):
        try:
            key = self._get_object_key(data)
            self.objects[key] = data
            self.resolved_objects[key] = {'src': 'local', 'manifest': data}
        except KeyError:
            print("key error {}".format(data))
            return

    def _parse_dependency(self, dependent_key, model):
        for key, value in model.items():
            if key == "depends":
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
        guid = ResolverCache._maybe_guid(kind, name_or_guid)

        obj_list = self.rc.list_objects(kind)
        for obj in obj_list:
            obj_guid = self._get_attr(obj, ResolverCache.GUID_KEYS)
            obj_name = self._get_attr(obj, ResolverCache.NAME_KEYS)

            if kind == 'package':
                if (guid and obj_guid == guid):
                    self._add_remote_object_to_resolve_tree(dependent_key, obj_guid, dependency, obj)

                if (name_or_guid == obj_name) and (
                        'version' in dependency and obj['packageVersion'] == dependency.get('version')):
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
            self.resolved_objects[key] = {'src': 'missing'}

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

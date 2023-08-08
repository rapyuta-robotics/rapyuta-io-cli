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
import queue
import threading
import typing
from graphlib import TopologicalSorter

import click
import jinja2
import yaml
from tabulate import tabulate

from riocli.apply.resolver import ResolverCache
from riocli.config import Configuration
from riocli.constants import Colors, Symbols
from riocli.utils import dump_all_yaml, print_separator, run_bash
from riocli.utils.mermaid import mermaid_link, mermaid_safe
from riocli.utils.spinner import with_spinner


class Applier(object):
    DEFAULT_MAX_WORKERS = 6

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

    def __init__(self, files: typing.List, values, secrets):
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
        self.secrets = {}
        self.values = {}
        self.diagram = ["flowchart LR"]
        if values or secrets:
            self.environment = jinja2.Environment()

        if values:
            self.values = self._load_file_content(
                values, is_value=True, is_secret=False)[0]

        if secrets:
            self.secrets = self._load_file_content(
                secrets, is_value=True, is_secret=True)[0]

        self._process_file_list(files)

    # Public Functions
    def order(self):
        return self.graph.static_order()

    @with_spinner(text='Applying...', timer=True)
    def apply(self, *args, **kwargs):
        spinner = kwargs.get('spinner')
        kwargs['workers'] = int(kwargs.get('workers')
                                or self.DEFAULT_MAX_WORKERS)
        apply_func = self.apply_async
        if kwargs['workers'] == 1:
            apply_func = self.apply_sync

        try:
            apply_func(*args, **kwargs)
            spinner.text = 'Apply successful.'
            spinner.green.ok(Symbols.SUCCESS)
        except Exception as e:
            spinner.text = 'Apply failed. Error: {}'.format(e)
            spinner.red.fail(Symbols.ERROR)
            raise SystemExit(1) from e

    def apply_async(self, *args, **kwargs):
        workers = int(kwargs.get('workers') or self.DEFAULT_MAX_WORKERS)
        task_queue = queue.Queue()
        done_queue = queue.Queue()

        def worker():
            while True:
                o = task_queue.get()
                if o in self.resolved_objects and 'manifest' in \
                        self.resolved_objects[o]:
                    try:
                        self._apply_manifest(o, *args, **kwargs)
                    except Exception as ex:
                        click.secho(
                            '[Err] Object "{}" apply failed. Apply will not progress further.'.format(
                                o, str(ex)))
                        done_queue.put(ex)
                        continue

                task_queue.task_done()
                done_queue.put(o)

        worker_list = []
        for worker_id in range(workers):
            worker_list.append(threading.Thread(target=worker, daemon=True))
            worker_list[worker_id].start()

        self.graph.prepare()
        while self.graph.is_active():
            for obj in self.graph.get_ready():
                task_queue.put(obj)

            done_obj = done_queue.get()
            if not isinstance(done_obj, Exception):
                self.graph.done(done_obj)
            else:
                raise Exception(done_obj)

        task_queue.join()

    def apply_sync(self, *args, **kwargs):
        self.graph.prepare()
        while self.graph.is_active():
            for obj in self.graph.get_ready():
                if (obj in self.resolved_objects and
                        'manifest' in self.resolved_objects[obj]):
                    self._apply_manifest(obj, *args, **kwargs)
                self.graph.done(obj)

    @with_spinner(text='Deleting...', timer=True)
    def delete(self, *args, **kwargs):
        spinner = kwargs.get('spinner')
        delete_order = list(self.graph.static_order())
        delete_order.reverse()
        try:
            for obj in delete_order:
                if (obj in self.resolved_objects and
                        'manifest' in self.resolved_objects[obj]):
                    self._delete_manifest(obj, *args, **kwargs)
            spinner.text = 'Delete successful.'
            spinner.green.ok(Symbols.SUCCESS)
        except Exception as e:
            spinner.text = 'Delete failed. Error: {}'.format(e)
            spinner.red.fail(Symbols.ERROR)

    def print_resolved_manifests(self):
        manifests = [o for _, o in self.objects.items()]
        dump_all_yaml(manifests)

    def parse_dependencies(
            self,
            check_missing=True,
            delete=False,
            template=False
    ):
        number_of_objects = 0
        for f, data in self.files.items():
            for model in data:
                key = self._get_object_key(model)
                self._parse_dependency(key, model)
                self._add_graph_node(key)
                number_of_objects = number_of_objects + 1

        resource_list = []
        total_time = 0

        for node in copy.deepcopy(self.graph).static_order():
            action = 'UPDATE'
            if not self.resolved_objects[node]['src'] == 'remote':
                action = 'CREATE'
            elif delete:
                action = 'DELETE'
            kind = node.split(":")[0]
            expected_time = round(
                self.EXPECTED_TIME.get(kind.lower(), 5) / 60, 2)
            total_time += expected_time
            resource_list.append([node, action, expected_time])

        if not template:
            self._display_context(
                total_time=total_time,
                total_objects=number_of_objects,
                resource_list=resource_list
            )

        if check_missing:
            missing_resources = []
            for key, item in self.resolved_objects.items():
                if 'src' in item and item['src'] == 'missing':
                    missing_resources.append(key)

            if missing_resources:
                click.secho(
                    "Missing resources found in yaml. Please ensure the "
                    "following are either available in your YAML or created"
                    " on the server. {}".format(
                        set(missing_resources)), fg=Colors.RED)

                raise SystemExit(1)

    # Manifest Operations via base.py
    def _apply_manifest(self, obj_key, *args, **kwargs):
        obj = self.objects[obj_key]
        cls = ResolverCache.get_model(obj)
        ist = cls.from_dict(self.client, obj)
        setattr(ist, 'rc', ResolverCache(self.client))
        ist.apply(self.client, *args, **kwargs)

    def _delete_manifest(self, obj_key, *args, **kwargs):
        obj = self.objects[obj_key]
        cls = ResolverCache.get_model(obj)
        ist = cls.from_dict(self.client, obj)
        setattr(ist, 'rc', ResolverCache(self.client))
        ist.delete(self.client, obj, *args, **kwargs)

    # File Loading Operations

    def _process_file_list(self, files):
        for f in files:
            data = self._load_file_content(f)
            if data:
                for obj in data:
                    self._register_object(obj)

            self.files[f] = data

    def _register_object(self, data):
        try:
            key = self._get_object_key(data)
            self.objects[key] = data
            self.resolved_objects[key] = {'src': 'local', 'manifest': data}
        except KeyError:
            click.secho("Key error {}".format(data), fg=Colors.RED)
            return

    def _load_file_content(self, file_name, is_value=False, is_secret=False):
        if not is_secret:
            with open(file_name) as opened:
                data = opened.read()
        else:
            data = run_bash('sops -d {}'.format(file_name))

        # TODO: If no Kind in yaml/json, then skip
        if not (is_value or is_secret):
            if self.environment or file_name.endswith('.j2'):
                template = self.environment.from_string(data)
                template_args = self.values
                if self.secrets:
                    template_args['secrets'] = self.secrets
                try:
                    data = template.render(**template_args)
                except Exception as ex:
                    click.secho('{} yaml parsing error. Msg: {}'.format(
                        file_name, str(ex)))
                    raise ex

                file_name = file_name.rstrip('.j2')

        loaded_data = []
        if file_name.endswith('json'):
            # FIXME: Handle for JSON List.
            try:
                loaded = json.loads(data)
                loaded_data.append(loaded)
            except json.JSONDecodeError as ex:
                ex_message = '{} yaml parsing error. Msg: {}'.format(
                    file_name, str(ex))
                raise Exception(ex_message)

        elif file_name.endswith('yaml') or file_name.endswith('yml'):
            try:
                loaded = yaml.safe_load_all(data)
                loaded_data = list(loaded)

            except yaml.YAMLError as e:
                ex_message = '{} yaml parsing error. Msg: {}'.format(
                    file_name, str(e))
                raise Exception(ex_message)

        if not loaded_data:
            click.secho('{} file is empty'.format(file_name))

        return loaded_data

    # Graph Operations

    def _add_graph_node(self, key):
        self.graph.add(key)
        self.diagram.append('\t{}[{}]'.format(mermaid_safe(key), key))

    def _add_graph_edge(self, dependent_key, key):
        self.graph.add(dependent_key, key)
        self.diagram.append('\t{}[{}] --> {}[{}] '.format(mermaid_safe(key),
                                                          key, mermaid_safe(
                dependent_key), dependent_key))

    # Dependency Resolution
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
                if guid and obj_guid == guid:
                    self._add_remote_object_to_resolve_tree(
                        dependent_key, obj_guid, dependency, obj)

                if (name_or_guid == obj_name) and (
                        'version' in dependency and obj[
                    'packageVersion'] == dependency.get('version')):
                    self._add_remote_object_to_resolve_tree(
                        dependent_key, obj_guid, dependency, obj)

            # Special handling for Static route since it doesn't have a name field.
            # StaticRoute sends a URLPrefix field with name being the prefix along with short org guid.
            elif kind == 'staticroute' and name_or_guid in obj_name:
                self._add_remote_object_to_resolve_tree(
                    dependent_key, obj_guid, dependency, obj)

            elif (guid and obj_guid == guid) or (name_or_guid == obj_name):
                self._add_remote_object_to_resolve_tree(
                    dependent_key, obj_guid, dependency, obj)

        self.dependencies[kind][name_or_guid] = {'local': True}
        self._add_graph_edge(dependent_key, key)

        if key not in self.resolved_objects:
            self.resolved_objects[key] = {'src': 'missing'}

    def _add_remote_object_to_resolve_tree(self, dependent_key, guid,
                                           dependency, obj):
        kind = dependency.get('kind')
        name_or_guid = dependency.get('nameOrGUID')
        key = '{}:{}'.format(kind, name_or_guid)
        self.dependencies[kind][name_or_guid] = {
            'guid': guid, 'raw': obj, 'local': False}
        if key not in self.resolved_objects:
            self.resolved_objects[key] = {}
        self.resolved_objects[key]['guid'] = guid
        self.resolved_objects[key]['raw'] = obj
        self.resolved_objects[key]['src'] = 'remote'

        self._add_graph_edge(dependent_key, key)

        dependency['guid'] = guid
        if kind.lower() == "disk":
            dependency['depGuid'] = obj['internalDeploymentGUID']

        if kind.lower() == "deployment":
            dependency['guid'] = obj['deploymentId']

    def _initialize_kind_dependency(self, kind):
        if not self.dependencies.get(kind):
            self.dependencies[kind] = {}

    def show_dependency_graph(self):
        """Lauches mermaid.live dependency graph"""
        link = mermaid_link("\n".join(self.diagram))
        click.launch(link)

    # Utils
    def _display_context(
            self,
            total_time: int,
            total_objects: int,
            resource_list: typing.List
    ) -> None:
        headers = [
            click.style('Resource Context', bold=True, fg=Colors.YELLOW)]
        context = [
            ['Expected Time (mins)', round(total_time, 2)],
            ['Files', len(self.files)],
            ['Resources', total_objects],
        ]
        click.echo(tabulate(context, headers=headers,
                            tablefmt='simple', numalign='center'))

        # Display Resource Inventory
        headers = []
        for header in ['Resource', 'Action', 'Expected Time (mins)']:
            headers.append(click.style(header, fg=Colors.YELLOW, bold=True))

        print_separator()
        click.echo(tabulate(resource_list, headers=headers,
                            tablefmt='simple', numalign='center'))
        print_separator()

    @staticmethod
    def _get_attr(obj, accept_keys):
        metadata = None

        if hasattr(obj, 'metadata'):
            metadata = getattr(obj, 'metadata')

        for key in accept_keys:
            if hasattr(obj, key):
                return getattr(obj, key)
            if metadata is not None and hasattr(metadata, key):
                return getattr(metadata, key)

        raise Exception('guid resolve failed')

    @staticmethod
    def _get_object_key(obj: dict) -> str:
        kind = obj.get('kind').lower()
        name_or_guid = obj['metadata']['name']

        return '{}:{}'.format(kind, name_or_guid)

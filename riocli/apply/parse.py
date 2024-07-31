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
import json
import queue
import threading
import typing
from graphlib import TopologicalSorter

import click
import jinja2
import yaml
from munch import munchify

from riocli.apply.util import get_model, print_resolved_objects, message_with_prompt
from riocli.constants import Colors, Symbols
from riocli.utils import dump_all_yaml, run_bash, print_centered_text
from riocli.utils.graph import Graphviz
from riocli.utils.spinner import with_spinner

DELETE_POLICY_LABEL = 'rapyuta.io/deletionPolicy'


class Applier(object):
    DEFAULT_MAX_WORKERS = 6

    def __init__(self, files: typing.List, values, secrets):
        self.environment = None
        self.input_file_paths = files
        self.objects = {}
        self.resolved_objects = {}
        self.files = {}
        self.graph = TopologicalSorter()
        self.secrets = {}
        self.values = {}
        self.diagram = Graphviz(direction='LR', format='svg')
        if values or secrets:
            self.environment = jinja2.Environment()

        if values:
            self.values = self._load_file_content(
                values, is_value=True, is_secret=False)[0]

        if secrets:
            self.secrets = self._load_file_content(
                secrets, is_value=True, is_secret=True)[0]

        self._process_file_list(files)

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
                if o in self.resolved_objects and 'manifest' in self.resolved_objects[o]:
                    try:
                        self._apply_manifest(o, *args, **kwargs)
                    except Exception as ex:
                        done_queue.put(ex)
                        continue

                task_queue.task_done()
                done_queue.put(o)

        # Start the workers that will accept tasks from the task_queue
        # and process them. Upon completion, they will put the object
        # in the done_queue.
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

        # Block until the task_queue is empty.
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
        """Validates and prints the resolved manifests"""
        manifests = []
        for _, o in self.objects.items():
            kls = get_model(o)
            kls.validate(o)
            manifests.append(o)

        dump_all_yaml(manifests)

    def parse_dependencies(self):
        for _, data in self.files.items():
            for model in data:
                key = self._get_object_key(model)
                self._parse_dependency(key, model)
                self._add_graph_node(key)

        print_centered_text("Parsed Resources")
        print_resolved_objects(self.resolved_objects)

    def show_dependency_graph(self):
        """Lauches mermaid.live dependency graph"""
        self.diagram.visualize()

    def _apply_manifest(self, obj_key: str, *args, **kwargs) -> None:
        """Instantiate and apply the object manifest"""
        spinner = kwargs.get('spinner')
        dryrun = kwargs.get("dryrun", False)

        obj = self.objects[obj_key]
        kls = get_model(obj)
        kls.validate(obj)
        ist = kls(munchify(obj))

        message_with_prompt("{} Applying {}...".format(
            Symbols.WAITING, obj_key), fg=Colors.CYAN, spinner=spinner)

        try:
            if not dryrun:
                ist.apply(*args, **kwargs)
        except Exception as ex:
            message_with_prompt("{} Failed to apply {}. Error: {}".format(
                Symbols.ERROR, obj_key, str(ex)), fg=Colors.RED, spinner=spinner)
            raise ex

        message_with_prompt("{} Applied {}".format(
            Symbols.SUCCESS, obj_key), fg=Colors.GREEN, spinner=spinner)

    def _delete_manifest(self, obj_key: str, *args, **kwargs) -> None:
        """Instantiate and delete the object manifest"""
        spinner = kwargs.get('spinner')
        dryrun = kwargs.get("dryrun", False)

        obj = self.objects[obj_key]
        kls = get_model(obj)
        kls.validate(obj)
        ist = kls(munchify(obj))

        message_with_prompt("{} Deleting {}...".format(
            Symbols.WAITING, obj_key), fg=Colors.CYAN, spinner=spinner)

        # If a resource has a label with DELETE_POLICY_LABEL set
        # to 'retain', it should not be deleted.
        labels = obj.get('metadata', {}).get('labels', {})
        can_delete = labels.get(DELETE_POLICY_LABEL) != 'retain'

        try:
            if not dryrun and can_delete:
                ist.delete(*args, **kwargs)
        except Exception as ex:
            message_with_prompt("{} Failed to delete {}. Error: {}".format(
                Symbols.ERROR, obj_key, str(ex)), fg=Colors.RED, spinner=spinner)
            raise ex

        message_with_prompt("{} Deleted {}.".format(
            Symbols.SUCCESS, obj_key), fg=Colors.GREEN, spinner=spinner)

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
        """Load the file content and return the parsed data.

        When the file is a template, render it using values or secrets.
        """
        try:
            if is_secret:
                data = run_bash(f'sops -d {file_name}')
            else:
                with open(file_name) as f:
                    data = f.read()
        except Exception as e:
            raise Exception(f'Error loading file {file_name}: {str(e)}')

        # When the file is a template, render it using
        # values or secrets.
        if not (is_value or is_secret):
            if self.environment or file_name.endswith('.j2'):
                try:
                    template = self.environment.from_string(data)
                except Exception as e:
                    raise Exception(f'Error loading template {file_name}: {str(e)}')

                template_args = self.values

                if self.secrets:
                    template_args['secrets'] = self.secrets

                try:
                    data = template.render(**template_args)
                except Exception as ex:
                    raise Exception(f'Failed to parse {file_name}: {str(ex)}')

                file_name = file_name.rstrip('.j2')

        loaded_data = []
        if file_name.endswith('json'):
            # FIXME: Handle for JSON List.
            try:
                loaded = json.loads(data)
                loaded_data.append(loaded)
            except json.JSONDecodeError as ex:
                raise Exception(f'Failed to parse {file_name}: {str(ex)}')
        elif file_name.endswith('yaml') or file_name.endswith('yml'):
            try:
                loaded = yaml.safe_load_all(data)
                loaded_data = list(loaded)
            except yaml.YAMLError as e:
                raise Exception(f'Failed to parse {file_name}: {str(e)}')

        if not loaded_data:
            click.secho('{} file is empty'.format(file_name))

        return loaded_data

    # Graph Operations

    def _add_graph_node(self, key):
        self.graph.add(key)
        self.diagram.node(key)

    def _add_graph_edge(self, dependent_key, key):
        self.graph.add(dependent_key, key)
        self.diagram.edge(key, dependent_key)

    # Dependency Resolution
    def _parse_dependency(self, dependent_key, model):
        # TODO(pallab): let resources determine their own dependencies and return them
        # kls = get_model(model)
        # for dependency in kls.parse_dependencies(model):
        #     self._resolve_dependency(dependent_key, dependency)

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

        self._add_graph_edge(dependent_key, key)

    @staticmethod
    def _get_object_key(obj: dict) -> str:
        kind = obj.get('kind').lower()
        name_or_guid = obj.get('metadata', {}).get('name')

        if not name_or_guid:
            raise ValueError('[kind:{}] name is required.'.format(kind))

        return '{}:{}'.format(kind, name_or_guid)

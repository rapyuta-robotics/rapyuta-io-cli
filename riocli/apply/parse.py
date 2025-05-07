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
import json
import queue
import threading
import typing

import click
import yaml
from benedict import benedict
from graphlib import TopologicalSorter
from munch import munchify

from riocli.apply.util import (
    get_model,
    init_jinja_environment,
    message_with_prompt,
    print_resolved_objects,
)
from riocli.config import Configuration
from riocli.constants import Colors, Symbols, ApplyResult
from riocli.exceptions import (
    NoProjectSelected,
    NoOrganizationSelected,
    ResourceNotFound,
    LoggedOut,
)
from riocli.utils import dump_all_yaml, print_centered_text, run_bash
from riocli.utils.graph import Graphviz
from riocli.utils.spinner import with_spinner


class Applier(object):
    DEFAULT_MAX_WORKERS = 6
    DELETE_POLICY_LABEL = "rapyuta.io/deletionPolicy"

    def __init__(
        self,
        files: typing.List,
        values: typing.List,
        secrets: typing.List,
        config: Configuration,
    ):
        self.files = {}
        self.objects = {}
        self.resolved_objects = {}
        self.input_file_paths = files
        self.config = config
        self.graph = TopologicalSorter()
        self.environment = init_jinja_environment()
        self.diagram = Graphviz(direction="LR", format="svg")
        self._process_values_and_secrets(values, secrets)
        self._process_file_list(files)

    def print_resolved_manifests(self):
        """Validates and prints the resolved manifests"""
        manifests = []
        for _, o in self.objects.items():
            kls = get_model(o)
            kls.validate(o)
            manifests.append(o)

        dump_all_yaml(manifests)

    @with_spinner(text="Applying...", timer=True)
    def apply(self, *args, **kwargs):
        """Apply the resources defined in the manifest files"""
        spinner = kwargs.get("spinner")
        kwargs["workers"] = int(kwargs.get("workers") or self.DEFAULT_MAX_WORKERS)

        apply_func = self.apply_async
        if kwargs["workers"] == 1:
            apply_func = self.apply_sync

        try:
            apply_func(*args, **kwargs)
            spinner.text = click.style("Apply successful.", fg=Colors.BRIGHT_GREEN)
            spinner.green.ok(Symbols.SUCCESS)
        except Exception as e:
            spinner.text = click.style(
                "Apply failed. Error: {}".format(e), fg=Colors.BRIGHT_RED
            )
            spinner.red.fail(Symbols.ERROR)
            raise SystemExit(1) from e

    def apply_sync(self, *args, **kwargs):
        self.graph.prepare()
        while self.graph.is_active():
            for obj in self.graph.get_ready():
                if (
                    obj in self.resolved_objects
                    and "manifest" in self.resolved_objects[obj]
                ):
                    self._apply_manifest(obj, *args, **kwargs)
                self.graph.done(obj)

    def apply_async(self, *args, **kwargs):
        task_queue = queue.Queue()
        done_queue = queue.Queue()

        self._start_apply_workers(
            self._apply_manifest, task_queue, done_queue, *args, **kwargs
        )

        self.graph.prepare()
        while self.graph.is_active():
            for obj in self.graph.get_ready():
                task_queue.put(obj)

            done_obj = done_queue.get()
            if isinstance(done_obj, Exception):
                raise Exception(done_obj)

            self.graph.done(done_obj)

        # Block until the task_queue is empty.
        task_queue.join()

    @with_spinner(text="Deleting...", timer=True)
    def delete(self, *args, **kwargs):
        """Delete resources defined in manifests."""
        spinner = kwargs.get("spinner")
        kwargs["workers"] = int(kwargs.get("workers") or self.DEFAULT_MAX_WORKERS)

        delete_func = self.delete_async
        if kwargs["workers"] == 1:
            delete_func = self.delete_sync

        try:
            delete_func(*args, **kwargs)
            spinner.text = click.style("Delete successful.", fg=Colors.BRIGHT_GREEN)
            spinner.green.ok(Symbols.SUCCESS)
        except Exception as e:
            spinner.text = click.style(
                "Delete failed. Error: {}".format(e), fg=Colors.BRIGHT_RED
            )
            spinner.red.fail(Symbols.ERROR)
            raise SystemExit(1) from e

    def delete_sync(self, *args, **kwargs) -> None:
        delete_order = list(self.graph.static_order())
        delete_order.reverse()
        for o in delete_order:
            if o in self.resolved_objects and "manifest" in self.resolved_objects[o]:
                self._delete_manifest(o, *args, **kwargs)

    def delete_async(self, *args, **kwargs) -> None:
        task_queue = queue.Queue()
        done_queue = queue.Queue()

        self._start_apply_workers(
            self._delete_manifest, task_queue, done_queue, *args, **kwargs
        )

        for nodes in self._get_async_delete_order():
            for node in nodes:
                task_queue.put(node)

            done_obj = done_queue.get()
            if isinstance(done_obj, Exception):
                raise Exception(done_obj)

            task_queue.join()

    def _start_apply_workers(
        self,
        func: typing.Callable,
        tasks: queue.Queue,
        done: queue.Queue,
        *args,
        **kwargs,
    ) -> None:
        """A helper method to start workers for apply/delete operations

        The `func` should have the following signature:
            func(obj_key: str, *args, **kwargs) -> None

        The `tasks` queue is used to pass objects to the workers for processing.
        The `done` queue is used to pass the processed objects back to the main.
        """

        def _worker():
            while True:
                o = tasks.get()
                if o in self.resolved_objects and "manifest" in self.resolved_objects[o]:
                    try:
                        func(o, *args, **kwargs)
                    except Exception as ex:
                        tasks.task_done()
                        done.put(ex)
                        continue

                tasks.task_done()
                done.put(o)

        # Start the workers that will accept tasks from the task_queue
        # and process them. Upon completion, they will put the object
        # in the done_queue. The main thread will wait for the task_queue
        # to be empty before exiting. The daemon threads will die with the
        # main process.
        n = int(kwargs.get("workers") or self.DEFAULT_MAX_WORKERS)
        for i in range(n):
            threading.Thread(target=_worker, daemon=True, name=f"worker-{i}").start()

    def _get_async_delete_order(self):
        """Returns the delete order for async delete operation

        This method returns the delete order in a way that the
        resources that are dependent on other resources are deleted
        first while also ensuring that they can be processed concurrently.
        """
        stack = []
        self.graph.prepare()
        while self.graph.is_active():
            nodes = self.graph.get_ready()
            stack.append(nodes)
            self.graph.done(*nodes)

        while stack:
            yield stack.pop()

    def parse_dependencies(self, print_resources: bool = True):
        for _, data in self.files.items():
            for model in data:
                key = self._get_object_key(model)
                self._parse_dependency(key, model)
                self._add_graph_node(key)

        if print_resources:
            print_centered_text("Parsed Resources")
            print_resolved_objects(self.resolved_objects)

    def show_dependency_graph(self):
        """Lauches mermaid.live dependency graph"""
        self.diagram.visualize()

    def _apply_manifest(self, obj_key: str, *args, **kwargs) -> None:
        """Instantiate and apply the object manifest"""
        spinner = kwargs.get("spinner")
        dryrun = kwargs.get("dryrun", False)

        obj = self.objects[obj_key]
        kls = get_model(obj)

        try:
            kls.validate(obj)
        except Exception as ex:
            raise Exception(f"invalid manifest {obj_key}: {str(ex)}")

        ist = kls(munchify(obj))

        obj_key = click.style(obj_key, bold=True)

        message_with_prompt(
            "{} Applying {}...".format(Symbols.WAITING, obj_key),
            fg=Colors.CYAN,
            spinner=spinner,
        )

        try:
            result = ApplyResult.CREATED
            if not dryrun:
                result = ist.apply(*args, **kwargs)

            if result == ApplyResult.EXISTS:
                message_with_prompt(
                    "{} {} already exists".format(Symbols.INFO, obj_key),
                    fg=Colors.WHITE,
                    spinner=spinner,
                )
                return

            message_with_prompt(
                "{} {} {}".format(Symbols.SUCCESS, result, obj_key),
                fg=Colors.GREEN,
                spinner=spinner,
            )
        except Exception as ex:
            message_with_prompt(
                "{} Failed to apply {}. Error: {}".format(
                    Symbols.ERROR, obj_key, str(ex)
                ),
                fg=Colors.RED,
                spinner=spinner,
            )
            raise Exception(f"{obj_key}: {str(ex)}")

    def _delete_manifest(self, obj_key: str, *args, **kwargs) -> None:
        """Instantiate and delete the object manifest"""
        spinner = kwargs.get("spinner")
        dryrun = kwargs.get("dryrun", False)

        obj = self.objects[obj_key]
        kls = get_model(obj)

        try:
            kls.validate(obj)
        except Exception as ex:
            raise Exception(f"invalid manifest {obj_key}: {str(ex)}")

        ist = kls(munchify(obj))

        obj_key = click.style(obj_key, bold=True)

        message_with_prompt(
            "{} Deleting {}...".format(Symbols.WAITING, obj_key),
            fg=Colors.CYAN,
            spinner=spinner,
        )

        # If a resource has a label with DELETE_POLICY_LABEL set
        # to 'retain', it should not be deleted.
        labels = obj.get("metadata", {}).get("labels", {})
        can_delete = labels.get(self.DELETE_POLICY_LABEL) != "retain"

        if not can_delete:
            message_with_prompt(
                "{} {} cannot be deleted since deletion policy is set to 'retain'".format(
                    Symbols.INFO, obj_key
                ),
                fg=Colors.WHITE,
                spinner=spinner,
            )
            return

        try:
            if not dryrun and can_delete:
                ist.delete(*args, **kwargs)

            message_with_prompt(
                "{} Deleted {}".format(Symbols.SUCCESS, obj_key),
                fg=Colors.GREEN,
                spinner=spinner,
            )
        except ResourceNotFound:
            message_with_prompt(
                "{} {} not found".format(Symbols.WARNING, obj_key),
                fg=Colors.YELLOW,
                spinner=spinner,
            )
            return
        except Exception as ex:
            message_with_prompt(
                "{} Failed to delete {}. Error: {}".format(
                    Symbols.ERROR, obj_key, str(ex)
                ),
                fg=Colors.RED,
                spinner=spinner,
            )
            raise Exception(f"{obj_key}: {str(ex)}")

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
            self.resolved_objects[key] = {"src": "local", "manifest": data}
        except KeyError:
            click.secho("Key error {}".format(data), fg=Colors.RED)
            return

    def _load_file_content(self, file_name, is_value=False, is_secret=False):
        """Load the file content and return the parsed data.

        When the file is a template, render it using values or secrets.
        """
        try:
            if is_secret:
                data = run_bash(f"sops -d {file_name}")
            else:
                with open(file_name) as f:
                    data = f.read()
        except Exception as e:
            raise Exception(f"Error loading file {file_name}: {str(e)}")

        # When the file is a template, render it using
        # values or secrets.
        if not (is_value or is_secret):
            if self.environment or file_name.endswith(".j2"):
                try:
                    template = self.environment.from_string(data)
                except Exception as e:
                    raise Exception(f"Error loading template {file_name}: {str(e)}")

                template_args = self.values

                if self.secrets:
                    template_args["secrets"] = self.secrets

                try:
                    data = template.render(**template_args)
                except Exception as ex:
                    raise Exception(f"Failed to parse {file_name}: {str(ex)}")

                file_name = file_name.rstrip(".j2")

        loaded_data = []
        if file_name.endswith("json"):
            # FIXME: Handle for JSON List.
            try:
                loaded = json.loads(data)
                loaded_data.append(loaded)
            except json.JSONDecodeError as ex:
                raise Exception(f"Failed to parse {file_name}: {str(ex)}")
        elif file_name.endswith("yaml") or file_name.endswith("yml"):
            try:
                loaded = yaml.safe_load_all(data)
                loaded_data = list(loaded)
            except yaml.YAMLError as e:
                raise Exception(f"Failed to parse {file_name}: {str(e)}")

        if not loaded_data:
            click.secho("{} file is empty".format(file_name))

        return loaded_data

    def _add_graph_node(self, key):
        self.graph.add(key)
        self.diagram.node(key)

    def _add_graph_edge(self, dependent_key, key):
        self.graph.add(dependent_key, key)
        self.diagram.edge(key, dependent_key)

    def _parse_dependency(self, dependent_key, model):
        # TODO(pallab): let resources determine their own dependencies and return them
        # kls = get_model(model)
        # for dependency in kls.parse_dependencies(model):
        #     self._resolve_dependency(dependent_key, dependency)

        for key, value in model.items():
            if key == "depends":
                if "kind" in value and value.get("kind"):
                    self._resolve_dependency(dependent_key, value)
                if isinstance(value, list):
                    for each in value:
                        if isinstance(each, dict) and each.get("kind"):
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
        kind = dependency.get("kind")
        name_or_guid = dependency.get("nameOrGUID")
        key = "{}:{}".format(kind, name_or_guid)

        self._add_graph_edge(dependent_key, key)

    @staticmethod
    def _get_object_key(obj: dict) -> str:
        kind = obj.get("kind").lower()
        name_or_guid = obj.get("metadata", {}).get("name")

        if not name_or_guid:
            raise ValueError("[kind:{}] name is required.".format(kind))

        return "{}:{}".format(kind, name_or_guid)

    def _inject_rio_namespace(self, values: typing.Optional[dict] = None) -> dict:
        values = values or {}

        try:
            rio = {
                "project": {
                    "name": self.config.data.get("project_name"),
                    "guid": self.config.project_guid,
                },
                "organization": {
                    "name": self.config.data.get("organization_name"),
                    "guid": self.config.organization_guid,
                    "short_id": self.config.organization_short_id,
                },
                "email_id": self.config.data.get("email_id"),
            }
        except (LoggedOut, NoProjectSelected, NoOrganizationSelected):
            rio = {
                "project": {
                    "name": "project-name",
                    "guid": "project-guid",
                },
                "organization": {
                    "name": "org-name",
                    "guid": "org-guid",
                    "short_id": "org-short",
                },
                "email_id": "user@rapyuta.io",
            }

        if "rio" in values:
            benedict(values["rio"]).merge(rio)
        else:
            values["rio"] = rio

        return values

    def _process_values_and_secrets(
        self, values: typing.List, secrets: typing.List
    ) -> None:
        """Process the values and secrets files and inject them into the manifest files"""
        self.values, self.secrets = benedict({}), benedict({})

        values = values or []
        secrets = secrets or []

        for v in values:
            benedict(self.values).merge(self._load_file_content(v, is_value=True)[0])

        self.values = self._inject_rio_namespace(self.values)

        for s in secrets:
            benedict(self.secrets).merge(self._load_file_content(s, is_secret=True)[0])

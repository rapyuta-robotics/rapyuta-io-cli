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
from __future__ import annotations

import graphlib
import json
from concurrent.futures import ThreadPoolExecutor
from functools import partial
from pathlib import Path
from typing import TYPE_CHECKING, Any

import click
import yaml
from benedict import benedict
from munch import munchify

from riocli.apply.util import (
    get_resource_class,
    init_jinja_environment,
    message_with_prompt,
    print_objects_table,
)
from riocli.constants import ApplyResult, Colors, Symbols
from riocli.exceptions import (
    LoggedOut,
    NoOrganizationSelected,
    NoProjectSelected,
    ResourceNotFound,
)
from riocli.model.base import Model
from riocli.utils import dump_all_yaml, print_centered_text, run_bash
from riocli.utils.graph import GraphVisualizer, Graphviz
from riocli.utils.spinner import with_spinner

if TYPE_CHECKING:
    from collections.abc import Callable, Iterable, Mapping

    from rapyuta_io import Client
    from rapyuta_io_sdk_v2 import Client as v2Client
    from yaspin.api import Yaspin

    from riocli.config import Configuration

DEFAULT_MAX_WORKERS = 6
DELETE_POLICY_LABEL = "rapyuta.io/deletionPolicy"


class Applier:
    def __init__(
        self,
        files: Iterable[str],
        values: Iterable[str],
        secrets: Iterable[str],
        config: Configuration,
    ):
        self.input_file_paths = files
        self.config = config
        self.environment = init_jinja_environment()
        self.values = self._load_values_and_secrets(values, secrets)
        self.objects, self.manifests = self._load_objects(files)
        self.dependency_graph, self.diagram = self._get_dependency_graph(self.objects)

    def print_summary(self) -> None:
        """Prints a summary table with Resource list for the operation."""
        print_centered_text("Parsed Resources")
        print_objects_table(self.objects.keys())

    def print_manifests(self):
        """Validates and prints the resolved manifests"""
        dump_all_yaml(self.manifests)

    def show_dependency_graph(self, print_only: bool):
        """Shows a GraphViz dependency graph of the objects."""
        self.diagram.visualize(print_only=print_only)

    @with_spinner(text="Applying...", timer=True)
    def apply(
        self,
        dryrun: bool,
        retry_count: int,
        retry_interval: int,
        workers: int = DEFAULT_MAX_WORKERS,
        spinner: Yaspin | None = None,
    ):
        """Apply the resources defined in the manifest files"""
        assert spinner is not None

        if dryrun:
            client = None
            v2_client = None
        else:
            client = self.config.new_client()
            v2_client = self.config.new_v2_client()

        apply_func = partial(
            self._apply_manifest,
            client=client,
            v2_client=v2_client,
            dryrun=dryrun,
            retry_count=retry_count,
            retry_interval=retry_interval,
            spinner=spinner,
        )

        try:
            self._start_work(op=apply_func, work=self._get_apply_order(), workers=workers)
            spinner.text = click.style("Apply successful.", fg=Colors.BRIGHT_GREEN)
            spinner.green.ok(Symbols.SUCCESS)
        except Exception as e:
            spinner.text = click.style(f"Apply failed. Error: {e}", fg=Colors.BRIGHT_RED)
            spinner.red.fail(Symbols.ERROR)
            raise SystemExit(1) from e

    @with_spinner(text="Deleting...", timer=True)
    def delete(
        self,
        dryrun: bool,
        retry_count: int,
        retry_interval: int,
        workers: int = DEFAULT_MAX_WORKERS,
        spinner: Yaspin | None = None,
    ):
        """Delete resources defined in manifests."""
        assert spinner is not None

        if dryrun:
            client = None
            v2_client = None
        else:
            client = self.config.new_client()
            v2_client = self.config.new_v2_client()

        delete_func = partial(
            self._delete_manifest,
            client=client,
            v2_client=v2_client,
            dryrun=dryrun,
            retry_count=retry_count,
            retry_interval=retry_interval,
            spinner=spinner,
        )

        try:
            self._start_work(
                op=delete_func, work=self._get_delete_order(), workers=workers
            )
            spinner.text = click.style("Delete successful.", fg=Colors.BRIGHT_GREEN)
            spinner.green.ok(Symbols.SUCCESS)
        except Exception as e:
            spinner.text = click.style(f"Delete failed. Error: {e}", fg=Colors.BRIGHT_RED)
            spinner.red.fail(Symbols.ERROR)
            raise SystemExit(1) from e

    def _apply_manifest(
        self,
        obj_key: str,
        client: Client | None = None,
        v2_client: v2Client | None = None,
        dryrun: bool = False,
        retry_count: int = 0,
        retry_interval: int = 0,
        spinner: Yaspin | None = None,
    ) -> None:
        """Instantiate and apply the object manifest"""
        assert spinner is not None

        if obj_key not in self.objects:
            return

        obj = self.objects[obj_key]
        obj_key = click.style(obj_key, bold=True)

        message_with_prompt(
            f"{Symbols.WAITING} Applying {obj_key}...",
            fg=Colors.CYAN,
            spinner=spinner,
        )

        try:
            result = ApplyResult.CREATED
            if not dryrun:
                result = obj.apply(
                    client=client,
                    v2_client=v2_client,
                    config=self.config,
                    retry_count=retry_count,
                    retry_interval=retry_interval,
                )

            if result == ApplyResult.EXISTS:
                message_with_prompt(
                    f"{Symbols.INFO} {obj_key} already exists",
                    fg=Colors.WHITE,
                    spinner=spinner,
                )
                return

            message_with_prompt(
                f"{Symbols.SUCCESS} {result} {obj_key}",
                fg=Colors.GREEN,
                spinner=spinner,
            )
        except Exception as ex:
            message_with_prompt(
                f"{Symbols.ERROR} Failed to apply {obj_key}. Error: {str(ex)}",
                fg=Colors.RED,
                spinner=spinner,
            )
            raise Exception(f"{obj_key}: {str(ex)}")

    def _delete_manifest(
        self,
        obj_key: str,
        client: Client | None = None,
        v2_client: v2Client | None = None,
        dryrun: bool = False,
        retry_count: int = 0,
        retry_interval: int = 0,
        spinner: Yaspin | None = None,
    ) -> None:
        """Instantiate and delete the object manifest"""
        assert spinner is not None

        if obj_key not in self.objects:
            return

        obj = self.objects[obj_key]
        obj_key = click.style(obj_key, bold=True)

        message_with_prompt(
            f"{Symbols.WAITING} Deleting {obj_key}...",
            fg=Colors.CYAN,
            spinner=spinner,
        )

        can_delete = self._can_delete(obj)

        if not can_delete:
            message_with_prompt(
                f"{Symbols.INFO} {obj_key} cannot be deleted since deletion policy is set to 'retain'",
                fg=Colors.WHITE,
                spinner=spinner,
            )
            return

        try:
            if not dryrun and can_delete:
                obj.delete(
                    client=client,
                    v2_client=v2_client,
                    config=self.config,
                    retry_count=retry_count,
                    retry_interval=retry_interval,
                )

            message_with_prompt(
                f"{Symbols.SUCCESS} Deleted {obj_key}",
                fg=Colors.GREEN,
                spinner=spinner,
            )
        except ResourceNotFound:
            message_with_prompt(
                f"{Symbols.WARNING} {obj_key} not found",
                fg=Colors.YELLOW,
                spinner=spinner,
            )
            return
        except Exception as ex:
            message_with_prompt(
                f"{Symbols.ERROR} Failed to delete {obj_key}. Error: {str(ex)}",
                fg=Colors.RED,
                spinner=spinner,
            )
            raise Exception(f"{obj_key}: {str(ex)}")

    def _get_dependency_graph(
        self, objects: dict[str, Model]
    ) -> tuple[graphlib.TopologicalSorter[str], GraphVisualizer]:
        graph: graphlib.TopologicalSorter[str] = graphlib.TopologicalSorter()
        diagram = Graphviz(direction="LR", format="svg")

        for key, obj in objects.items():
            dependencies = obj.list_dependencies()

            graph.add(key)
            diagram.node(key)

            if dependencies is not None:
                for d in dependencies:
                    graph.add(key, d)
                    diagram.edge(key, d)

        return graph, diagram

    def _load_objects(self, files) -> tuple[dict[str, Model], list[dict[str, Any]]]:
        loaded_objects: dict[str, Model] = {}
        loaded_manifests: list[dict[str, Any]] = []

        for f in files:
            objects = self._load_manifests(f)
            if objects is not None:
                for obj in objects:
                    if obj is None:
                        continue
                    key, loaded = self._load_object(obj)
                    loaded_objects[key] = loaded
                    loaded_manifests.append(obj)

        return loaded_objects, loaded_manifests

    def _load_object(self, obj: Mapping[str, Any]) -> tuple[str, Model]:
        key = Model.object_key(obj)
        kls = get_resource_class(obj)

        try:
            ist = kls(munchify(obj))
        except Exception as e:
            raise Exception(f"invalid manifest {key}: {str(e)}")

        return key, ist

    def _load_manifests(self, file_name: str) -> list[dict[str, Any]] | None:
        extension = self._get_file_extension(file_name)

        with open(file_name) as f:
            content = f.read()

        return self._parse_content(
            file_name=file_name,
            extension=extension,
            content=content,
            use_values=True,
        )

    def _load_values_and_secrets(
        self, value_files: Iterable[str] | None, secret_files: Iterable[str] | None
    ) -> benedict:
        """
        Process the values and secrets files and inject them into the manifest files.
        """
        values: benedict = benedict({})
        secrets: benedict = benedict({})

        if value_files is not None:
            for v in value_files:
                value = self._load_value(v)
                if value is not None:
                    values.merge(value)

        # The "rio" namespace exposes the commonly used fields from rio's
        # Configuration file.
        rio = self._get_rio_namespace()

        # If "rio" field already exists in the values, then merge otherwise set
        # it.
        if "rio" in values:
            benedict(values["rio"]).merge(rio)
        else:
            values["rio"] = rio

        if secret_files is not None:
            for s in secret_files:
                secret = self._load_secret(s)
                if secret is not None:
                    secrets.merge(secret)

        if "secrets" in values:
            benedict(values["secrets"]).merge(secrets.dict())
        else:
            values["secrets"] = secrets.dict()

        return values

    def _get_rio_namespace(self) -> dict[str, Any]:
        try:
            project_name = self.config.data.get("project_name")
            project_guid = self.config.project_guid
            org_name = self.config.data.get("organization_name")
            org_guid = self.config.organization_guid
            org_short_guid = self.config.organization_short_id
            email_id = self.config.data.get("email_id")

        except (LoggedOut, NoProjectSelected, NoOrganizationSelected):
            project_name = "project-name"
            project_guid = "project-guid"
            org_name = "org-name"
            org_guid = "org-guid"
            org_short_guid = "org-short"
            email_id = "user@rapyuta.io"

        return {
            "project": {
                "name": project_name,
                "guid": project_guid,
            },
            "organization": {
                "name": org_name,
                "guid": org_guid,
                "short_id": org_short_guid,
            },
            "email_id": email_id,
        }

    def _load_secret(self, file_name: str) -> dict[str, Any] | None:
        extension = self._get_file_extension(file_name)

        content = run_bash(f"sops -d {file_name}")

        secrets = self._parse_content(
            file_name=file_name,
            extension=extension,
            content=content,
            use_values=False,
        )

        if secrets is None or len(secrets) == 0:
            return

        return secrets[0]

    def _load_value(self, file_name: str) -> dict[str, Any] | None:
        extension = self._get_file_extension(file_name)

        with open(file_name) as f:
            content = f.read()

        values = self._parse_content(
            file_name=file_name,
            extension=extension,
            content=content,
            use_values=False,
        )

        if values is None or len(values) == 0:
            return

        return values[0]

    def _parse_content(
        self,
        file_name: str,
        extension: str,
        content: str,
        use_values: bool = True,
    ) -> list[dict[str, Any]] | None:
        try:
            content = self._render_template(content=content, use_values=use_values)
        except Exception as e:
            raise Exception(f"Error rendering template {file_name}: {e}")

        loaded = None

        try:
            if extension == ".json":
                # TODO(ankit): Verify how this works.
                # list() -> [] beacause list method make list of keys but [] itself wraps whole object
                loaded = [json.loads(content)]
            elif extension in (".yaml", ".yml"):
                loaded = list(yaml.safe_load_all(content))
        except (json.JSONDecodeError, yaml.YAMLError) as e:
            raise Exception(f"Failed to parse {file_name}: {e}")

        if loaded is None:
            click.secho(f"{file_name} file is empty")

        return loaded

    def _render_template(self, content: str, use_values: bool = False) -> str:
        template = self.environment.from_string(content)

        if use_values:
            return template.render(**self.values)

        return template.render()

    def _get_apply_order(self) -> list[tuple[str, ...]]:
        """
        Generates the order to apply the Graph nodes.
        """
        self.dependency_graph.prepare()

        order: list[tuple[str, ...]] = []

        while self.dependency_graph.is_active():
            nodes = self.dependency_graph.get_ready()
            order.append(nodes)
            self.dependency_graph.done(*nodes)

        return order

    def _get_delete_order(self) -> Iterable[tuple[str, ...]]:
        """
        Generates the order to delete the Graph nodes.
        """
        return reversed(self._get_apply_order())

    @staticmethod
    def _start_work(
        op: Callable[[str], None],
        work: Iterable[tuple[str, ...]],
        workers: int,
    ) -> None:
        """
        Performs the operation asynchronously with workers over the Work.
        """

        def worker_func(w: str) -> Exception | None:
            try:
                op(w)
            except Exception as e:
                return e
            
        max_workers = int(workers) if workers is not None else None

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            for tasks in work:
                futures = executor.map(worker_func, tasks)

                for f in futures:
                    if isinstance(f, Exception):
                        raise f

    @staticmethod
    def _can_delete(obj: Model) -> bool:
        metadata = obj.get("metadata")
        if metadata is None:
            return True

        labels: dict[str, str] = metadata.get("labels")
        if labels is None:
            return True

        policy = labels.get(DELETE_POLICY_LABEL)
        if policy is None:
            return True

        if not isinstance(policy, str):
            return True

        # If a resource has a label with DELETE_POLICY_LABEL set
        # to 'retain', it should not be deleted.
        return policy != "retain"

    @staticmethod
    def _get_file_extension(file_name: str) -> str:
        path = Path(file_name)
        extension = path.suffix.lower()

        # Only YAML and JSON files are supported.
        if extension not in (".json", ".yaml", ".yml"):
            raise Exception(f"Unsupported file extension for {path}")

        return extension

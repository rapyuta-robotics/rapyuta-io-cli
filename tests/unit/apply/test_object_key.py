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
from unittest.mock import MagicMock

import pytest
import yaml
from munch import munchify

from riocli.apply.parse import Applier
from riocli.apply.util import print_objects_table
from riocli.deployment.model import Deployment
from riocli.model.base import Model, package_key

PACKAGE_V1 = {
    "apiVersion": "api.rapyuta.io/v2",
    "kind": "Package",
    "metadata": {"name": "logger", "version": "1.0.0"},
    "spec": {
        "runtime": "cloud",
        "cloud": {"replicas": 1},
        "executables": [
            {"name": "logger", "type": "docker", "docker": {"image": "logger:1"}}
        ],
    },
}

PACKAGE_V2 = {
    **PACKAGE_V1,
    "metadata": {"name": "logger", "version": "2.0.0"},
}

DEPLOYMENT_ON_V1 = {
    "apiVersion": "api.rapyuta.io/v2",
    "kind": "Deployment",
    "metadata": {
        "name": "logger-old",
        "depends": {"kind": "package", "nameOrGUID": "logger", "version": "1.0.0"},
    },
    "spec": {"runtime": "cloud"},
}

DEPLOYMENT_ON_V2 = {
    **DEPLOYMENT_ON_V1,
    "metadata": {
        "name": "logger-new",
        "depends": {"kind": "package", "nameOrGUID": "logger", "version": "2.0.0"},
    },
}


def write_manifest(tmp_path, name: str, objects: list[dict]) -> str:
    path = tmp_path / name
    path.write_text(yaml.safe_dump_all(objects))
    return str(path)


class TestObjectKey:
    def test_package_key_includes_version(self):
        assert Model.object_key(PACKAGE_V1) == "package:logger:1.0.0"

    def test_same_package_name_different_versions_are_distinct(self):
        assert Model.object_key(PACKAGE_V1) != Model.object_key(PACKAGE_V2)

    @pytest.mark.parametrize("version", ["1.0.0", ""])
    def test_node_key_and_edge_key_are_built_the_same_way(self, version):
        """The node and the dependency edge must derive their key identically,
        including for a falsy version. Special-casing one side only is what
        leaves the graph with a predecessor no manifest satisfies, which
        `_apply_manifest` skips silently instead of failing."""
        obj = {"kind": "Package", "metadata": {"name": "logger", "version": version}}
        assert Model.object_key(obj) == package_key("logger", version)

    def test_unversioned_kinds_are_unaffected(self):
        obj = {"kind": "Network", "metadata": {"name": "net", "version": "1.0.0"}}
        assert Model.object_key(obj) == "network:net"

    def test_kind_is_required(self):
        with pytest.raises(ValueError, match="kind is a required field"):
            Model.object_key({"metadata": {"name": "logger"}})

    def test_name_is_required(self):
        with pytest.raises(ValueError, match="is required"):
            Model.object_key({"kind": "Package", "metadata": {"version": "1.0.0"}})


class TestDeploymentPackageDependency:
    def test_package_dependency_edge_is_versioned(self):
        deployment = Deployment(munchify(DEPLOYMENT_ON_V1))
        assert deployment.list_dependencies() == ["package:logger:1.0.0"]

    def test_edge_matches_the_package_object_key(self):
        """The edge and the node must agree, or the graph gains a dangling node
        and the dependency is silently skipped."""
        deployment = Deployment(munchify(DEPLOYMENT_ON_V2))
        dependencies = deployment.list_dependencies() or []
        assert Model.object_key(PACKAGE_V2) in dependencies
        assert Model.object_key(PACKAGE_V1) not in dependencies

    def test_other_dependencies_are_preserved(self):
        obj = {
            **DEPLOYMENT_ON_V1,
            "spec": {
                "runtime": "cloud",
                "staticRoutes": [
                    {
                        "name": "route",
                        "depends": {"kind": "staticroute", "nameOrGUID": "my-route"},
                    }
                ],
            },
        }
        dependencies = Deployment(munchify(obj)).list_dependencies() or []
        assert sorted(dependencies) == [
            "package:logger:1.0.0",
            "staticroute:my-route",
        ]

    def test_deployment_without_package_dependency_returns_none(self):
        obj = {
            "apiVersion": "api.rapyuta.io/v2",
            "kind": "Deployment",
            "metadata": {"name": "standalone"},
            "spec": {"runtime": "cloud"},
        }
        assert Deployment(munchify(obj)).list_dependencies() is None


class TestApplierMultiVersionPackages:
    def test_both_package_versions_are_loaded(self, tmp_path):
        path = write_manifest(
            tmp_path,
            "multiversion.yaml",
            [PACKAGE_V1, PACKAGE_V2, DEPLOYMENT_ON_V1, DEPLOYMENT_ON_V2],
        )
        applier = Applier([path], [], [], MagicMock())

        assert set(applier.objects.keys()) == {
            "package:logger:1.0.0",
            "package:logger:2.0.0",
            "deployment:logger-old",
            "deployment:logger-new",
        }

    def test_each_package_version_is_applied_before_its_deployment(self, tmp_path):
        path = write_manifest(
            tmp_path,
            "multiversion.yaml",
            [PACKAGE_V1, PACKAGE_V2, DEPLOYMENT_ON_V1, DEPLOYMENT_ON_V2],
        )
        applier = Applier([path], [], [], MagicMock())

        order = [key for batch in applier._get_apply_order() for key in batch]
        for package, deployment in (
            ("package:logger:1.0.0", "deployment:logger-old"),
            ("package:logger:2.0.0", "deployment:logger-new"),
        ):
            assert order.index(package) < order.index(deployment)

    def test_duplicate_name_and_version_is_rejected(self, tmp_path):
        path = write_manifest(tmp_path, "duplicate.yaml", [PACKAGE_V1, PACKAGE_V1])

        with pytest.raises(Exception, match="duplicate resource package:logger:1.0.0"):
            Applier([path], [], [], MagicMock())

    def test_duplicates_across_files_are_rejected(self, tmp_path):
        first = write_manifest(tmp_path, "first.yaml", [PACKAGE_V1])
        second = write_manifest(tmp_path, "second.yaml", [PACKAGE_V1])

        with pytest.raises(Exception, match="duplicate resource package:logger:1.0.0"):
            Applier([first, second], [], [], MagicMock())


class TestPrintObjectsTable:
    def test_version_column_shown_for_versioned_objects(self, capsys):
        print_objects_table(["package:logger:1.0.0", "deployment:logger-old"])
        out = capsys.readouterr().out
        assert "Version" in out
        assert "1.0.0" in out

    def test_version_containing_a_colon_is_not_truncated(self, capsys):
        # Nothing constrains the version format, so it may contain a colon.
        # The key is "<kind>:<name>:<version>", so the split must be capped or
        # the version is silently cut at the first colon it contains.
        print_objects_table(["package:logger:2024-01-01T00:00:00Z"])
        assert "2024-01-01T00:00:00Z" in capsys.readouterr().out

    def test_version_column_omitted_when_no_object_is_versioned(self, capsys):
        print_objects_table(["network:net", "secret:cred"])
        out = capsys.readouterr().out
        assert "Version" not in out
        assert "Net" in out

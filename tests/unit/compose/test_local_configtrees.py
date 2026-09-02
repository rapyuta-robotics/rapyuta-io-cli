import click
import pytest

from riocli.compose.local_configtrees import (
    CONFIGTREE_API_SERVICE,
    CONFIGTREE_BOOTSTRAP_SERVICE,
    CONFIGTREE_SYNCER_SERVICE,
    generate_local_configtree_services,
)


class TestGenerateLocalConfigtreeServices:
    def test_raises_when_no_tree_files_found(self, tmp_path):
        with pytest.raises(click.UsageError, match="No ConfigTree YAML files found"):
            generate_local_configtree_services(tmp_path, "http://etcd:2379")

    def test_defaults_tree_files_to_yaml_files_in_dir(self, tmp_path):
        (tmp_path / "common.yaml").write_text("{}")
        (tmp_path / "wms.yml").write_text("{}")
        (tmp_path / "notes.txt").write_text("ignored")

        services = generate_local_configtree_services(tmp_path, "http://etcd:2379")

        env = services[CONFIGTREE_BOOTSTRAP_SERVICE].environment
        assert env["CONFIG_TREE_FILES"] == "common.yaml wms.yml"

    def test_explicit_tree_files_override_glob(self, tmp_path):
        (tmp_path / "a.yaml").write_text("{}")

        services = generate_local_configtree_services(
            tmp_path, "http://etcd:2379", tree_files=("only-this.yaml",)
        )

        env = services[CONFIGTREE_BOOTSTRAP_SERVICE].environment
        assert env["CONFIG_TREE_FILES"] == "only-this.yaml"

    def test_startup_ordering_gates_on_healthy_then_completed(self, tmp_path):
        (tmp_path / "a.yaml").write_text("{}")

        services = generate_local_configtree_services(tmp_path, "http://etcd:2379")

        bootstrap_deps = services[CONFIGTREE_BOOTSTRAP_SERVICE].depends_on
        assert bootstrap_deps[CONFIGTREE_API_SERVICE].condition == "service_healthy"

        syncer_deps = services[CONFIGTREE_SYNCER_SERVICE].depends_on
        assert syncer_deps[CONFIGTREE_API_SERVICE].condition == "service_healthy"
        assert (
            syncer_deps[CONFIGTREE_BOOTSTRAP_SERVICE].condition
            == "service_completed_successfully"
        )

    def test_syncer_uses_given_etcd_endpoint(self, tmp_path):
        (tmp_path / "a.yaml").write_text("{}")

        services = generate_local_configtree_services(tmp_path, "http://my-etcd:2379")

        assert (
            services[CONFIGTREE_SYNCER_SERVICE].environment["ETCD_ENDPOINT"]
            == "http://my-etcd:2379"
        )

    def test_syncer_addresses_api_via_localhost_not_service_name(self, tmp_path):
        # Services share host networking (DEFAULT_NETWORK_MODE) with no compose
        # DNS between them, so peers must be addressed via localhost + port.
        (tmp_path / "a.yaml").write_text("{}")

        services = generate_local_configtree_services(tmp_path, "http://etcd:2379")

        assert (
            services[CONFIGTREE_SYNCER_SERVICE].environment["CONFIG_TREE_API"]
            == "http://localhost:8080"
        )

    def test_bootstrap_mounts_configtree_dir(self, tmp_path):
        (tmp_path / "a.yaml").write_text("{}")

        services = generate_local_configtree_services(tmp_path, "http://etcd:2379")

        volumes = services[CONFIGTREE_BOOTSTRAP_SERVICE].volumes
        assert volumes == [f"{tmp_path.resolve()}:/configtrees"]

    def test_api_service_has_healthcheck_and_tmpfs(self, tmp_path):
        (tmp_path / "a.yaml").write_text("{}")

        services = generate_local_configtree_services(tmp_path, "http://etcd:2379")

        api = services[CONFIGTREE_API_SERVICE]
        assert api.tmpfs == ["/data"]
        assert api.healthcheck.test == "nc -z localhost 8080"

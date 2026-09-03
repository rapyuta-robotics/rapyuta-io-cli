from riocli.compose.local_configtrees import (
    CONFIGTREE_API_SERVICE,
    generate_local_configtree_services,
)


class TestGenerateLocalConfigtreeServices:
    def test_returns_only_the_api_service(self):
        services = generate_local_configtree_services()

        assert list(services.keys()) == [CONFIGTREE_API_SERVICE]

    def test_api_service_has_healthcheck_and_tmpfs(self):
        services = generate_local_configtree_services()

        api = services[CONFIGTREE_API_SERVICE]
        assert api.image == "quay.io/rapyuta/configtrees:latest"
        assert api.tmpfs == ["/data"]
        assert api.healthcheck.test == "nc -z localhost 8080"

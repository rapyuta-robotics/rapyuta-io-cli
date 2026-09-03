from riocli.compose.local_configtrees import (
    CONFIGTREE_API_SERVICE,
    generate_local_configtree_services,
    warn_on_local_configtree_collisions,
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


class TestWarnOnLocalConfigtreeCollisions:
    def test_warns_when_service_name_already_exists(self, capsys):
        local_services = generate_local_configtree_services()
        existing = {CONFIGTREE_API_SERVICE: {"image": "something-else"}}

        warn_on_local_configtree_collisions(existing, local_services)

        output = capsys.readouterr().out
        assert CONFIGTREE_API_SERVICE in output
        assert "overwrites an existing service" in output

    def test_no_warning_when_no_collision(self, capsys):
        local_services = generate_local_configtree_services()

        warn_on_local_configtree_collisions({}, local_services)

        assert capsys.readouterr().out == ""

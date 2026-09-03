"""
Local config-tree API service for ``rio compose generate --local-configtrees``.

Cloud deployments get a config-tree API from the platform natively. A local
``docker compose`` stack has no platform underneath it, so this stands in for it: a
lightweight config-tree API backend, so any repo that wants to seed and sync its own
ConfigTree data locally has something to talk to.
"""

from __future__ import annotations

from riocli.compose.model import HealthCheck, Service

CONFIGTREE_API_IMAGE = "quay.io/rapyuta/configtrees:latest"
CONFIGTREE_API_SERVICE = "v2-apiserver_v2-apiserver"
CONFIGTREE_API_PORT = 8080


def generate_local_configtree_services() -> dict[str, Service]:
    """Builds the config-tree API service for a local stack."""
    api_service = Service(
        container_name=CONFIGTREE_API_SERVICE,
        image=CONFIGTREE_API_IMAGE,
        command=[
            "-database",
            "/data/configtrees.db",
            "-address",
            f":{CONFIGTREE_API_PORT}",
        ],
        tmpfs=["/data"],
        healthcheck=HealthCheck(
            test=f"nc -z localhost {CONFIGTREE_API_PORT}",
            interval="10s",
            timeout="5s",
            retries=5,
            start_period="30s",
        ),
    )

    return {CONFIGTREE_API_SERVICE: api_service}

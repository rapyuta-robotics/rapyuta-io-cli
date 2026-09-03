"""
Local config-tree API service for ``rio compose generate --local-configtrees``.

Cloud deployments get a config-tree API from the platform natively. A local
``docker compose`` stack has no platform underneath it, so this stands in for it: a
lightweight config-tree API backend, so any repo that wants to seed and sync its own
ConfigTree data locally has something to talk to.
"""

from __future__ import annotations

import click

from riocli.compose.model import HealthCheck, Service
from riocli.constants.colors import Colors

CONFIGTREE_API_IMAGE = "quay.io/rapyuta/configtrees:latest"
CONFIGTREE_API_SERVICE = "v2-apiserver_v2-apiserver"
CONFIGTREE_API_PORT = 8080


def warn_on_local_configtree_collisions(
    existing_services: dict, local_services: dict[str, Service]
) -> None:
    """Warns when a --local-configtrees service name collides with an existing one.

    Service names are derived from a manifest's own deployment/exec names, so a
    manifest that happens to declare the same name (e.g. a leftover hand-rolled
    "v2-apiserver" deployment) silently loses its own definition to the merge that
    follows this check -- this at least surfaces it instead of merging silently.
    """
    for name in local_services:
        if name in existing_services:
            click.secho(
                f"Warning: --local-configtrees service '{name}' overwrites an "
                "existing service of the same name.",
                fg=Colors.YELLOW,
            )


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

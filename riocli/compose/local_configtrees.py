"""
Local config-tree API + bootstrap + syncer wiring for ``rio compose generate --local-configtrees``.

Cloud deployments get the config-tree API, its bootstrap, and the ioconfig-syncer wiring
from the platform natively. A local ``docker compose`` stack has no platform underneath
it, so this stands in for it: a lightweight config-tree API backend, a one-shot bootstrap
that seeds it from local ConfigTree YAML files, and ioconfig-syncer to sync the tree into
etcd for consumers that read ConfigTree data from there.
"""

from __future__ import annotations

import shlex
from typing import TYPE_CHECKING

import click

from riocli.compose.model import DependsCondition, HealthCheck, Service

if TYPE_CHECKING:
    from pathlib import Path

CONFIGTREE_API_IMAGE = "quay.io/rapyuta/configtrees:latest"
CONFIGTREE_BOOTSTRAP_IMAGE = "quay.io/rapyuta/v2config_bootstrap:1.0"
CONFIGTREE_SYNCER_IMAGE = "quay.io/rapyuta/ioconfig-syncer:latest"

CONFIGTREE_API_SERVICE = "v2-apiserver"
CONFIGTREE_BOOTSTRAP_SERVICE = "v2configtree-bootstrap"
CONFIGTREE_SYNCER_SERVICE = "ioconfig-syncer"

CONFIGTREE_API_PORT = 8080
CONFIGTREE_MOUNT_PATH = "/configtrees"


def generate_local_configtree_services(
    configtree_dir: Path,
    etcd_endpoint: str,
    tree_files: tuple[str, ...] = (),
) -> dict[str, Service]:
    """
    Builds the config-tree API, bootstrap, and ioconfig-syncer services for a local stack.

    Startup ordering: API healthy -> bootstrap completes -> syncer runs once.

    Args:
        configtree_dir: Local directory of ConfigTree YAML files. Bind-mounted into the
            bootstrap container and loaded into the config-tree API.
        etcd_endpoint: etcd endpoint the syncer writes the synced tree into.
        tree_files: Basenames (under ``configtree_dir``) to bootstrap. Defaults to every
            ``*.yaml``/``*.yml`` file found there.

    Returns:
        Dict of service name -> Service.
    """
    files = tree_files or tuple(sorted(p.name for p in configtree_dir.glob("*.y*ml")))
    if not files:
        raise click.UsageError(f"No ConfigTree YAML files found under {configtree_dir}")

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

    bootstrap_service = Service(
        container_name=CONFIGTREE_BOOTSTRAP_SERVICE,
        image=CONFIGTREE_BOOTSTRAP_IMAGE,
        restart="no",
        volumes=[f"{configtree_dir.resolve()}:{CONFIGTREE_MOUNT_PATH}"],
        environment={"CONFIG_TREE_FILES": " ".join(files)},
        depends_on={
            CONFIGTREE_API_SERVICE: DependsCondition(condition="service_healthy"),
        },
    )

    syncer_service = Service(
        container_name=CONFIGTREE_SYNCER_SERVICE,
        image=CONFIGTREE_SYNCER_IMAGE,
        restart="no",
        command=shlex.split(
            "sync --serialize json --checksum-file /tmp/checksum.db "
            "--sync-file=false --organization-guid dev-org "
            "--project-guid dev-project --token dev-token"
        ),
        environment={
            # Services default to `network_mode: host` (see model.DEFAULT_NETWORK_MODE),
            # sharing the host's network namespace with no compose-DNS between them -- so
            # peers are addressed via localhost + port, not by service name.
            "CONFIG_TREE_API": f"http://localhost:{CONFIGTREE_API_PORT}",
            "RIO_PROJECT_ID": "dev-project",
            "RIO_AuthToken": "dev-token",
            "RIO_ORGANIZATION_ID": "dev-org",
            "CONFIG_TREE_NAMES": "default",
            "ETCD_ENDPOINT": etcd_endpoint,
        },
        depends_on={
            CONFIGTREE_API_SERVICE: DependsCondition(condition="service_healthy"),
            CONFIGTREE_BOOTSTRAP_SERVICE: DependsCondition(
                condition="service_completed_successfully"
            ),
        },
    )

    return {
        CONFIGTREE_API_SERVICE: api_service,
        CONFIGTREE_BOOTSTRAP_SERVICE: bootstrap_service,
        CONFIGTREE_SYNCER_SERVICE: syncer_service,
    }

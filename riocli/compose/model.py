from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal

# Type aliases for better readability
EnvironmentDict = dict[str, str | int | float]
DependsDict = dict[str, "DependsCondition"]
ServiceDict = dict[str, "Service"]

# Constants
DEFAULT_PULL_POLICY = "if_not_present"
DEFAULT_RESTART_POLICY = "always"
DEFAULT_NETWORK_MODE = "host"
DEFAULT_DEPENDS_CONDITION = "service_started"


@dataclass
class DependsCondition:
    """Dependency condition for Docker Compose services."""

    condition: Literal[
        "service_started", "service_healthy", "service_completed_successfully"
    ] = DEFAULT_DEPENDS_CONDITION


@dataclass
class HealthCheck:
    """Health check configuration for Docker Compose services."""

    test: str
    interval: str | None = None
    timeout: str | None = None
    retries: int | None = None


@dataclass
class Service:
    """Docker Compose service configuration."""

    container_name: str
    image: str
    pull_policy: str | None = DEFAULT_PULL_POLICY
    command: str | list[str] | None = None
    hostname: str | None = None
    restart: str | None = DEFAULT_RESTART_POLICY
    ports: list[str] | None = field(default_factory=list)
    volumes: list[str] | None = field(default_factory=list)
    environment: EnvironmentDict | None = field(default_factory=dict)
    depends_on: DependsDict | None = field(default_factory=dict)
    healthcheck: HealthCheck | None = None
    network_mode: str | None = DEFAULT_NETWORK_MODE
    mem_limit: str | None = None
    cpus: str | float | None = None


@dataclass
class DockerCompose:
    """Docker Compose configuration."""

    services: ServiceDict
    version: str | None = None

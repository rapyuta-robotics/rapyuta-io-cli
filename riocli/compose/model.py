from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Literal, Union

# Type aliases for better readability
EnvironmentDict = Dict[str, Union[str, int, float]]
DependsDict = Dict[str, "DependsCondition"]
ServiceDict = Dict[str, "Service"]

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
    interval: Optional[str] = None
    timeout: Optional[str] = None
    retries: Optional[int] = None


@dataclass
class Service:
    """Docker Compose service configuration."""

    container_name: str
    image: str
    pull_policy: Optional[str] = DEFAULT_PULL_POLICY
    command: Optional[Union[str, List[str]]] = None
    hostname: Optional[str] = None
    restart: Optional[str] = DEFAULT_RESTART_POLICY
    ports: Optional[List[str]] = field(default_factory=list)
    volumes: Optional[List[str]] = field(default_factory=list)
    environment: Optional[EnvironmentDict] = field(default_factory=dict)
    depends_on: Optional[DependsDict] = field(default_factory=dict)
    healthcheck: Optional[HealthCheck] = None
    network_mode: Optional[str] = DEFAULT_NETWORK_MODE
    mem_limit: Optional[str] = None
    cpus: Optional[Union[str, float]] = None


@dataclass
class DockerCompose:
    """Docker Compose configuration."""

    services: ServiceDict
    version: Optional[str] = None

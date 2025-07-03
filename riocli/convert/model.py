from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Literal, Union


@dataclass
class BuildConfig:
    """Docker build configuration for a service."""

    context: str
    dockerfile: Optional[str] = None


@dataclass
class DependsCondition:
    """Dependency condition for Docker Compose services."""

    condition: Literal[
        "service_started", "service_healthy", "service_completed_successfully"
    ] = "service_started"


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
    pull_policy: Optional[str] = "if_not_present"
    command: Optional[Union[str, List[str]]] = None
    hostname: Optional[str] = None
    restart: Optional[str] = "always"
    build: Optional[BuildConfig] = None
    ports: Optional[List[str]] = field(default_factory=list)
    volumes: Optional[List[str]] = field(default_factory=list)
    environment: Optional[Dict[str, Union[str, int, float]]] = field(default_factory=dict)
    depends_on: Optional[Dict[str, DependsCondition]] = field(default_factory=dict)
    healthcheck: Optional[HealthCheck] = None
    network_mode: Optional[str] = "host"
    mem_limit: Optional[str] = None
    cpus: Optional[Union[str, float]] = None


@dataclass
class DockerCompose:
    """Docker Compose configuration."""

    version: str
    services: Dict[str, Service]

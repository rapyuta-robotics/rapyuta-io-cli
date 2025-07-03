from dataclasses import dataclass, field
from typing import Dict, List, Optional, Literal


@dataclass
class BuildConfig:
    context: str
    dockerfile: Optional[str] = field(default_factory=str)


@dataclass
class DependsCondition:
    condition: Literal[
        "service_started", "service_healthy", "service_completed_successfully"
    ] = "service_started"


@dataclass
class HealthCheck:
    test: str
    interval: Optional[str] = field(default_factory=str)
    timeout: Optional[str] = field(default_factory=str)
    retries: Optional[int] = field(default_factory=int)


@dataclass
class Service:
    container_name: str
    image: str
    pull_policy: Optional[str] = field(default="if_not_present")
    command: Optional[object] = None
    hostname: Optional[str] = None
    restart: Optional[str] = field(default="always")
    build: Optional[BuildConfig] = None
    ports: Optional[List[str]] = field(default_factory=list)
    volumes: Optional[List[str]] = field(default_factory=list)
    environment: Optional[Dict[str, object]] = field(default_factory=dict)
    depends_on: Optional[Dict[str, DependsCondition]] = field(default_factory=dict)
    healthcheck: Optional[HealthCheck] = None
    network_mode: Optional[str] = field(default="host")
    mem_limit: Optional[str] = None
    cpus: Optional[str] = None


@dataclass
class DockerCompose:
    version: str
    services: Dict[str, Service]

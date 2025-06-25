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
    command: Optional[str] = field(default_factory=str)
    hostname: Optional[str] = field(default_factory=str)
    restart: Optional[str] = field(default_factory=str)
    build: Optional[BuildConfig] = None
    ports: Optional[List[str]] = field(default_factory=list)
    volumes: Optional[List[str]] = field(default_factory=list)
    environment: Optional[Dict[str, str]] = field(default_factory=dict)
    depends_on: Optional[Dict[str, DependsCondition]] = field(default_factory=dict)
    healthcheck: Optional[HealthCheck] = None


@dataclass
class Volume:
    driver: Optional[str] = field(default_factory=str)


@dataclass
class Network:
    driver: Optional[str] = field(default_factory=str)


@dataclass
class DockerCompose:
    version: str
    services: Dict[str, Service]
    volumes: Optional[Dict[str, Volume]] = field(default_factory=dict)
    networks: Optional[Dict[str, Network]] = field(default_factory=dict)

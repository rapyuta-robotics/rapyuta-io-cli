# Copyright 2024 Rapyuta Robotics
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
from __future__ import annotations

import os
import typing
from dataclasses import asdict
from pathlib import Path

import click
import yaml
from click_help_colors import HelpColorsCommand

from riocli.apply.parse import Applier
from riocli.apply.util import process_files_values_secrets
from riocli.config import get_config_from_context
from riocli.constants import Colors
from riocli.convert.model import DockerCompose
from riocli.convert.populate import populate
from riocli.convert.compose import DockerComposeManager

# Constants
DEFAULT_COMPOSE_FILENAME = "docker-compose.yaml"
DEVICE_RUNTIME = "device"


@click.command(
    "convert",
    cls=HelpColorsCommand,
    help_headers_color=Colors.YELLOW,
    help_options_color=Colors.GREEN,
)
@click.option(
    "--name",
    "-n",
    default=DEFAULT_COMPOSE_FILENAME,
    help="Output Docker Compose file name.",
)
@click.option(
    "--values",
    "-v",
    multiple=True,
    default=(),
    help="YAML file(s) with variable values.",
)
@click.option(
    "--secrets",
    "-s",
    multiple=True,
    default=(),
    help="SOPS-encrypted secret file(s).",
)
@click.option(
    "--up",
    "up",
    default=False,
    is_flag=True,
    help="Run 'docker compose up' after generating the file.",
)
@click.option(
    "--down",
    "down",
    default=False,
    is_flag=True,
    help="Run 'docker compose down' for the generated file.",
)
@click.argument("files", nargs=-1)
@click.argument("path", type=click.Path(exists=True))
@click.pass_context
def convert(
    ctx: click.Context,
    name: str,
    values: typing.Tuple[str, ...],
    secrets: typing.Tuple[str, ...],
    up: bool,
    down: bool,
    files: typing.Tuple[str, ...],
    path: str,
) -> None:
    """
    Convert Kubernetes manifests to Docker Compose YAML.

    By default, only generates the compose file. Use --up to start services
    or --down to stop them. Both flags can be combined to restart services.

    Examples:
        rio convert templates/ /output/path
        rio convert templates/ /output/path --up
        rio convert templates/ /output/path --down 
    """
    # Validate input path
    if os.path.isfile(path):
        click.secho("Invalid path: expected a directory.", fg=Colors.RED)
        raise SystemExit(1)

    compose_path = Path(path) / name
    compose_manager = DockerComposeManager(compose_path)

    # Validate Docker availability if up or down operations are requested
    if (up or down) and not compose_manager.validate_docker_availability():
        raise SystemExit(1)

    # Always write output file first (except for down-only when file exists)
    should_write_file = True
    if down and not up and compose_manager.file_exists():
        should_write_file = False

    if should_write_file:
        # Process input files and configurations
        glob_files, abs_values, abs_secrets = process_files_values_secrets(
            files, values, secrets
        )

        # Validate required inputs
        if not path or not glob_files:
            click.secho("No path or files specified.", fg=Colors.RED)
            raise SystemExit(1)

        # Parse and process manifests
        config = get_config_from_context(ctx)
        applier = Applier(glob_files, abs_values, abs_secrets, config)
        deployments, packages = sort_deployment_package(applier)

        docker_compose_manifest = populate(deployments, packages)

        write_compose_yaml(output_path=compose_path, compose_dict=docker_compose_manifest)

    # Handle docker compose down operation (if requested)
    if down:
        if not compose_manager.down():
            click.secho("Docker Compose down operation failed.", fg=Colors.RED)
            raise SystemExit(1)

    # Handle docker compose up operation (if requested)
    if up:
        if not compose_manager.up():
            click.secho("Docker Compose up operation failed.", fg=Colors.RED)
            raise SystemExit(1)


def sort_deployment_package(
    applier: Applier,
) -> typing.Tuple[typing.Dict[str, dict], typing.Dict[str, dict]]:
    """
    Sorts applier objects into deployments and packages for device runtime.

    Args:
        applier: Applier object containing parsed manifests

    Returns:
        Tuple of (deployments, packages) dictionaries
    """
    deployments = {
        k: v
        for k, v in applier.objects.items()
        if (
            v.get("kind") == "Deployment"
            and v.get("spec", {}).get("runtime") == DEVICE_RUNTIME
        )
    }

    packages = {
        k: v
        for k, v in applier.objects.items()
        if (
            v.get("kind") == "Package"
            and v.get("spec", {}).get("runtime") == DEVICE_RUNTIME
        )
    }

    return deployments, packages


def write_compose_yaml(compose_dict: DockerCompose, output_path: str) -> None:
    """
    Writes the given Docker Compose dictionary to a YAML file.

    Args:
        compose_dict: Dictionary representing the Docker Compose configuration.
        dir_path: Directory path where the YAML file will be written.
        file_name: Name of the output YAML file.

    Raises:
        OSError: If the file cannot be written
    """
    # Clean the compose dictionary
    cleaned_compose = clean_dict(asdict(compose_dict))

    try:
        with output_path.open("w", encoding="utf-8") as f:
            yaml.dump(
                cleaned_compose,
                f,
                sort_keys=False,
                default_flow_style=False,
                allow_unicode=True,
            )
        click.secho(f"Docker Compose file written to: {output_path}", fg=Colors.GREEN)
    except OSError as e:
        click.secho(f"Error writing file {output_path}: {e}", fg=Colors.RED)
        raise


def clean_dict(data: typing.Any) -> typing.Any:
    """
    Recursively remove None values, empty lists, and empty dicts from dataclass-to-dict structures.

    Args:
        data: Data structure to clean (dict, list, or primitive type)

    Returns:
        Cleaned data structure with empty/None values removed
    """
    if isinstance(data, dict):
        return {
            k: clean_dict(v)
            for k, v in data.items()
            if v is not None and v != {} and v != []
        }
    elif isinstance(data, list):
        cleaned_list = [
            clean_dict(i) for i in data if i is not None and i != {} and i != []
        ]
        return cleaned_list if cleaned_list else None
    else:
        return data

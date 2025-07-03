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

# Constants
DEFAULT_COMPOSE_FILENAME = "docker-compose.yml"
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
    help="Define file name for docker compose",
)
@click.option(
    "--values",
    "-v",
    multiple=True,
    default=(),
    help="Path to values yaml file. key/values specified in the "
    "values file can be used as variables in template YAMLs",
)
@click.option(
    "--secrets",
    "-s",
    multiple=True,
    default=(),
    help="Secret files are sops encoded value files. riocli "
    "expects sops to be authorized for decoding files on this computer",
)
@click.argument("files", nargs=-1)
@click.argument("path", type=click.Path(exists=True))
@click.pass_context
def convert(
    ctx: click.Context,
    name: str,
    values: typing.Tuple[str, ...],
    secrets: typing.Tuple[str, ...],
    files: typing.Tuple[str, ...],
    path: str,
) -> None:
    """
    Converts Kubernetes manifests into a Docker Compose YAML

    Usage Example:

        rio convert templates/ -v values.yaml path_to_file
    """
    # Validate input path
    if os.path.isfile(path):
        click.secho(
            "Invalid path: expected a directory, but received a file.", fg=Colors.RED
        )
        raise SystemError

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

    # Generate Docker Compose configuration
    docker_compose_manifest = populate(deployments, packages)

    # Write output file
    write_compose_yaml(
        dir_path=path, file_name=name, compose_dict=docker_compose_manifest
    )


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


def write_compose_yaml(
    compose_dict: DockerCompose, dir_path: str, file_name: str
) -> None:
    """
    Writes the given Docker Compose dictionary to a YAML file.

    Args:
        compose_dict: Dictionary representing the Docker Compose configuration.
        dir_path: Directory path where the YAML file will be written.
        file_name: Name of the output YAML file.

    Raises:
        OSError: If the file cannot be written
    """
    # Create absolute path using pathlib for better path handling
    output_path = Path(dir_path) / file_name

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

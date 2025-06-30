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
import typing
import os

import click
import yaml
from click_help_colors import HelpColorsCommand
from dataclasses import asdict

from riocli.apply.parse import Applier
from riocli.apply.util import process_files_values_secrets
from riocli.config import get_config_from_context
from riocli.constants import Colors
from riocli.convert.model import DockerCompose
from riocli.convert.populate import populate


@click.command(
    "convert",
    cls=HelpColorsCommand,
    help_headers_color=Colors.YELLOW,
    help_options_color=Colors.GREEN,
)
@click.option(
    "--name",
    "-n",
    default="docker-compose.yml",
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
    values: typing.Tuple[str],
    secrets: typing.Tuple[str],
    files: typing.Tuple[str],
    path: str,
) -> None:
    if os.path.isfile(path):
        click.secho(
            "Invalid path: expected a directory, but received a file.", fg=Colors.RED
        )
        raise SystemError

    glob_files, abs_values, abs_secrets = process_files_values_secrets(
        files, values, secrets
    )

    if len(path) == 0 or len(glob_files) == 0:
        click.secho("No path or files specified.", fg=Colors.RED)
        raise SystemExit(1)

    config = get_config_from_context(ctx)
    applier = Applier(glob_files, abs_values, abs_secrets, config)
    deployments, packages = sort_deployment_package(applier)
    docker_compose_manifest = populate(deployments, packages)

    write_compose_yaml(
        dir_path=path, file_name=name, compose_dict=docker_compose_manifest
    )


def sort_deployment_package(applier: Applier):
    deployments = {
        k: v for k, v in applier.objects.items()
        if v.get("kind") == "Deployment" and v.get("spec", {}).get("runtime") == "device"
    }
    packages = {
        k: v for k, v in applier.objects.items()
        if v.get("kind") == "Package" and v.get("spec", {}).get("runtime") == "device"
    }
    return deployments, packages


def write_compose_yaml(compose_dict: DockerCompose, dir_path: str, file_name: str):
    """
    Writes the given Docker Compose dictionary to a YAML file.

    Args:
        compose_dict (dict): Dictionary representing the Docker Compose configuration.
        dir_path (str): Directory path where the YAML file will be written.
        file_name (str): Name of the output YAML file.
    """
    # Use yaml.SafeDumper to ensure safe output, and sort_keys=False to preserve ordering
    abs_path = os.path.abspath(dir_path) + "/{}".format(file_name)
    cleaned_compose = clean_dict(asdict(compose_dict))
    with open(abs_path, "w") as f:
        yaml.dump(cleaned_compose, f, sort_keys=False, default_flow_style=False)


def clean_dict(data):
    """
    Recursively remove None values, empty lists, and empty dicts from dataclass-to-dict structures.
    """
    if isinstance(data, dict):
        return {
            k: clean_dict(v)
            for k, v in data.items()
            if v is not None and v != {} and v != []
        }
    elif isinstance(data, list):
        return [clean_dict(i) for i in data if i is not None and i != {} and i != []]
    else:
        return data

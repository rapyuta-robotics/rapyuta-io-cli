from __future__ import annotations

import typing
from dataclasses import asdict
from pathlib import Path

import click
from munch import munchify
import yaml
from click_help_colors import HelpColorsCommand

from riocli.apply.parse import Applier
from riocli.apply.util import process_files_values_secrets
from riocli.config import get_config_from_context
from riocli.constants import Colors
from riocli.compose.defaults import DEFAULT_COMPOSE_FILENAME, DEVICE_RUNTIME
from riocli.compose.model import DockerCompose
from riocli.compose.populate import populate
from riocli.utils import print_centered_text


# Expose the command for import
@click.command(
    "generate",
    cls=HelpColorsCommand,
    help_headers_color=Colors.YELLOW,
    help_options_color=Colors.GREEN,
)
@click.option(
    "--file",
    "-f",
    "file_name",
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
    "--path",
    "-p",
    default=Path.cwd(),
    help="Define path for output of compose file.",
    type=click.Path(
        exists=True, dir_okay=True, file_okay=False, path_type=Path, resolve_path=True
    ),
)
@click.argument("files", nargs=-1)
@click.pass_context
def generate(
    ctx: click.Context,
    file_name: str,
    values: typing.Tuple[str, ...],
    secrets: typing.Tuple[str, ...],
    path: Path,
    files: typing.Tuple[str, ...],
) -> None:
    """
    Convert Rapyuta.io manifests into a Docker Compose YAML file.

    This command processes one or more manifest files along with optional values and SOPS-encrypted secrets,
    generating a ready-to-use `docker-compose.yaml` file.

    Examples:

        Convert a single manifest with values and secrets:

            rio compose generate -v values.yaml -s secrets.yaml manifest.yaml

        Convert all manifests in a directory:

            rio compose generate -v values.yaml -s secrets.yaml templates/

        Specify a custom output path and file name:

            rio compose generate -v values.yaml -s secrets.yaml templates/ -p ./compose_output -f compose.yaml
    """

    if not path:
        click.secho("No path specified.", fg=Colors.RED)
    compose_path = path.absolute() / file_name
    generate_compose_file(
        ctx=ctx,
        compose_path=compose_path,
        values=values,
        secrets=secrets,
        files=files,
    )


def generate_compose_file(
    ctx: click.Context,
    compose_path: Path,
    values: typing.Tuple[str, ...],
    secrets: typing.Tuple[str, ...],
    files: typing.Tuple[str, ...],
):
    glob_files, abs_values, abs_secrets = process_files_values_secrets(
        files, values, secrets
    )

    # Validate required inputs
    if not glob_files:
        click.secho("No files specified.", fg=Colors.RED)
        raise SystemExit(1)

    # Parse and process manifests
    config = get_config_from_context(ctx)
    applier = Applier(glob_files, abs_values, abs_secrets, config)
    deployments, packages = get_deployment_package(applier)

    print_centered_text("Converting Manifests")
    docker_compose_manifest = populate(
        ctx=ctx, deployments=deployments, packages=packages
    )

    write_compose_yaml(output_path=compose_path, compose_dict=docker_compose_manifest)


def get_deployment_package(
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

    return munchify(deployments), munchify(packages)


def write_compose_yaml(compose_dict: DockerCompose, output_path: Path) -> None:
    """
    Write a Docker Compose configuration to a YAML file.

    Args:
        compose_dict: DockerCompose dataclass instance to serialize.
        output_path: Path object specifying where to write the YAML file.

    Raises:
        OSError: If writing the file fails.
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
        click.secho(
            f"Docker Compose file written to: {output_path.relative_to(Path.cwd())}",
            fg=Colors.GREEN,
        )
    except OSError as e:
        click.secho(
            f"Error writing file {output_path.relative_to(Path.cwd())}: {e}",
            fg=Colors.RED,
        )
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

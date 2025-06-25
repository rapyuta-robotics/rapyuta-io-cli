from pathlib import Path
import typing
import click
from click_help_colors import HelpColorsCommand

from riocli.constants.colors import Colors
from riocli.compose.generate import generate_compose_file
from riocli.compose.compose import DockerComposeManager
from riocli.compose.defaults import DEFAULT_COMPOSE_FILENAME
from riocli.utils import print_centered_text


@click.command(
    "up",
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
@click.option(
    "--no-detach",
    "-nd",
    "no_detach",
    is_flag=True,
    help="Detached mode: Run containers in the background",
)
@click.option(
    "--build",
    is_flag=True,
    help="Build images before starting containers",
)
@click.argument("files", nargs=-1)
@click.pass_context
def up(
    ctx: click.Context,
    file_name: str,
    values: typing.Tuple[str, ...],
    secrets: typing.Tuple[str, ...],
    path: str,
    no_detach: bool,
    build: bool,
    files: typing.Tuple[str, ...],
):
    """
    Generate and start services using Docker Compose.

    If the compose file doesn't exist, it will be created before launching the services.

    By default, containers are started in detached mode unless `--no-detach` is specified.
    Use `--build` to build images before starting containers.

    Examples:

        Apply a single manifest with values and secrets:

            rio compose up -v values.yaml -s secrets.yaml manifest.yaml

        Apply manifests from a directory:

            rio compose up -v values.yaml -s secrets.yaml templates/

        Specify a custom output path and compose file name:

            rio compose up -v values.yaml -s secrets.yaml templates/ -p ./compose_output -f compose.yaml

        Run in attached mode with image build:

            rio compose up -v values.yaml -s secrets.yaml -nd --build templates/
    """

    compose_path = path.absolute() / file_name

    generate_compose_file(
        ctx=ctx,
        compose_path=compose_path,
        files=files,
        values=values,
        secrets=secrets,
    )

    compose_manager = DockerComposeManager(compose_path=compose_path)

    if not compose_manager.validate_docker_availability():
        raise SystemExit(1)

    detach = not no_detach

    print_centered_text("Starting docker services")
    if not compose_manager.up(detached=detach, build=build):
        click.secho("Docker Compose up operation failed.", fg=Colors.RED)
        raise SystemExit(1)

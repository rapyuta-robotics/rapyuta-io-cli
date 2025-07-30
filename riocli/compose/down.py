import typing
from pathlib import Path

import click
from click_help_colors import HelpColorsCommand

from riocli.compose.compose import DockerComposeManager
from riocli.compose.defaults import DEFAULT_COMPOSE_FILENAME
from riocli.compose.generate import generate_compose_file
from riocli.constants.colors import Colors


@click.command(
    "down",
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
def down(
    ctx: click.Context,
    file_name: str,
    values: typing.Tuple[str, ...],
    secrets: typing.Tuple[str, ...],
    path: str,
    files: typing.Tuple[str, ...],
):
    """
    Stop and remove services defined in the Docker Compose file.

    If the compose file does not exist, it will be generated using the provided manifest(s),
    values, and secret files before bringing the services down.

    Examples:

        Apply a single manifest with values and secrets:

            rio compose down -v values.yaml -s secrets.yaml manifest.yaml

        Apply manifests from a directory:

            rio compose down -v values.yaml -s secrets.yaml templates/

        Specify a custom output path and compose file name:

            rio compose down -v values.yaml -s secrets.yaml templates/ -p ./compose_output -f compose.yaml
    """

    compose_path = path.absolute() / file_name
    compose_manager = DockerComposeManager(compose_path=compose_path)

    if not compose_path.exists() or compose_manager.check_empty_file():
        click.secho(
            f"Compose file '{compose_path}' does not exist or is empty.", fg=Colors.YELLOW
        )
        generate_compose_file(
            ctx=ctx,
            compose_path=compose_path,
            values=values,
            secrets=secrets,
            files=files,
        )

    if not compose_manager.validate_docker_availability():
        raise SystemExit(1)

    if not compose_manager.down():
        click.secho("Docker Compose down operation failed.", fg=Colors.RED)
        raise SystemExit(1)

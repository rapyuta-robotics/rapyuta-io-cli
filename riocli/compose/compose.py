"""
Docker Compose operations manager for the convert module.
"""

from __future__ import annotations

import subprocess
from pathlib import Path
from typing import Optional

import click

from riocli.constants.colors import Colors


class DockerComposeManager:
    """
    Manages Docker Compose operations for converted manifests.
    """

    def __init__(self, compose_path: Path):
        self.absolute_path = compose_path.resolve()
        self.compose_path = compose_path.relative_to(Path.cwd())

    def file_exists(self) -> bool:
        return self.absolute_path.exists()

    def check_empty_file(self) -> bool:
        return self.absolute_path.stat().st_size == 0

    def up(self, detached: bool = False, build: bool = False) -> bool:
        # Run 'docker compose up' for the compose file.
        if not self.file_exists():
            click.secho(
                f"Docker Compose file not found: {self.compose_path}", fg=Colors.RED
            )
            return False

        cmd = ["docker", "compose", "-f", str(self.absolute_path), "up"]

        if detached:
            cmd.append("-d")
        if build:
            cmd.append("--build")

        try:
            result = subprocess.run(
                cmd,
                check=True,
            )
            click.secho(
                f"Successfully started Docker Compose services from {self.compose_path}",
                fg=Colors.GREEN,
            )
            if result.stdout:
                click.echo(result.stdout)
            return True

        except subprocess.CalledProcessError as e:
            click.secho(f"Failed to run 'docker compose up': {e}", fg=Colors.RED)
            if e.stderr:
                click.secho(f"Error details: {e.stderr}", fg=Colors.RED)
            return False

        except FileNotFoundError:
            click.secho(
                "Docker Compose is not installed or not found in PATH", fg=Colors.RED
            )
            return False

    def down(self, remove_volumes: bool = False, remove_images: bool = False) -> bool:
        # Run 'docker compose down' for the compose file.
        if not self.file_exists():
            click.secho(
                f"Docker Compose file not found: {self.compose_path}", fg=Colors.YELLOW
            )
            return True  # Not an error if file doesn't exist for down operation

        cmd = ["docker", "compose", "-f", str(self.absolute_path), "down"]

        if remove_volumes:
            cmd.append("-v")
        if remove_images:
            cmd.append("--rmi=all")

        try:
            result = subprocess.run(
                cmd,
                check=True,
            )
            click.secho(
                f"Successfully stopped Docker Compose services from {self.compose_path}",
                fg=Colors.GREEN,
            )
            if result.stdout:
                click.echo(result.stdout)
            return True

        except subprocess.CalledProcessError as e:
            click.secho(f"Failed to run 'docker compose down': {e}", fg=Colors.RED)
            if e.stderr:
                click.secho(f"Error details: {e.stderr}", fg=Colors.RED)
            return False

        except FileNotFoundError:
            click.secho(
                "Docker Compose is not installed or not found in PATH", fg=Colors.RED
            )
            return False

    def status(self) -> Optional[str]:
        # Get the status of Docker Compose services.
        if not self.file_exists():
            return None

        try:
            result = subprocess.run(
                ["docker", "compose", "-f", str(self.absolute_path), "ps"],
                check=True,
                capture_output=True,
                text=True,
            )
            return result.stdout

        except (subprocess.CalledProcessError, FileNotFoundError):
            return None

    def validate_docker_availability(self) -> bool:
        # Validate that Docker and Docker Compose are available.
        try:
            # Check Docker
            subprocess.run(["docker", "--version"], check=True, capture_output=True)

            # Check Docker Compose
            subprocess.run(
                ["docker", "compose", "version"], check=True, capture_output=True
            )
            return True

        except (subprocess.CalledProcessError, FileNotFoundError):
            click.secho(
                "Docker or Docker Compose is not installed or not available",
                fg=Colors.RED,
            )
            return False

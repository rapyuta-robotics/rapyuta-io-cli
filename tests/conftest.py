"""
Pytest configuration and fixtures for rapyuta.io CLI tests.

This module provides common fixtures and configuration for all CLI tests,
including CLI runner setup and test user configurations.
"""

import json
import os
from pathlib import Path

import pytest
from click.testing import CliRunner

from riocli.bootstrap import cli


def load_password_config():
    """Load password configuration from .password file"""
    password_file = Path(__file__).parent / ".password"
    passwords = {}

    if password_file.exists():
        with open(password_file) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#"):
                    if "=" in line:
                        key, value = line.split("=", 1)
                        passwords[key.strip()] = value.strip()

    # Fallback to default if no password file exists
    return passwords.get("DEFAULT_PASSWORD")


@pytest.fixture(scope="session", autouse=True)
def setup_test_config():
    """Automatically set RIO_CONFIG environment variable for all tests."""
    config_path = Path(__file__).parent / ".test.config.json"
    if not config_path.exists():
        pytest.skip(f"Test config file not found: {config_path}")

    # Set the environment variable for the entire test session
    os.environ["RIO_CONFIG"] = str(config_path)

    yield

    # Cleanup: Remove the environment variable after tests
    if "RIO_CONFIG" in os.environ:
        del os.environ["RIO_CONFIG"]


@pytest.fixture(scope="session")
def test_config():
    """Load test configuration from .test.config.json file."""
    config_path = Path(__file__).parent / ".test.config.json"
    if not config_path.exists():
        pytest.skip(f"Test config file not found: {config_path}")

    with open(config_path) as f:
        return json.load(f)


class RBACTestUser:
    """Helper class to represent a test user with their credentials"""

    def __init__(
        self,
        email: str,
        organization: str,
        password: str = None,
        auth_token: str = None,
    ):
        self.email = email
        self.organization = organization
        self.password = password or load_password_config()
        self.auth_token = auth_token

    def login(self, runner: CliRunner, project_name: str = None) -> None:
        """Login with this user's credentials"""
        cmd = [
            "auth",
            "login",
            "--email",
            self.email,
            "--password",
            self.password,
            "--organization",
            self.organization,
            "--no-interactive",
        ]

        if project_name:
            cmd.extend(["--project", project_name])

        result = runner.invoke(cli, cmd)
        if "Logged in successfully" not in result.output:
            raise AssertionError(f"Login failed for {self.email}: {result.output}")


@pytest.fixture
def cli_runner():
    """Provides a Click CLI runner for testing CLI commands."""
    return CliRunner()


@pytest.fixture
def test_user_from_config(test_config):
    """Test user loaded from configuration file."""
    return RBACTestUser(
        email=test_config["email_id"],
        organization=test_config["organization_name"],
        auth_token=test_config.get("auth_token"),
    )


@pytest.fixture
def super_user():
    return RBACTestUser("cli.superuser@rapyuta-robotics.com", "CliTest")


@pytest.fixture
def test_user_11():
    """Test user from Rapyuta2 organization with limited permissions."""
    return RBACTestUser("cli.test1@rapyuta-robotics.com", "CliTest")


@pytest.fixture
def test_user_12():
    """Test user from Rapyuta organization with different permissions."""
    return RBACTestUser("cli.test2@rapyuta-robotics.com", "CliTest")


@pytest.fixture
def test_projects():
    """List of test projects for testing."""
    return ["test-project1", "test-project2"]


@pytest.fixture
def logged_in_user_from_config(cli_runner, test_user_from_config, test_config):
    """Provides a CLI runner with test user from config already logged in."""
    project_name = test_config["project_name"]
    test_user_from_config.login(cli_runner, project_name=project_name)
    return cli_runner, test_user_from_config


@pytest.fixture
def logged_in_user_11(cli_runner, test_user_11, test_projects):
    """Provides a CLI runner with test_user_11 already logged in."""
    # Use the first project from test_projects
    project_name = test_projects[0]
    test_user_11.login(cli_runner, project_name=project_name)
    return cli_runner, test_user_11


@pytest.fixture
def logged_in_user_12(cli_runner, test_user_12, test_projects):
    """Provides a CLI runner with test_user_12 already logged in."""
    # Use the first project from test_projects
    project_name = test_projects[0]
    test_user_12.login(cli_runner, project_name=project_name)
    return cli_runner, test_user_12


@pytest.fixture(autouse=True)
def isolation():
    """
    Provides test isolation by ensuring each test starts with a clean state.
    This fixture runs automatically for every test.
    """
    # Setup: could add cleanup logic here if needed
    yield
    # Teardown: could add cleanup logic here if needed
    pass

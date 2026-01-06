"""
Authentication and login tests for rapyuta.io CLI.

This module tests various authentication scenarios using pytest and Click testing.
"""

from pathlib import Path

import pytest

from riocli.bootstrap import cli


def load_test_password():
    """Load password from .password file for tests"""
    password_file = Path(__file__).parent.parent / ".password"
    if password_file.exists():
        with open(password_file) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "DEFAULT_PASSWORD=" in line:
                    return line.split("=", 1)[1].strip()
    else:
        raise Exception("No password file found. Please create one")


@pytest.mark.auth
def test_login_missing_credentials(cli_runner):
    """Test login behavior with missing credentials"""
    result = cli_runner.invoke(cli, ["auth", "login", "--no-interactive"])

    assert "email not specified" in result.output, (
        f"Expected 'email not specified' in output, but got: {result.output}"
    )


@pytest.mark.auth
@pytest.mark.integration
@pytest.mark.slow
@pytest.mark.parametrize(
    "email", ["cli.test1@rapyuta-robotics.com", "cli.test2@rapyuta-robotics.com"]
)
def test_login_success_with_project(cli_runner, test_config, test_projects, email):
    """Test login behavior when project is specified with organization"""
    test_password = load_test_password()

    result = cli_runner.invoke(
        cli,
        [
            "auth",
            "login",
            "--email",
            email,
            "--password",
            test_password,
            "--organization",
            "CliTest",
            "--project",
            test_projects[0],  # Use first project from test_projects fixture
            "--no-interactive",
        ],
    )

    assert "Logged in successfully" in result.output

"""
Pytest configuration and fixtures for rapyuta.io CLI tests.

This module provides common fixtures and configuration for all CLI tests,
including CLI runner setup and test user configurations.
"""

import json
import os
import time
from pathlib import Path

import pytest
from click.testing import CliRunner
from rapyuta_io_sdk_v2 import walk_pages

from riocli.bootstrap import cli
from riocli.config import new_v2_client
from riocli.device.util import find_device_guid


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

    return passwords


def get_default_password():
    """Get the default password from .password file"""
    passwords = load_password_config()
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
        self.password = password or get_default_password()
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


@pytest.fixture(scope="module")
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


@pytest.fixture(scope="module")
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
def test_user_11_email(test_user_11):
    """Email address for test_user_11."""
    return test_user_11.email


@pytest.fixture
def test_user_12_email(test_user_12):
    """Email address for test_user_12."""
    return test_user_12.email


@pytest.fixture(scope="module")
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


@pytest.fixture(scope="module")
def test_device(test_device_setup):
    """Provides just the device name from test_device_setup"""
    return test_device_setup["device_name"]


@pytest.fixture(scope="module")
def device_file_factory(cli_runner):
    """Factory fixture to create files on a device

    Creates files directly on the onboarded device using device execute command.

    Args:
        device_name: Name of the device
        file_name: Name of the file to create on the device
        size_bytes: Size of the file in bytes (default: 1024)
        device_path: Path on device where file should be created (default: /tmp/)

    Returns:
        Full path to the file on the device

    Example:
        file_path = device_file_factory(device_name, "test.txt", 2048)
        # Returns: "/tmp/test.txt"
    """

    def _create_file_on_device(
        device_name: str,
        file_name: str,
        size_bytes: int = 1024,
        device_path: str = "/tmp",
    ) -> str:
        """Create a file on the device with specified name and size"""
        full_path = f"{device_path.rstrip('/')}/{file_name}"

        if size_bytes < 1024:
            size_kb = 1
        else:
            size_kb = (size_bytes + 1023) // 1024

        create_cmd = f"dd if=/dev/zero of={full_path} bs=1024 count={size_kb} 2>/dev/null && echo 'File created successfully'"

        result = cli_runner.invoke(cli, ["device", "execute", device_name, create_cmd])

        if result.exit_code == 0:
            return full_path
        else:
            raise RuntimeError(f"Failed to create file on device: {result.output}")

    yield _create_file_on_device


@pytest.fixture(scope="module")
def hwil_login(cli_runner):
    """Login to HWIL for virtual device operations"""
    passwords = load_password_config()
    hwil_username = passwords.get("HWIL_USERNAME")
    hwil_password = passwords.get("HWIL_PASSWORD")

    if not hwil_username or not hwil_password:
        pytest.skip("HWIL credentials not found in .password file")

    result = cli_runner.invoke(
        cli,
        [
            "hwil",
            "login",
            "--username",
            hwil_username,
            "--password",
            hwil_password,
            "--no-interactive",
        ],
    )

    if result.exit_code != 0:
        pytest.skip(f"HWIL login failed: {result.output}")

    return result


@pytest.fixture(scope="module")
def test_device_setup(
    cli_runner, super_user, test_projects, device_file_factory, hwil_login
):
    """Create and setup test device with pre-created files for file upload tests

    Returns:
        dict with keys:
            - device_name: Name of the created device
            - small_file: Path to small test file on device
            - large_file: Path to large test file on device
    """
    device_manifest = (
        Path(__file__).parent / "fixtures" / "manifests" / "device" / "test-devices.yaml"
    )
    device_name = "test-upload-device"

    super_user.login(cli_runner, project_name=test_projects[0])

    result = cli_runner.invoke(
        cli, ["apply", "--silent", "--delete-existing", str(device_manifest)]
    )
    assert result.exit_code == 0, result.output

    max_retries = 20
    interval = 5
    for _ in range(max_retries):
        result = cli_runner.invoke(cli, ["device", "list"])
        if result.exit_code == 0 and device_name in result.output:
            break
        time.sleep(interval)

    small_file = device_file_factory(device_name, "test-upload.txt", 100)
    large_file = device_file_factory(device_name, "large-upload.txt", 20000)

    setup_data = {
        "device_name": device_name,
        "small_file": small_file,
        "large_file": large_file,
    }

    yield setup_data

    super_user.login(cli_runner, project_name=test_projects[0])

    try:
        client = new_v2_client()
        device_guid = find_device_guid(client, device_name)

        uploads = []
        for page in walk_pages(client.list_fileuploads, device_guid=device_guid):
            uploads.extend(page)

        for upload in uploads:
            file_name = upload.spec.file_name
            cli_runner.invoke(
                cli, ["device", "uploads", "delete", device_name, file_name]
            )
    except Exception:
        pass

    cli_runner.invoke(cli, ["delete", "--silent", str(device_manifest)])

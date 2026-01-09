"""
Organization user management tests for rapyuta.io CLI.

This module tests organization user management scenarios including
adding and removing users from organizations.
"""

import pytest

from riocli.bootstrap import cli


@pytest.mark.organization
@pytest.mark.integration
@pytest.mark.slow
def test_remove_user_from_organization(cli_runner, super_user, test_projects):
    """Test removing a user from the organization"""
    # Login as superuser (organization admin)
    super_user.login(cli_runner, project_name=test_projects[0])

    # Remove user cli.test1@rapyuta-robotics.com from organization
    result = cli_runner.invoke(
        cli, ["organization", "remove-user", "cli.test1@rapyuta-robotics.com"]
    )

    # Should succeed or user already not in organization
    assert result.exit_code == 0, (
        f"Failed to remove user from organization. "
        f"Exit code: {result.exit_code}, Output: {result.output}"
    )
    assert (
        "Users removed successfully" in result.output
        or "Users are not part of the organization" in result.output
    ), f"Unexpected output: {result.output}"


@pytest.mark.organization
@pytest.mark.integration
@pytest.mark.slow
def test_add_user_to_organization(cli_runner, super_user, test_projects):
    """Test adding a user back to the organization"""
    # Login as superuser (organization admin)
    super_user.login(cli_runner, project_name=test_projects[0])

    # Add user cli.test1@rapyuta-robotics.com to organization
    result = cli_runner.invoke(
        cli, ["organization", "add-user", "cli.test1@rapyuta-robotics.com"]
    )

    # Should succeed
    assert result.exit_code == 0, (
        f"Failed to add user to organization. "
        f"Exit code: {result.exit_code}, Output: {result.output}"
    )
    assert "Users added successfully" in result.output, (
        f"Unexpected output: {result.output}"
    )


@pytest.mark.organization
@pytest.mark.integration
@pytest.mark.slow
def test_list_organization_users(cli_runner, super_user, test_projects):
    """Test listing users in the organization to verify user was added"""
    # Login as superuser (organization admin)
    super_user.login(cli_runner, project_name=test_projects[0])

    # List organization users
    result = cli_runner.invoke(cli, ["organization", "users"])

    # Should succeed
    assert result.exit_code == 0, (
        f"Failed to list organization users. "
        f"Exit code: {result.exit_code}, Output: {result.output}"
    )

    # Check that cli.test1@rapyuta-robotics.com is in the list
    assert "cli.test1@rapyuta-robotics.com" in result.output, (
        f"User cli.test1@rapyuta-robotics.com not found in organization users list. "
        f"Output: {result.output}"
    )


@pytest.mark.organization
@pytest.mark.integration
@pytest.mark.slow
def test_remove_multiple_users(cli_runner, super_user, test_projects):
    """Test removing multiple users from the organization at once"""
    # Login as superuser (organization admin)
    super_user.login(cli_runner, project_name=test_projects[0])

    # First add the users
    cli_runner.invoke(
        cli,
        [
            "organization",
            "add-user",
            "cli.test1@rapyuta-robotics.com",
            "cli.test2@rapyuta-robotics.com",
        ],
    )

    # Remove multiple users at once
    result = cli_runner.invoke(
        cli,
        [
            "organization",
            "remove-user",
            "cli.test1@rapyuta-robotics.com",
            "cli.test2@rapyuta-robotics.com",
        ],
    )

    # Should succeed
    assert result.exit_code == 0, (
        f"Failed to remove multiple users from organization. "
        f"Exit code: {result.exit_code}, Output: {result.output}"
    )
    assert (
        "Users removed successfully" in result.output
        or "Users are not part of the organization" in result.output
    ), f"Unexpected output: {result.output}"


@pytest.mark.organization
@pytest.mark.integration
@pytest.mark.slow
def test_add_multiple_users(cli_runner, super_user, test_projects):
    """Test adding multiple users to the organization at once"""
    # Login as superuser (organization admin)
    super_user.login(cli_runner, project_name=test_projects[0])

    # Add multiple users at once
    result = cli_runner.invoke(
        cli,
        [
            "organization",
            "add-user",
            "cli.test1@rapyuta-robotics.com",
            "cli.test2@rapyuta-robotics.com",
        ],
    )

    # Should succeed
    assert result.exit_code == 0, (
        f"Failed to add multiple users to organization. "
        f"Exit code: {result.exit_code}, Output: {result.output}"
    )
    assert (
        "Users added successfully" in result.output
        or "Users are already part of the organization" in result.output
    ), f"Unexpected output: {result.output}"


@pytest.mark.organization
def test_remove_user_with_invalid_email(cli_runner, super_user, test_projects):
    """Test removing a user with invalid email format"""
    # Login as superuser (organization admin)
    super_user.login(cli_runner, project_name=test_projects[0])

    # Try to remove user with invalid email
    result = cli_runner.invoke(cli, ["organization", "remove-user", "invalid-email"])

    # Should fail
    assert result.exit_code != 0, (
        f"Should fail with invalid email. "
        f"Exit code: {result.exit_code}, Output: {result.output}"
    )
    assert "not a valid email address" in result.output, (
        f"Unexpected output: {result.output}"
    )


@pytest.mark.organization
def test_add_user_with_invalid_email(cli_runner, super_user, test_projects):
    """Test adding a user with invalid email format"""
    # Login as superuser (organization admin)
    super_user.login(cli_runner, project_name=test_projects[0])

    # Try to add user with invalid email
    result = cli_runner.invoke(cli, ["organization", "add-user", "invalid-email"])

    # Should fail
    assert result.exit_code != 0, (
        f"Should fail with invalid email. "
        f"Exit code: {result.exit_code}, Output: {result.output}"
    )
    assert "not a valid email address" in result.output, (
        f"Unexpected output: {result.output}"
    )


@pytest.mark.organization
def test_remove_user_without_email(cli_runner, super_user, test_projects):
    """Test removing a user without specifying email"""
    # Login as superuser (organization admin)
    super_user.login(cli_runner, project_name=test_projects[0])

    # Try to remove user without email
    result = cli_runner.invoke(cli, ["organization", "remove-user"])

    # Should fail
    assert result.exit_code != 0, (
        f"Should fail when no email specified. "
        f"Exit code: {result.exit_code}, Output: {result.output}"
    )
    assert "No user specified" in result.output, f"Unexpected output: {result.output}"


@pytest.mark.organization
@pytest.mark.integration
@pytest.mark.slow
@pytest.mark.parametrize(
    "user_email", ["cli.test1@rapyuta-robotics.com", "cli.test2@rapyuta-robotics.com"]
)
@pytest.mark.parametrize("project", ["test-project1", "test-project2"])
def test_allow_project_get_access(cli_runner, super_user, project, user_email):
    """Test granting project get access to users via role binding"""
    super_user.login(cli_runner, project_name="test-project1")

    result = cli_runner.invoke(
        cli,
        ["apply", "tests/fixtures/manifests/organization/project-viewer-role.yaml", "-f"],
    )
    assert result.exit_code == 0, result.output

    result = cli_runner.invoke(
        cli,
        [
            "role",
            "bind",
            "project-viewer-only",
            f"Project:{project}",
            f"User:{user_email}",
        ],
    )
    assert result.exit_code == 0, result.output

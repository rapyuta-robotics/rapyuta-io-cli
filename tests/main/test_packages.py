"""
RBAC Tests for rapyuta.io CLI - Package Operations

This module tests Role-Based Access Control scenarios for package operations
using pytest and Click testing framework. It covers:
- Super user creating roles and packages
- Test users with restricted access to packages
- Pydantic model validation for invalid manifests
"""

from pathlib import Path

import pytest

from riocli.bootstrap import cli


@pytest.mark.rbac
@pytest.mark.integration
@pytest.mark.slow
class TestPackagesRBAC:
    """Test class for Package RBAC scenarios"""

    @pytest.fixture(autouse=True)
    def setup_manifests(self):
        """Setup manifest file paths"""
        self.manifests_dir = (
            Path(__file__).parent.parent / "fixtures" / "manifests" / "rbac"
        )
        self.role_manifest = self.manifests_dir / "package-role.yaml"
        self.package_correct = (
            self.manifests_dir / "package-correct.yaml"
        )  # Super user creates these
        self.package_manifest = (
            self.manifests_dir / "package.yaml"
        )  # Test users create these
        self.package_wrong_manifest = self.manifests_dir / "package-wrong.yaml"

    def test_super_user_creates_role(self, cli_runner, super_user, test_projects):
        """Test that superuser can create the role for package access"""
        # Login as superuser
        super_user.login(cli_runner, project_name=test_projects[0])

        # Create role using apply command
        result = cli_runner.invoke(cli, ["apply", "--silent", str(self.role_manifest)])

        # Should succeed
        assert result.exit_code == 0
        assert "Created" in result.output or "Updated" in result.output

    def test_super_user_creates_packages(self, cli_runner, super_user, test_projects):
        """Test that superuser can create packages"""
        # Login as superuser
        super_user.login(cli_runner, project_name=test_projects[0])

        # Create packages from package-correct.yaml
        # (contains test-package-1, test-package-2, package-docker, unauthorized-package)
        result = cli_runner.invoke(
            cli,
            [
                "apply",
                "--silent",
                str(self.package_correct),
            ],
        )

        # Should succeed
        assert result.exit_code == 0
        assert "Apply successful" in result.output

    def test_super_user_binds_role_to_test_users(
        self, cli_runner, super_user, test_user_11, test_user_12, test_projects
    ):
        """Test that superuser can bind the role to test users"""
        # Login as superuser
        super_user.login(cli_runner, project_name=test_projects[0])

        # Bind role to test_user_11
        result = cli_runner.invoke(
            cli,
            [
                "role",
                "bind",
                "package-viewer",
                f"Project:{test_projects[0]}",
                f"User:{test_user_11.email}",
            ],
        )

        # Should succeed
        assert result.exit_code == 0

        # Bind role to test_user_12
        result = cli_runner.invoke(
            cli,
            [
                "role",
                "bind",
                "package-viewer",
                f"Project:{test_projects[0]}",
                f"User:{test_user_12.email}",
            ],
        )

        # Should succeed
        assert result.exit_code == 0

    def test_user11_creates_packages_from_manifest(self, logged_in_user_11):
        """Test that test_user_11 creates packages from package.yaml"""
        runner, user = logged_in_user_11

        # Create packages from package.yaml
        # This contains test-package-4 (should succeed) and random-package (should fail)
        result = runner.invoke(cli, ["apply", "--silent", str(self.package_manifest)])

        # The result might be mixed - some packages succeed, others fail
        # We'll verify the actual results in the list test
        assert result.exit_code != 0
        assert "Created package:test-package-4" in result.output
        assert (
            "Failed to apply package:random-package. Error: subject is not authorized for this operation"
            in result.output
        )

    def test_user11_can_list_packages(self, logged_in_user_11):
        """Test that test_user_11 can list all packages"""
        runner, user = logged_in_user_11

        result = runner.invoke(cli, ["package", "list"])

        # Should succeed
        assert result.exit_code == 0, (
            f"Package list should succeed for {user.email}. "
            f"Exit code: {result.exit_code}, Output: {result.output}"
        )

        # User should be able to see packages that match test-package.* pattern
        expected_visible = [
            "test-package-1",
            "test-package-2",
            "test-package-4",
            "package-docker",
            "unauthorized-package",
        ]

        # Check that authorized packages are visible
        for package in expected_visible:
            assert package in result.output

    def test_user11_can_inspect_authorized_packages(self, logged_in_user_11):
        """Test that test_user_11 can inspect packages matching the role pattern"""
        runner, user = logged_in_user_11

        # Should be able to inspect test-package-1
        result = runner.invoke(cli, ["package", "inspect", "test-package-1"])

        assert result.exit_code == 0

        # Should be able to inspect test-package-2
        result = runner.invoke(cli, ["package", "inspect", "test-package-2"])

        assert result.exit_code == 0

        # Should be able to inspect test-package-4 from package.yaml
        result = runner.invoke(cli, ["package", "inspect", "test-package-4"])

        assert result.exit_code == 0

    def test_user11_cannot_inspect_unauthorized_packages(self, logged_in_user_11):
        """Test that test_user_11 cannot inspect packages not matching the role pattern"""
        runner, user = logged_in_user_11

        # Should NOT be able to inspect unauthorized-package
        result = runner.invoke(cli, ["package", "inspect", "unauthorized-package"])

        assert result.exit_code != 0
        assert "subject is not authorized for this operation" in result.output

        # Should NOT be able to inspect random-package (doesn't match test-package.* pattern)
        result = runner.invoke(cli, ["package", "inspect", "random-package"])

        assert result.exit_code != 0
        # Check for authorization error messages
        assert "package not found" in result.output

    def test_user11_cannot_delete_packages(self, logged_in_user_11):
        """Test that test_user_11 cannot delete packages (only has get/list permissions)"""
        runner, user = logged_in_user_11

        # Should NOT be able to delete even authorized packages
        result = runner.invoke(
            cli, ["package", "delete", "test-package-1", "--force", "--silent"]
        )

        assert result.exit_code != 0
        assert "subject is not authorized for this operation" in result.output

    def test_user11_cannot_delete_own_package(self, logged_in_user_11):
        """Test that test_user_11 cannot delete packages (only has get/list permissions)"""
        runner, user = logged_in_user_11

        # Should NOT be able to delete even their own packages
        result = runner.invoke(
            cli, ["package", "delete", "test-package-4", "--force", "--silent"]
        )

        assert result.exit_code == 1
        assert "subject is not authorized for this operation" in result.output

    def test_superuser_can_delete_package(self, super_user, cli_runner, test_projects):
        """Test that superuser can delete packages"""
        super_user.login(cli_runner, project_name=test_projects[0])

        # Should be able to delete package as superuser
        result = cli_runner.invoke(
            cli, ["package", "delete", "test-package-4", "--force", "--silent"]
        )

        assert result.exit_code == 0

    def test_user12_creates_packages_from_manifest(self, logged_in_user_12):
        """Test that test_user_12 creates packages from package.yaml"""
        runner, user = logged_in_user_12

        # Create packages from package.yaml
        # This contains test-package-4 (should succeed) and random-package (should fail)
        result = runner.invoke(cli, ["apply", "--silent", str(self.package_manifest)])

        assert result.exit_code != 0
        assert "Created package:test-package-4" in result.output
        assert (
            "Failed to apply package:random-package. Error: subject is not authorized for this operation"
            in result.output
        )

    def test_user12_can_list_packages(self, logged_in_user_12):
        """Test that test_user_12 can list all packages"""
        runner, user = logged_in_user_12

        result = runner.invoke(cli, ["package", "list"])

        # Should succeed
        assert result.exit_code == 0, (
            f"Package list should succeed for {user.email}. "
            f"Exit code: {result.exit_code}, Output: {result.output}"
        )

        # User should be able to see packages that match test-package.* pattern
        expected_visible = [
            "test-package-1",
            "test-package-2",
            "test-package-4",
            "package-docker",
            "unauthorized-package",
        ]

        # Check that authorized packages are visible
        for package in expected_visible:
            assert package in result.output

    def test_user12_can_inspect_authorized_packages(self, logged_in_user_12):
        """Test that test_user_12 can inspect packages matching the role pattern"""
        runner, user = logged_in_user_12

        # Should be able to inspect test-package-1
        result = runner.invoke(cli, ["package", "inspect", "test-package-1"])

        assert result.exit_code == 0

        # Should be able to inspect test-package-2
        result = runner.invoke(cli, ["package", "inspect", "test-package-2"])

        assert result.exit_code == 0

        # Should be able to inspect test-package-4 from package.yaml
        result = runner.invoke(cli, ["package", "inspect", "test-package-4"])

        assert result.exit_code == 0

    def test_user12_cannot_inspect_unauthorized_packages(self, logged_in_user_12):
        """Test that test_user_12 cannot inspect packages not matching the role pattern"""
        runner, user = logged_in_user_12

        # Should NOT be able to inspect unauthorized-package
        result = runner.invoke(cli, ["package", "inspect", "unauthorized-package"])

        assert result.exit_code != 0
        # Check for authorization error messages
        assert "subject is not authorized for this operation" in result.output

        # Should NOT be able to inspect random-package (doesn't match test-package.* pattern)
        result2 = runner.invoke(cli, ["package", "inspect", "random-package"])

        assert result2.exit_code != 0
        assert "package not found" in result2.output

    def test_user12_cannot_delete_packages(self, logged_in_user_12):
        """Test that test_user_12 cannot delete packages (only has get/list permissions)"""
        runner, user = logged_in_user_12

        # Should NOT be able to delete even authorized packages
        result = runner.invoke(
            cli, ["package", "delete", "test-package-2", "--force", "--silent"]
        )

        assert result.exit_code != 0
        assert "subject is not authorized for this operation" in result.output

    def test_user12_cannot_delete_own_package(self, logged_in_user_12):
        """Test that test_user_12 cannot delete packages (only has get/list permissions)"""
        runner, user = logged_in_user_12

        # Should NOT be able to delete even their own packages
        result = runner.invoke(
            cli, ["package", "delete", "test-package-4", "--force", "--silent"]
        )

        assert result.exit_code == 1
        assert "subject is not authorized for this operation" in result.output

    def test_pydantic_model_validation_error(self, cli_runner, super_user, test_projects):
        """Test that invalid package manifest fails with pydantic validation error"""
        # Login as super user
        super_user.login(cli_runner, project_name=test_projects[0])

        # Try to apply the wrong manifest (Secret instead of Package)
        result = cli_runner.invoke(
            cli, ["apply", "--silent", str(self.package_wrong_manifest)]
        )

        # Should fail with validation error
        assert result.exit_code != 0
        error_output = result.output
        if hasattr(result, "stderr") and result.stderr:
            error_output += result.stderr
        if result.exception:
            error_output += str(result.exception)
        assert (
            "Field required" in error_output
            or "invalid manifest" in error_output
            or "is a required property" in error_output
            or "'runtime' is a required property" in error_output
        )

    def test_cleanup_resources(self, cli_runner, super_user, test_projects):
        """Cleanup test resources"""
        # Login as super user
        super_user.login(cli_runner, project_name=test_projects[0])

        # Delete packages
        package_manifests = [
            self.package_manifest,  # Contains test-package-4 and random-package
            self.package_correct,
        ]

        for manifest in package_manifests:
            result = cli_runner.invoke(cli, ["delete", "--silent", str(manifest)])
            # Don't assert on exit code as resources might not exist
            assert result.exit_code == 0

        # Unbind roles (if role bindings exist)
        for user_email in [
            "cli.test1@rapyuta-robotics.com",
            "cli.test2@rapyuta-robotics.com",
        ]:
            result = cli_runner.invoke(
                cli,
                [
                    "role",
                    "unbind",
                    "package-viewer",
                    "--user",
                    user_email,
                    "--project",
                    test_projects[0],
                ],
            )
            # Don't assert on exit code as bindings might not exist

        # Delete role
        result = cli_runner.invoke(cli, ["delete", "--silent", str(self.role_manifest)])
        assert result.exit_code == 0

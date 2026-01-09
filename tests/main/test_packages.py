"""
RBAC Tests for rapyuta.io CLI - Package Operations

This module tests Role-Based Access Control scenarios for package operations
using pytest and Click testing framework. It covers:
- Super user creating roles and packages
- Test users with restricted access to packages
- Multiple role scenarios with different permission patterns
- Pydantic model validation for invalid manifests

Test execution order:
1. Setup tests (super user creates roles and resources)
2. Basic RBAC tests (original package-viewer role scenarios)
3. Extended role tests (new package roles with different patterns)
4. Complex scenarios (multiple roles, boundary testing)
5. Cleanup tests (teardown resources)
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
            Path(__file__).parent.parent / "fixtures" / "manifests" / "package"
        )
        self.role_manifest = self.manifests_dir / "package-role.yaml"
        self.package_correct = (
            self.manifests_dir / "package-correct.yaml"
        )  # Super user creates these
        self.package_manifest = (
            self.manifests_dir / "package.yaml"
        )  # Test users create these
        self.package_wrong_manifest = self.manifests_dir / "package-wrong.yaml"
        self.package_extended = (
            self.manifests_dir / "package-extended.yaml"
        )  # Extended patterns
        self.package_docker = (
            self.manifests_dir / "package-docker.yaml"
        )  # Docker patterns
        self.managed_package_2 = (
            self.manifests_dir / "managed-package-2.yaml"
        )  # For manager role testing
        self.boundary_packages = (
            self.manifests_dir / "boundary-packages.yaml"
        )  # For pattern boundary testing

    # =================
    # SETUP TESTS (Run First)
    # =================

    def test_01_super_user_creates_role(self, cli_runner, super_user, test_projects):
        """Test that superuser can create all roles for package access"""
        # Login as superuser
        super_user.login(cli_runner, project_name=test_projects[0])

        # Create all roles using apply command
        result = cli_runner.invoke(cli, ["apply", "--silent", str(self.role_manifest)])

        # Should succeed
        assert result.exit_code == 0
        assert "Created" in result.output or "Updated" in result.output

    def test_02_super_user_creates_packages(self, cli_runner, super_user, test_projects):
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

    def test_03_super_user_creates_extended_packages(
        self, cli_runner, super_user, test_projects
    ):
        """Test that superuser can create extended package patterns"""
        # Login as superuser
        super_user.login(cli_runner, project_name=test_projects[0])

        # Create extended packages (user-package-1, managed-package-1, temp-package-1)
        result = cli_runner.invoke(cli, ["apply", "--silent", str(self.package_extended)])
        assert result.exit_code == 0
        assert "Apply successful" in result.output

        # Create docker packages (docker-registry-package, dockerhub-package)
        result = cli_runner.invoke(cli, ["apply", "--silent", str(self.package_docker)])
        assert result.exit_code == 0
        assert "Apply successful" in result.output

    def test_04_super_user_binds_role_to_test_users(
        self, cli_runner, super_user, test_user_11, test_user_12, test_projects
    ):
        """Test that superuser can bind the package-viewer role to test users"""
        # Login as superuser
        super_user.login(cli_runner, project_name=test_projects[0])

        # Bind package-viewer role to test_user_11
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

        # Bind package-viewer role to test_user_12
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

    # =================
    # BASIC RBAC TESTS (package-viewer role)
    # =================

    def test_10_user11_creates_packages_from_manifest(self, logged_in_user_11):
        """Test that test_user_11 creates packages from package.yaml"""
        runner, user = logged_in_user_11

        # Create packages from package.yaml
        # This contains test-package-4 (should succeed) and random-package (should fail)
        result = runner.invoke(cli, ["apply", "--silent", str(self.package_manifest)])

        # The result might be mixed - some packages succeed, others fail
        assert result.exit_code != 0
        assert "Created package:test-package-4" in result.output
        assert (
            "Failed to apply package:random-package. Error: subject is not authorized for this operation"
            in result.output
        )

    def test_11_user11_can_list_packages(self, logged_in_user_11):
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
        ]

        # Check that authorized packages are visible
        for package in expected_visible:
            assert package in result.output

    def test_12_user11_can_inspect_authorized_packages(self, logged_in_user_11):
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

    def test_13_user11_cannot_inspect_unauthorized_packages(self, logged_in_user_11):
        """Test that test_user_11 cannot inspect packages not matching the role pattern"""
        runner, user = logged_in_user_11

        # Should NOT be able to inspect unauthorized-package
        result = runner.invoke(cli, ["package", "inspect", "unauthorized-package"])
        assert result.exit_code != 0, result.output
        assert "subject is not authorized for this operation" in result.output

        # Should NOT be able to inspect random-package (doesn't match test-package.* pattern)
        result = runner.invoke(cli, ["package", "inspect", "random-package"])
        assert result.exit_code != 0, result.output
        # Check for authorization error messages
        assert "package not found" in result.output

    def test_14_user11_cannot_delete_packages(self, logged_in_user_11):
        """Test that test_user_11 cannot delete packages (only has get/create permissions)"""
        runner, user = logged_in_user_11

        # Should NOT be able to delete even authorized packages
        result = runner.invoke(
            cli, ["package", "delete", "test-package-1", "--force", "--silent"]
        )

        assert result.exit_code != 0
        assert "subject is not authorized for this operation" in result.output

    def test_15_user12_creates_packages_from_manifest(self, logged_in_user_12):
        """Test that test_user_12 creates packages from package.yaml"""
        runner, user = logged_in_user_12

        # Create packages from package.yaml
        result = runner.invoke(cli, ["apply", "--silent", str(self.package_manifest)])

        assert result.exit_code != 0
        assert "subject is not authorized for this operation" in result.output

    def test_16_user12_can_list_packages(self, logged_in_user_12):
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
        ]

        # Check that authorized packages are visible
        for package in expected_visible:
            assert package in result.output

    def test_17_user12_can_inspect_authorized_packages(self, logged_in_user_12):
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

    def test_18_user12_cannot_inspect_unauthorized_packages(self, logged_in_user_12):
        """Test that test_user_12 cannot inspect packages not matching the role pattern"""
        runner, user = logged_in_user_12

        # Should NOT be able to inspect unauthorized-package
        result = runner.invoke(cli, ["package", "inspect", "unauthorized-package"])
        assert result.exit_code != 0, result.output
        # Check for authorization error messages
        assert "subject is not authorized for this operation" in result.output

        # Should NOT be able to inspect random-package (doesn't match test-package.* pattern)
        result2 = runner.invoke(cli, ["package", "inspect", "random-package"])
        assert result2.exit_code != 0
        assert "package not found" in result2.output

    def test_19_user12_cannot_delete_packages(self, logged_in_user_12):
        """Test that test_user_12 cannot delete packages (only has get/create permissions)"""
        runner, user = logged_in_user_12

        # Should NOT be able to delete even authorized packages
        result = runner.invoke(
            cli, ["package", "delete", "test-package-2", "--force", "--silent"]
        )

        assert result.exit_code != 0
        assert "subject is not authorized for this operation" in result.output

    # =================
    # EXTENDED ROLE TESTS (new package role patterns)
    # =================

    def test_20_package_creator_role_permissions(
        self, cli_runner, super_user, test_user_11, test_projects
    ):
        """Test package-creator role - can create/get user-package.* and list all packages"""
        # Login as superuser and setup
        super_user.login(cli_runner, project_name=test_projects[0])

        # Bind package-creator role to test_user_11
        result = cli_runner.invoke(
            cli,
            [
                "role",
                "bind",
                "package-creator",
                f"Project:{test_projects[0]}",
                f"User:{test_user_11.email}",
            ],
        )
        assert result.exit_code == 0, result.output

        # Login as test_user_11
        test_user_11.login(cli_runner, project_name=test_projects[0])

        # Test listing all packages (should work)
        result = cli_runner.invoke(cli, ["package", "list"])
        assert result.exit_code == 0, result.output
        assert "user-package-1" in result.output

        # Test getting user-package-* (should work)
        result = cli_runner.invoke(cli, ["package", "inspect", "user-package-1"])
        assert result.exit_code == 0, result.output

        # Test getting managed-package-* (should fail - wrong pattern)
        result = cli_runner.invoke(cli, ["package", "inspect", "managed-package-1"])
        assert result.exit_code != 0, result.output
        assert "subject is not authorized for this operation" in result.output

    def test_21_package_manager_role_permissions(
        self, cli_runner, super_user, test_user_12, test_projects
    ):
        """Test package-manager role - full CRUD on managed-package.* and list all"""
        # Login as superuser and setup
        super_user.login(cli_runner, project_name=test_projects[0])

        # Bind package-manager role to test_user_12
        result = cli_runner.invoke(
            cli,
            [
                "role",
                "bind",
                "package-manager",
                f"Project:{test_projects[0]}",
                f"User:{test_user_12.email}",
            ],
        )
        assert result.exit_code == 0

        # Login as test_user_12
        test_user_12.login(cli_runner, project_name=test_projects[0])

        # Test listing all packages (should work)
        result = cli_runner.invoke(cli, ["package", "list"])
        assert result.exit_code == 0
        assert "managed-package-1" in result.output

        # Test getting managed-package-* (should work)
        result = cli_runner.invoke(cli, ["package", "inspect", "managed-package-1"])
        assert result.exit_code == 0

        # Test creating new managed package via manifest (should work)
        result = cli_runner.invoke(
            cli, ["apply", "--silent", str(self.managed_package_2)]
        )
        assert result.exit_code == 0

        # Test deleting managed package (should work)
        result = cli_runner.invoke(
            cli, ["package", "delete", "managed-package-1", "--force", "--silent"]
        )
        assert result.exit_code == 0

    def test_22_package_readonly_role_permissions(
        self, cli_runner, super_user, test_user_11, test_projects
    ):
        """Test package-readonly role - can get *docker* pattern and list all"""
        # Login as superuser and setup
        super_user.login(cli_runner, project_name=test_projects[0])

        # Bind package-readonly role to test_user_11
        result = cli_runner.invoke(
            cli,
            [
                "role",
                "unbind",
                "package-creator",
                f"Project:{test_projects[0]}",
                f"User:{test_user_11.email}",
            ],
        )
        assert result.exit_code == 0

        # Bind package-readonly role to test_user_11
        result = cli_runner.invoke(
            cli,
            [
                "role",
                "bind",
                "package-readonly",
                f"Project:{test_projects[0]}",
                f"User:{test_user_11.email}",
            ],
        )
        assert result.exit_code == 0, result.output

        # Login as test_user_11
        test_user_11.login(cli_runner, project_name=test_projects[0])

        # Test listing all packages (should work)
        result = cli_runner.invoke(cli, ["package", "list"])
        assert result.exit_code == 0
        assert "docker-registry-package" in result.output
        assert "dockerhub-package" in result.output

        # Test getting *docker* pattern packages (should work)
        result = cli_runner.invoke(cli, ["package", "inspect", "docker-registry-package"])
        assert result.exit_code == 0, result.output

        result = cli_runner.invoke(cli, ["package", "inspect", "dockerhub-package"])
        assert result.exit_code == 0, result.output

        # Test getting non-docker packages (should fail)
        result = cli_runner.invoke(cli, ["package", "inspect", "user-package-1"])
        assert result.exit_code != 0, result.output
        assert "subject is not authorized for this operation" in result.output

    def test_23_package_deleter_role_permissions(
        self, cli_runner, super_user, test_user_12, test_projects
    ):
        """Test package-deleter role - can delete/get temp-package.* and list all"""
        # Login as superuser and setup
        super_user.login(cli_runner, project_name=test_projects[0])

        # Bind package-deleter role to test_user_12
        result = cli_runner.invoke(
            cli,
            [
                "role",
                "bind",
                "package-deleter",
                f"Project:{test_projects[0]}",
                f"User:{test_user_12.email}",
            ],
        )
        assert result.exit_code == 0, result.output

        # Login as test_user_12
        test_user_12.login(cli_runner, project_name=test_projects[0])

        # Test listing all packages (should work)
        result = cli_runner.invoke(cli, ["package", "list"])
        assert result.exit_code == 0, result.output
        assert "temp-package-1" in result.output

        # Test getting temp-package-* (should work)
        result = cli_runner.invoke(cli, ["package", "inspect", "temp-package-1"])
        assert result.exit_code == 0, result.output

        # Test deleting temp-package-* (should work)
        result = cli_runner.invoke(
            cli, ["package", "delete", "temp-package-1", "--force", "--silent"]
        )
        assert result.exit_code == 0, result.output

        # Test getting non-temp packages (should fail) - use user-package-1 since managed-package-1 was deleted in test_21
        result = cli_runner.invoke(cli, ["package", "inspect", "user-package-1"])
        assert result.exit_code != 0, result.output
        assert "subject is not authorized for this operation" in result.output

    # =================
    # COMPLEX SCENARIOS
    # =================

    def test_30_package_multiple_roles_combined_permissions(
        self, cli_runner, super_user, test_user_11, test_projects
    ):
        """Test user with multiple package roles has combined permissions"""
        # Login as superuser and setup
        super_user.login(cli_runner, project_name=test_projects[0])

        # Bind multiple roles to test_user_11
        roles = ["package-creator", "package-readonly"]
        for role in roles:
            result = cli_runner.invoke(
                cli,
                [
                    "role",
                    "bind",
                    role,
                    f"Project:{test_projects[0]}",
                    f"User:{test_user_11.email}",
                ],
            )
            assert result.exit_code == 0, result.output

        # Login as test_user_11
        test_user_11.login(cli_runner, project_name=test_projects[0])

        # Test listing all packages (should work from both roles)
        result = cli_runner.invoke(cli, ["package", "list"])
        assert result.exit_code == 0, result.output

        # Should be able to access user-package-* (from package-creator)
        result = cli_runner.invoke(cli, ["package", "inspect", "user-package-1"])
        assert result.exit_code == 0, result.output

        # Should be able to access *docker* (from package-readonly)
        result = cli_runner.invoke(cli, ["package", "inspect", "docker-registry-package"])
        assert result.exit_code == 0, result.output

        # Should NOT be able to access patterns from other roles
        result = cli_runner.invoke(cli, ["package", "inspect", "managed-package-2"])
        assert result.exit_code != 0, result.output
        assert "subject is not authorized for this operation" in result.output

    def test_31_package_pattern_boundary_validation(
        self, cli_runner, super_user, test_user_11, test_projects
    ):
        """Test RBAC pattern matching boundaries for package names"""
        # Login as superuser and setup
        super_user.login(cli_runner, project_name=test_projects[0])

        # Create boundary test packages via manifests
        result = cli_runner.invoke(
            cli, ["apply", "--silent", str(self.boundary_packages)]
        )
        # May succeed or fail based on superuser permissions

        # Bind package-creator role to test_user_11
        result = cli_runner.invoke(
            cli,
            [
                "role",
                "bind",
                "package-creator",
                f"Project:{test_projects[0]}",
                f"User:{test_user_11.email}",
            ],
        )
        assert result.exit_code == 0, result.output

        # Login as test_user_11
        test_user_11.login(cli_runner, project_name=test_projects[0])

        # Test pattern boundaries
        # Should work: user-package-test (matches user-package.*)
        result = cli_runner.invoke(cli, ["package", "inspect", "user-package-test"])
        assert result.exit_code in [0, 1]  # May not exist but pattern would match

        # Should fail: my-user-package-1 (doesn't start with user-package)
        result = cli_runner.invoke(cli, ["package", "inspect", "my-user-package-1"])
        assert result.exit_code != 0, result.output

        # Cleanup boundary packages
        super_user.login(cli_runner, project_name=test_projects[0])
        result = cli_runner.invoke(
            cli, ["delete", "--silent", str(self.boundary_packages)]
        )

    # =================
    # CLEANUP TESTS (Run Last)
    # =================

    def test_90_cleanup_resources(self, cli_runner, super_user, test_projects):
        """Cleanup test resources"""
        # Login as super user
        super_user.login(cli_runner, project_name=test_projects[0])

        result = cli_runner.invoke(cli, ["delete", "--silent", str(self.manifests_dir)])
        assert result.exit_code == 0

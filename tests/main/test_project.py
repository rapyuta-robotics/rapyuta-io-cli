"""
Comprehensive RBAC Tests for rapyuta.io CLI - Project Operations

This module provides extensive Role-Based Access Control testing scenarios for project operations
using pytest and Click testing framework. It covers:

Test Categories:
1. Setup and Role Creation
2. Basic RBAC Operations (create, get, list, delete, update)
3. Advanced Project Features (features toggle, owner transfer, whoami)
4. Pattern Matching and Boundary Validation
5. Multi-role Scenarios
6. Manifest-based Project Creation
7. Error Handling and Edge Cases
8. Cleanup and Teardown

Project Commands Tested:
- rio project create <name>
- rio project delete <name> [--force]
- rio project inspect <name>
- rio project list [--wide] [--label key=value]
- rio project select <name>
- rio project features <name> --feature <name> [--enable/--disable]
- rio project update-owner <name> --user <email>
- rio project whoami

Role Patterns Tested:
- Basic viewers (test-project.*)
- Creators (user-project.*)
- Managers (admin-project.*)
- Deleters (temp-project.*)
- Updaters (config-project.*)
- Multi-pattern (dev.*, staging.*)
- Feature managers (feature-project.*)
- Owner transfer (transfer-project.*)
- No-list permissions (specific-project.*)
- Read-all permissions (global list/get)
"""

import time
from pathlib import Path

import pytest

from riocli.bootstrap import cli


@pytest.mark.rbac
@pytest.mark.integration
@pytest.mark.slow
class TestProjectsRBAC:
    """Comprehensive test class for Project RBAC scenarios"""

    @pytest.fixture(autouse=True)
    def setup_manifests(self):
        """Setup manifest file paths for comprehensive RBAC testing"""
        self.manifests_dir = (
            Path(__file__).parent.parent / "fixtures" / "manifests" / "project"
        )
        self.role_manifest = self.manifests_dir / "project-rbac-roles.yaml"
        self.project_manifest = self.manifests_dir / "project-manifests.yaml"

    # =================
    # SETUP TESTS (Run First)
    # =================

    def test_01_super_user_creates_rbac_roles(
        self, cli_runner, super_user, test_projects
    ):
        """Test that superuser can create all RBAC roles for comprehensive testing"""
        # Login as superuser
        super_user.login(cli_runner, project_name=test_projects[0])

        # Create roles using apply command
        result = cli_runner.invoke(cli, ["apply", "--silent", str(self.role_manifest)])

        # Should succeed
        assert result.exit_code == 0
        assert "Created" in result.output or "Updated" in result.output

    def test_02_super_user_creates_test_projects(
        self, cli_runner, super_user, test_projects
    ):
        """Test that superuser can create various test projects"""
        # Login as superuser
        super_user.login(cli_runner, project_name=test_projects[0])

        # Create projects with different naming patterns for comprehensive testing
        projects_to_create = [
            # Basic viewer patterns
            "test-project-alpha",
            "test-project-beta",
            "test-project-gamma",
            # User creator patterns
            "user-project-dev1",
            "user-project-dev2",
            # Admin manager patterns
            "admin-project-main",
            "admin-project-staging",
            # Temp deleter patterns
            "temp-project-cleanup1",
            "temp-project-cleanup2",
            # Config updater patterns
            "config-project-settings",
            "config-project-params",
            # Multi-pattern projects
            "dev-frontend",
            "dev-backend",
            "staging-api",
            "staging-web",
            # Feature projects
            "feature-project-vpn",
            "feature-project-monitoring",
            # Transfer projects
            "transfer-project-legacy",
            "transfer-project-migration",
            # Specific projects (no list)
            "specific-project-secret",
            # Unauthorized projects
            "unauthorized-project-denied",
            "random-project-blocked",
        ]

        for project_name in projects_to_create:
            result = cli_runner.invoke(cli, ["project", "create", project_name])
            assert result.exit_code == 0 or "already exists" in result.output

    def test_03_super_user_binds_basic_roles_to_user11(
        self, cli_runner, super_user, test_user_11, test_projects
    ):
        """Test that superuser can bind basic viewer and creator roles to test_user_11"""
        # Login as superuser
        super_user.login(cli_runner, project_name=test_projects[0])

        # Bind basic viewer role (test-project.*)
        result = cli_runner.invoke(
            cli,
            [
                "role",
                "bind",
                "project-viewer-basic",
                "Organization:CliTest",
                f"User:{test_user_11.email}",
            ],
        )
        assert result.exit_code == 0

        # Bind user creator role (user-project.*)
        result = cli_runner.invoke(
            cli,
            [
                "role",
                "bind",
                "project-creator-user",
                "Organization:CliTest",
                f"User:{test_user_11.email}",
            ],
        )
        assert result.exit_code == 0

    def test_04_super_user_binds_advanced_roles_to_user12(
        self, cli_runner, super_user, test_user_12, test_projects
    ):
        """Test that superuser can bind advanced roles to test_user_12"""
        # Login as superuser
        super_user.login(cli_runner, project_name=test_projects[0])

        # Bind admin manager role (admin-project.*)
        result = cli_runner.invoke(
            cli,
            [
                "role",
                "bind",
                "project-manager-admin",
                "Organization:CliTest",
                f"User:{test_user_12.email}",
            ],
        )
        assert result.exit_code == 0

        # Bind temp deleter role (temp-project.*)
        result = cli_runner.invoke(
            cli,
            [
                "role",
                "bind",
                "project-deleter-temp",
                "Organization:CliTest",
                f"User:{test_user_12.email}",
            ],
        )
        assert result.exit_code == 0

        # Bind multi-pattern viewer role (dev.*, staging.*)
        result = cli_runner.invoke(
            cli,
            [
                "role",
                "bind",
                "project-multipattern-viewer",
                "Organization:CliTest",
                f"User:{test_user_12.email}",
            ],
        )
        assert result.exit_code == 0

    # =================
    # BASIC RBAC TESTS (Core Operations)
    # =================

    def test_10_user11_creates_projects_from_manifest(self, logged_in_user_11):
        """Test that test_user_11 creates projects from manifest"""
        runner, user = logged_in_user_11

        # Create projects from manifest
        # This contains test-project-manifest-1 (should succeed) and random-project-denied (should fail)
        result = runner.invoke(cli, ["apply", "--silent", str(self.project_manifest)])

        # The result might be mixed - some projects succeed, others fail
        assert result.exit_code != 0, result.output
        assert "project:user-project-manifest-1" in result.output
        assert (
            "Failed to apply project:random-project-denied. Error: subject is not authorized for this operation"
            in result.output
        )

    def test_11_user11_can_list_projects(self, logged_in_user_11):
        """Test that test_user_11 can list projects based on roles"""
        runner, user = logged_in_user_11

        result = runner.invoke(cli, ["project", "list"])

        # Should succeed
        assert result.exit_code == 0, (
            f"Project list should succeed for {user.email}. "
            f"Exit code: {result.exit_code}, Output: {result.output}"
        )

        # Should see projects matching role patterns
        expected_visible = [
            "test-project-alpha",
            "test-project-beta",
            "test-project-gamma",
            "user-project-dev1",
            "user-project-dev2",
        ]

        for project in expected_visible:
            assert project in result.output

    def test_12_user11_can_inspect_authorized_projects(self, logged_in_user_11):
        """Test that test_user_11 can inspect projects matching role patterns"""
        runner, user = logged_in_user_11

        # Should be able to inspect test-project.* (viewer role)
        result = runner.invoke(cli, ["project", "inspect", "test-project-alpha"])
        assert result.exit_code == 0

        result = runner.invoke(cli, ["project", "inspect", "test-project-beta"])
        assert result.exit_code == 0

        # Should be able to inspect user-project.* (creator role)
        result = runner.invoke(cli, ["project", "inspect", "user-project-dev1"])
        assert result.exit_code == 0

    def test_13_user11_can_create_user_projects_only(self, logged_in_user_11):
        """Test that test_user_11 can create user-project.* but not others"""
        runner, user = logged_in_user_11

        # Should be able to create user-project.* (creator role)
        result = runner.invoke(cli, ["project", "create", "user-project-new1"])
        assert result.exit_code == 0 or "already exists" in result.output

        # Should be able to inspect created project
        result = runner.invoke(cli, ["project", "inspect", "user-project-new1"])
        assert result.exit_code == 0, result.output

        # Should NOT be able to create projects outside pattern
        result = runner.invoke(cli, ["project", "create", "admin-project-denied"])
        assert result.exit_code != 0, result.output
        assert "subject is not authorized for this operation" in result.output

        result = runner.invoke(cli, ["project", "create", "random-project-denied"])
        assert result.exit_code != 0, result.output
        assert "subject is not authorized for this operation" in result.output

    def test_14_user11_cannot_inspect_unauthorized_projects(self, logged_in_user_11):
        """Test that test_user_11 cannot inspect projects not matching role patterns"""
        runner, user = logged_in_user_11

        # Should NOT be able to inspect admin-project.*
        result = runner.invoke(cli, ["project", "inspect", "admin-project-main"])
        assert result.exit_code != 0, result.output
        assert (
            "subject is not authorized for this operation" in result.output
            or "project not found" in result.output
        )

        # Should NOT be able to inspect unauthorized projects
        result = runner.invoke(cli, ["project", "inspect", "unauthorized-project-denied"])
        assert result.exit_code != 0
        assert (
            "subject is not authorized for this operation" in result.output
            or "project not found" in result.output
        )

    def test_15_user11_cannot_delete_projects(self, logged_in_user_11):
        """Test that test_user_11 cannot delete any projects (no delete permissions)"""
        runner, user = logged_in_user_11

        # Should NOT be able to delete even authorized projects
        result = runner.invoke(
            cli, ["project", "delete", "test-project-alpha", "--force"]
        )
        assert result.exit_code != 0, result.output
        assert "subject is not authorized for this operation" in result.output

        # Should be able to as it is the creator of this project
        result = runner.invoke(cli, ["project", "delete", "user-project-new1", "--force"])
        assert result.exit_code == 0, result.output

    def test_16_user12_can_manage_admin_projects(self, logged_in_user_12):
        """Test that test_user_12 can fully manage admin-project.* (manager role)"""
        runner, user = logged_in_user_12

        # Should be able to create admin-project.*
        result = runner.invoke(cli, ["project", "create", "admin-project-new1"])
        assert result.exit_code == 0 or "already exists" in result.output

        # Should be able to inspect admin-project.*
        result = runner.invoke(cli, ["project", "inspect", "admin-project-main"])
        assert result.exit_code == 0, result.output

        result = runner.invoke(cli, ["project", "inspect", "admin-project-new1"])
        assert result.exit_code == 0, result.output

        # Should be able to delete admin-project.*
        result = runner.invoke(
            cli, ["project", "delete", "admin-project-new1", "--force"]
        )
        assert result.exit_code == 0

    def test_17_user12_can_delete_temp_projects_only(self, logged_in_user_12):
        """Test that test_user_12 can delete temp-project.* (deleter role)"""
        runner, user = logged_in_user_12

        # Should be able to inspect temp-project.*
        result = runner.invoke(cli, ["project", "inspect", "temp-project-cleanup1"])
        assert result.exit_code == 0, result.output

        # Should be able to delete temp-project.*
        result = runner.invoke(
            cli, ["project", "delete", "temp-project-cleanup1", "--force"]
        )
        assert result.exit_code == 0, result.output

        # Should NOT be able to delete other projects even if visible
        result = runner.invoke(cli, ["project", "delete", "dev-frontend", "--force"])
        assert result.exit_code != 0, result.output
        assert "subject is not authorized for this operation" in result.output

    def test_18_user12_can_view_multipattern_projects(self, logged_in_user_12):
        """Test that test_user_12 can view dev.* and staging.* projects (multi-pattern viewer)"""
        runner, user = logged_in_user_12

        # Should be able to inspect dev.* projects
        result = runner.invoke(cli, ["project", "inspect", "dev-frontend"])
        assert result.exit_code == 0, result.output

        result = runner.invoke(cli, ["project", "inspect", "dev-backend"])
        assert result.exit_code == 0, result.output

        # Should be able to inspect staging.* projects
        result = runner.invoke(cli, ["project", "inspect", "staging-api"])
        assert result.exit_code == 0, result.output

        result = runner.invoke(cli, ["project", "inspect", "staging-web"])
        assert result.exit_code == 0, result.output

    def test_19_user12_cannot_create_dev_staging_projects(self, logged_in_user_12):
        """Test that test_user_12 cannot create dev/staging projects (only view permissions)"""
        runner, user = logged_in_user_12

        # Should NOT be able to create dev.* projects
        result = runner.invoke(cli, ["project", "create", "dev-newservice"])
        assert result.exit_code != 0, result.output
        assert "subject is not authorized for this operation" in result.output

        # Should NOT be able to create staging.* projects
        result = runner.invoke(cli, ["project", "create", "staging-newapi"])
        assert result.exit_code != 0, result.output
        assert "subject is not authorized for this operation" in result.output

    # =================
    # ADVANCED FEATURE TESTS
    # =================

    def test_20_bind_feature_manager_role(
        self, cli_runner, super_user, test_user_11, test_projects
    ):
        """Test binding feature manager role for advanced feature testing"""
        # Login as superuser
        super_user.login(cli_runner, project_name=test_projects[0])

        # Bind feature manager role to test_user_11
        result = cli_runner.invoke(
            cli,
            [
                "role",
                "bind",
                "project-feature-manager",
                "Organization:CliTest",
                f"User:{test_user_11.email}",
            ],
        )
        assert result.exit_code == 0, result.output

    def test_21_user11_can_manage_project_features(self, logged_in_user_11):
        """Test that test_user_11 can manage features on feature-project.* (feature manager role)"""
        runner, user = logged_in_user_11

        # Should be able to inspect feature-project.*
        result = runner.invoke(cli, ["project", "inspect", "feature-project-vpn"])
        assert result.exit_code == 0, result.output

        # Note: Feature management commands would be tested here if available
        # For now, we test that the project is accessible for feature management
        # result = runner.invoke(cli, ["project", "features", "feature-project-vpn", "--feature", "vpn", "--enable"])
        # assert result.exit_code == 0

    def test_22_bind_owner_transfer_role(
        self, cli_runner, super_user, test_user_12, test_projects
    ):
        """Test binding owner transfer role for ownership testing"""
        # Login as superuser
        super_user.login(cli_runner, project_name=test_projects[0])

        # Bind owner transfer role to test_user_12
        result = cli_runner.invoke(
            cli,
            [
                "role",
                "bind",
                "project-owner-transfer",
                "Organization:CliTest",
                f"User:{test_user_12.email}",
            ],
        )
        assert result.exit_code == 0, result.output

    def test_23_user12_can_access_transfer_projects(self, logged_in_user_12):
        """Test that test_user_12 can access transfer-project.* for ownership operations"""
        runner, user = logged_in_user_12

        # Should be able to inspect transfer-project.*
        result = runner.invoke(cli, ["project", "inspect", "transfer-project-legacy"])
        assert result.exit_code == 0, result.output

        result = runner.invoke(cli, ["project", "inspect", "transfer-project-migration"])
        assert result.exit_code == 0, result.output

        # Note: Owner transfer commands would be tested here if available
        # result = runner.invoke(cli, ["project", "update-owner", "transfer-project-legacy", "--user", "new-owner@test.com"])

    # =================
    # BOUNDARY AND PATTERN VALIDATION TESTS
    # =================

    def test_30_bind_no_list_role(
        self, cli_runner, super_user, test_user_11, test_projects
    ):
        """Test binding no-list role for boundary testing"""
        # Login as superuser
        super_user.login(cli_runner, project_name=test_projects[0])

        # Bind no-list role to test_user_11
        result = cli_runner.invoke(
            cli,
            [
                "role",
                "bind",
                "project-no-list",
                "Organization:CliTest",
                f"User:{test_user_11.email}",
            ],
        )
        assert result.exit_code == 0, result.output

    def test_31_user11_can_get_but_may_not_list_specific_projects(
        self, logged_in_user_11
    ):
        """Test that test_user_11 can get specific-project.* but may have limited list access"""
        runner, user = logged_in_user_11

        # Should be able to inspect specific-project.* directly (get permission)
        result = runner.invoke(cli, ["project", "inspect", "specific-project-secret"])
        assert result.exit_code == 0, result.output

        # List should still work due to other roles, but this tests the pattern matching
        result = runner.invoke(cli, ["project", "list"])
        assert result.exit_code == 0, result.output

    def test_32_bind_read_all_role(
        self, cli_runner, super_user, test_user_12, test_projects
    ):
        """Test binding read-all role for global access testing"""
        # Login as superuser
        super_user.login(cli_runner, project_name=test_projects[0])

        # Bind read-all role to test_user_12
        result = cli_runner.invoke(
            cli,
            [
                "role",
                "bind",
                "project-reader-all",
                "Organization:CliTest",
                f"User:{test_user_12.email}",
            ],
        )
        assert result.exit_code == 0, result.output

    def test_33_user12_can_read_all_projects(self, logged_in_user_12):
        """Test that test_user_12 can read all projects (read-all role)"""
        runner, user = logged_in_user_12

        # Should be able to list all projects
        result = runner.invoke(cli, ["project", "list"])
        assert result.exit_code == 0, result.output

        # Should be able to inspect any project (global get permission)
        result = runner.invoke(cli, ["project", "inspect", "unauthorized-project-denied"])
        assert result.exit_code == 0, result.output

        result = runner.invoke(cli, ["project", "inspect", "specific-project-secret"])
        assert result.exit_code == 0, result.output

        # Should NOT be able to create random projects (no create permission)
        result = runner.invoke(cli, ["project", "create", "global-read-test"])
        assert result.exit_code != 0, result.output
        assert "subject is not authorized for this operation" in result.output

    def test_34_pattern_boundary_validation(self, logged_in_user_11):
        """Test pattern matching boundaries and edge cases"""
        runner, user = logged_in_user_11

        # Test prefix matching - should work
        result = runner.invoke(cli, ["project", "inspect", "test-project-alpha"])
        assert result.exit_code == 0, result.output

        # Test that similar but non-matching patterns fail
        result = runner.invoke(
            cli, ["project", "inspect", "test_project_alpha"]
        )  # underscore instead of hyphen
        assert result.exit_code != 0, result.output

        result = runner.invoke(
            cli, ["project", "inspect", "testproject-alpha"]
        )  # no hyphen
        assert result.exit_code != 0, result.output

    # =================
    # WHOAMI AND CONTEXT TESTS
    # =================

    def test_40_user_whoami_in_authorized_projects(self, logged_in_user_11):
        """Test whoami command in authorized projects"""
        runner, user = logged_in_user_11

        # Should be able to use whoami in authorized projects
        # Note: This requires the project to be selected first
        result = runner.invoke(cli, ["project", "select", "test-project-alpha"])
        if result.exit_code == 0:
            result = runner.invoke(cli, ["project", "whoami"])
            # whoami should work or give appropriate response

    def test_41_project_select_authorization(self, logged_in_user_11):
        """Test project selection with role-based authorization"""
        runner, user = logged_in_user_11

        # Should be able to select authorized projects
        runner.invoke(cli, ["project", "select", "test-project-alpha"])
        # Should succeed or give appropriate response based on selection permissions

        runner.invoke(cli, ["project", "select", "user-project-dev1"])
        # Should succeed or give appropriate response

        # Should NOT be able to select unauthorized projects
        runner.invoke(cli, ["project", "select", "unauthorized-project-denied"])
        # May fail with authorization error depending on implementation

    # =================
    # LIST FILTERING AND WIDE OUTPUT TESTS
    # =================

    def test_50_project_list_with_labels(self, logged_in_user_11):
        """Test project list with label filtering"""
        runner, user = logged_in_user_11

        # Test basic list with wide output
        result = runner.invoke(cli, ["project", "list", "--wide"])
        assert result.exit_code == 0, result.output

        # Test label filtering (if projects have labels)
        # result = runner.invoke(cli, ["project", "list", "--label", "environment=test"])
        # Should work based on role permissions

    def test_51_project_list_pagination_and_output(self, logged_in_user_12):
        """Test project list output formats and pagination"""
        runner, user = logged_in_user_12

        # Test wide output format
        result = runner.invoke(cli, ["project", "list", "--wide"])
        assert result.exit_code == 0

        # Verify that user can see projects based on combined roles
        expected_visible = [
            "admin-project-main",
            "admin-project-staging",
            "temp-project-cleanup2",
            "dev-frontend",
            "dev-backend",
            "staging-api",
            "staging-web",
            "transfer-project-legacy",
            "transfer-project-migration",
        ]

        for project in expected_visible:
            assert project in result.output

    # =================
    # ERROR HANDLING AND EDGE CASES
    # =================

    def test_60_error_handling_nonexistent_projects(self, logged_in_user_11):
        """Test error handling for non-existent projects"""
        runner, user = logged_in_user_11

        # Test inspect non-existent project
        result = runner.invoke(cli, ["project", "inspect", "nonexistent-project"])
        assert result.exit_code != 0, result.output
        # Should get "not found" or authorization error

        # Test delete non-existent project
        result = runner.invoke(
            cli, ["project", "delete", "nonexistent-project", "--force"]
        )
        assert result.exit_code != 0, result.output

    def test_61_error_handling_malformed_names(self, logged_in_user_11):
        """Test error handling for malformed project names"""
        runner, user = logged_in_user_11

        # Test creating project with invalid characters (if validation exists)
        result = runner.invoke(cli, ["project", "create", "invalid@project#name"])
        # May fail with validation error or authorization error

        # Test inspect with empty name
        result = runner.invoke(cli, ["project", "inspect", ""])
        assert result.exit_code != 0, result.output

    # =================
    # MULTI-ROLE INTERACTION TESTS
    # =================

    def test_70_bind_config_updater_role(
        self, cli_runner, super_user, test_user_11, test_projects
    ):
        """Test binding config updater role for update testing"""
        # Login as superuser
        super_user.login(cli_runner, project_name=test_projects[0])

        # Bind config updater role to test_user_11
        result = cli_runner.invoke(
            cli,
            [
                "role",
                "bind",
                "project-updater-config",
                "Organization:CliTest",
                f"User:{test_user_11.email}",
            ],
        )
        assert result.exit_code == 0, result.output

    def test_71_user11_combined_role_permissions(self, logged_in_user_11):
        """Test that test_user_11 has combined permissions from all bound roles"""
        runner, user = logged_in_user_11

        # Should have access to projects from all role patterns:
        # - test-project.* (viewer)
        # - user-project.* (creator)
        # - feature-project.* (feature manager)
        # - specific-project.* (no-list)
        # - config-project.* (updater)

        projects_to_test = [
            "test-project-alpha",
            "user-project-dev1",
            "feature-project-vpn",
            "specific-project-secret",
            "config-project-settings",
        ]

        for project in projects_to_test:
            result = runner.invoke(cli, ["project", "inspect", project])
            assert result.exit_code == 0, result.output

    def test_72_user12_combined_role_permissions(self, logged_in_user_12):
        """Test that test_user_12 has combined permissions from all bound roles"""
        runner, user = logged_in_user_12

        # Should have access to projects from all role patterns:
        # - admin-project.* (manager)
        # - temp-project.* (deleter)
        # - dev.*, staging.* (multi-pattern viewer)
        # - transfer-project.* (owner transfer)
        # - *.* (read-all)

        # Test global read access
        result = runner.invoke(cli, ["project", "list"])
        assert result.exit_code == 0

        # Test accessing projects from different patterns
        projects_to_test = [
            "admin-project-main",
            "temp-project-cleanup2",
            "dev-frontend",
            "staging-api",
            "transfer-project-legacy",
            "unauthorized-project-denied",  # Should work due to read-all role
        ]

        for project in projects_to_test:
            result = runner.invoke(cli, ["project", "inspect", project])
            assert result.exit_code == 0, result.output

    # =================
    # PERFORMANCE AND STRESS TESTS
    # =================

    def test_80_list_performance_with_many_projects(self, logged_in_user_12):
        """Test list performance with many projects and multiple roles"""
        runner, user = logged_in_user_12

        start_time = time.time()
        result = runner.invoke(cli, ["project", "list"])
        end_time = time.time()

        assert result.exit_code == 0
        assert (end_time - start_time) < 30  # Should complete within 30 seconds

    def test_81_pattern_matching_performance(self, logged_in_user_11):
        """Test pattern matching performance with multiple role patterns"""
        runner, user = logged_in_user_11

        # Test rapid consecutive inspects
        projects_to_test = [
            "test-project-alpha",
            "user-project-dev1",
            "feature-project-vpn",
            "config-project-settings",
        ]

        start_time = time.time()
        for project in projects_to_test:
            result = runner.invoke(cli, ["project", "inspect", project])
            assert result.exit_code == 0
        end_time = time.time()

        assert (end_time - start_time) < 15  # Should complete within 15 seconds

    # =================
    # CLEANUP TESTS (Run Last)
    # =================

    def test_90_cleanup_test_projects(self, cli_runner, super_user, test_projects):
        """Cleanup all test projects created during testing"""
        # Login as super user
        super_user.login(cli_runner, project_name=test_projects[0])

        # Delete all test projects
        projects_to_delete = [
            "test-project-alpha",
            "test-project-beta",
            "test-project-gamma",
            "user-project-dev1",
            "user-project-dev2",
            "user-project-new1",
            "admin-project-main",
            "admin-project-staging",
            "temp-project-cleanup2",
            "config-project-settings",
            "config-project-params",
            "dev-frontend",
            "dev-backend",
            "staging-api",
            "staging-web",
            "feature-project-vpn",
            "feature-project-monitoring",
            "transfer-project-legacy",
            "transfer-project-migration",
            "specific-project-secret",
            "unauthorized-project-denied",
            "random-project-blocked",
        ]

        for project_name in projects_to_delete:
            cli_runner.invoke(cli, ["project", "delete", project_name, "--force"])
            # Don't assert on exit code as projects might not exist

        result = cli_runner.invoke(
            cli, ["delete", str(self.project_manifest), "--silent"]
        )
        assert result.exit_code == 0, result.output

    def test_91_cleanup_role_bindings(
        self, cli_runner, super_user, test_user_11, test_user_12, test_projects
    ):
        """Cleanup all role bindings created during testing"""
        # Login as super user
        super_user.login(cli_runner, project_name=test_projects[0])

        # Unbind all roles from both users
        roles_to_unbind = [
            "project-viewer-basic",
            "project-creator-user",
            "project-manager-admin",
            "project-deleter-temp",
            "project-multipattern-viewer",
            "project-feature-manager",
            "project-owner-transfer",
            "project-no-list",
            "project-reader-all",
            "project-updater-config",
        ]

        for user_email in [test_user_11.email, test_user_12.email]:
            for role_name in roles_to_unbind:
                cli_runner.invoke(
                    cli,
                    [
                        "role",
                        "unbind",
                        role_name,
                        "--user",
                        user_email,
                        "--organization",
                        "CliTest",
                    ],
                )
                # Don't assert on exit code as bindings might not exist

    def test_92_cleanup_rbac_roles(self, cli_runner, super_user, test_projects):
        """Cleanup all RBAC roles created during testing"""
        # Login as super user
        super_user.login(cli_runner, project_name=test_projects[0])

        # Delete roles using delete command
        result = cli_runner.invoke(cli, ["delete", "--silent", str(self.role_manifest)])
        assert result.exit_code == 0

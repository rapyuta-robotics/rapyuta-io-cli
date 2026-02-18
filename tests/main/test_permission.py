# Copyright 2025 Rapyuta Robotics
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
Permission Command Tests for rapyuta.io CLI.

This module tests the permission command functionality including:
- Permission inspection (rio permission inspect)
- Permission checking (rio permission check)

Test Categories:
1. Setup and Role Creation
2. Permission Inspect Command Tests
3. Permission Check Command Tests - Organization Level
4. Permission Check Command Tests - Project Level
5. Permission Check Command Tests - Default (Current Project)
6. Permission Check Command Tests - Instance Patterns
7. Service Account Permission Tests
8. Error Handling and Edge Cases
9. Cleanup

Permission Commands Tested:
- rio permission inspect
- rio permission check <resource> <action> [--domain] [--instance]

Scenarios Covered:
- Inspecting user permissions at org and project levels
- Checking permissions with explicit domain (Organization/Project)
- Checking permissions in default project from config
- Checking permissions with instance patterns (regex)
- Validating authorized and unauthorized access
- Service account permission inspection and checking
- Error handling for invalid domains and missing projects
"""

from pathlib import Path

import pytest

from riocli.bootstrap import cli


@pytest.mark.rbac
@pytest.mark.integration
@pytest.mark.slow
class TestPermissionCommands:
    """Comprehensive test class for Permission command scenarios"""

    @pytest.fixture(autouse=True)
    def setup_manifests(self):
        """Setup manifest file paths for permission testing"""
        self.manifests_dir = (
            Path(__file__).parent.parent / "fixtures" / "manifests" / "permission"
        )
        self.role_manifest = self.manifests_dir / "permission-test-roles.yaml"
        self.secret_manifest = self.manifests_dir / "permission-test-secrets.yaml"

    # =================
    # SETUP TESTS (Run First)
    # =================

    def test_01_super_user_creates_roles(self, cli_runner, super_user, test_projects):
        """Test that superuser can create RBAC roles for permission testing"""
        # Login as superuser
        super_user.login(cli_runner, project_name=test_projects[0])

        # Create roles using apply command
        result = cli_runner.invoke(cli, ["apply", "--silent", str(self.role_manifest)])

        # Should succeed
        assert result.exit_code == 0
        assert "Created" in result.output or "Updated" in result.output

    def test_02_super_user_creates_test_secrets(
        self, cli_runner, super_user, test_projects
    ):
        """Test that superuser can create test secrets for permission testing"""
        # Login as superuser
        super_user.login(cli_runner, project_name=test_projects[0])

        # Create secrets
        result = cli_runner.invoke(cli, ["apply", "--silent", str(self.secret_manifest)])

        # Should succeed - super user should be able to create all secrets
        assert result.exit_code == 0
        # Verify secrets were created (check for at least some of them)
        assert (
            "secret:perm-secret-001" in result.output
            or "perm-secret-001" in result.output
        )

    def test_03_super_user_binds_roles_to_test_users(
        self,
        cli_runner,
        super_user,
        test_projects,
        test_user_11_email,
        test_user_12_email,
    ):
        """Bind roles to test users for permission testing"""
        # Login as superuser
        super_user.login(cli_runner, project_name=test_projects[0])

        # Bind permission-viewer role to test_user_11 at project level
        result = cli_runner.invoke(
            cli,
            [
                "role",
                "bind",
                "permission-viewer",
                f"Project:{test_projects[0]}",
                f"User:{test_user_11_email}",
            ],
        )
        assert result.exit_code == 0

        # Bind permission-manager role to test_user_12 at project level
        result = cli_runner.invoke(
            cli,
            [
                "role",
                "bind",
                "permission-manager",
                f"Project:{test_projects[0]}",
                f"User:{test_user_12_email}",
            ],
        )
        assert result.exit_code == 0

        # Bind org-level viewer role to test_user_11
        result = cli_runner.invoke(
            cli,
            [
                "role",
                "bind",
                "org-device-viewer",
                "Organization:CliTest",
                f"User:{test_user_11_email}",
            ],
        )
        assert result.exit_code == 0

    # =================
    # PERMISSION INSPECT TESTS
    # =================

    def test_10_user11_can_inspect_own_permissions(self, logged_in_user_11):
        """Test that user11 can inspect their own permissions"""
        runner, user = logged_in_user_11

        result = runner.invoke(cli, ["permission", "inspect"])

        # Should succeed
        assert result.exit_code == 0
        # Should contain JSON output with organization and projects keys
        assert '"organization"' in result.output or '"projects"' in result.output

    def test_11_user12_can_inspect_own_permissions(self, logged_in_user_12):
        """Test that user12 can inspect their own permissions"""
        runner, user = logged_in_user_12

        result = runner.invoke(cli, ["permission", "inspect"])

        # Should succeed
        assert result.exit_code == 0
        # Should contain JSON output
        assert '"organization"' in result.output or '"projects"' in result.output

    def test_12_super_user_can_inspect_permissions(
        self, cli_runner, super_user, test_projects
    ):
        """Test that super user can inspect their own permissions"""
        super_user.login(cli_runner, project_name=test_projects[0])

        result = cli_runner.invoke(cli, ["permission", "inspect"])

        # Should succeed
        assert result.exit_code == 0
        # Super user should have extensive permissions
        assert '"organization"' in result.output
        assert '"projects"' in result.output

    # =================
    # PERMISSION CHECK - ORGANIZATION LEVEL
    # =================

    def test_20_user11_check_org_device_permission_authorized(self, logged_in_user_11):
        """Test user11 checking authorized org-level device permission"""
        runner, user = logged_in_user_11

        # User11 has org-device-viewer role, should be able to get devices matching pattern
        result = runner.invoke(
            cli,
            [
                "permission",
                "check",
                "device",
                "get_device",
                "-d",
                "Organization:CliTest",
                "-i",
                "device-test-001",
            ],
        )

        # Should be authorized
        assert result.exit_code == 0
        assert "Authorized" in result.output
        assert "organization level" in result.output

    def test_21_user11_check_org_device_permission_default_instance(
        self, logged_in_user_11
    ):
        """Test user11 checking org-level device permission with default instance pattern"""
        runner, user = logged_in_user_11

        # Without --instance flag, should use default .* pattern
        result = runner.invoke(
            cli,
            [
                "permission",
                "check",
                "device",
                "get_device",
                "-d",
                "Organization:CliTest",
            ],
        )

        # Should be authorized for any device (pattern .*)
        assert result.exit_code == 0
        assert "Authorized" in result.output

    def test_22_user12_check_org_device_permission_unauthorized(self, logged_in_user_12):
        """Test user12 checking unauthorized org-level device permission"""
        runner, user = logged_in_user_12

        # User12 does not have org-device-viewer role
        result = runner.invoke(
            cli,
            [
                "permission",
                "check",
                "device",
                "get_device",
                "-d",
                "Organization:CliTest",
            ],
        )

        # Should be unauthorized
        assert result.exit_code != 0
        assert "Unauthorized" in result.output

    def test_23_user11_check_invalid_org_name(self, logged_in_user_11):
        """Test checking permission with invalid organization name"""
        runner, user = logged_in_user_11

        # Try to check permission in a different org (should fail validation)
        result = runner.invoke(
            cli,
            [
                "permission",
                "check",
                "device",
                "get_device",
                "-d",
                "Organization:WrongOrg",
            ],
        )

        # Should fail with validation error
        assert result.exit_code != 0
        assert "does not match" in result.output

    # =================
    # PERMISSION CHECK - PROJECT LEVEL
    # =================

    def test_30_user11_check_project_secret_permission_authorized(
        self, logged_in_user_11
    ):
        """Test user11 checking authorized project-level secret permission"""
        runner, user = logged_in_user_11

        # User11 has permission-viewer role at project level
        result = runner.invoke(
            cli,
            [
                "permission",
                "check",
                "secret",
                "get",
                "-d",
                "Project:test-project1",
                "-i",
                "perm-secret-001",
            ],
        )

        # Should be authorized
        assert result.exit_code == 0
        assert "Authorized" in result.output

    def test_31_user12_check_project_secret_permission_authorized(
        self, logged_in_user_12
    ):
        """Test user12 checking authorized project-level secret permission"""
        runner, user = logged_in_user_12

        # User12 has permission-manager role at project level
        result = runner.invoke(
            cli,
            [
                "permission",
                "check",
                "secret",
                "create",
                "-d",
                "Project:test-project1",
                "-i",
                "managed-secret-001",
            ],
        )

        # Should be authorized
        assert result.exit_code == 0
        assert "Authorized" in result.output

    def test_32_user11_check_project_secret_create_unauthorized(self, logged_in_user_11):
        """Test user11 checking unauthorized create action (viewer role only)"""
        runner, user = logged_in_user_11

        # User11 has viewer role, cannot create
        result = runner.invoke(
            cli,
            [
                "permission",
                "check",
                "secret",
                "create",
                "-d",
                "Project:test-project1",
            ],
        )

        # Should be unauthorized
        assert result.exit_code != 0
        assert "Unauthorized" in result.output

    def test_33_user12_check_project_secret_delete_authorized(self, logged_in_user_12):
        """Test user12 checking authorized delete action (manager role)"""
        runner, user = logged_in_user_12

        # User12 has manager role, can delete
        result = runner.invoke(
            cli,
            [
                "permission",
                "check",
                "secret",
                "delete",
                "-d",
                "Project:test-project1",
                "-i",
                "managed-secret-002",
            ],
        )

        # Should be authorized
        assert result.exit_code == 0
        assert "Authorized" in result.output

    def test_34_user11_check_nonexistent_project(self, logged_in_user_11):
        """Test checking permission in a non-existent project"""
        runner, user = logged_in_user_11

        # Try to check permission in non-existent project
        result = runner.invoke(
            cli,
            [
                "permission",
                "check",
                "secret",
                "get",
                "-d",
                "Project:nonexistent-project",
            ],
        )

        # Should fail
        assert result.exit_code != 0
        assert "Failed to find project" in result.output

    # =================
    # PERMISSION CHECK - DEFAULT PROJECT (NO DOMAIN FLAG)
    # =================

    def test_40_user11_check_permission_in_current_project(self, logged_in_user_11):
        """Test user11 checking permission without domain flag (uses current project)"""
        runner, user = logged_in_user_11

        # Should check in current project from config (test-project1)
        result = runner.invoke(
            cli,
            [
                "permission",
                "check",
                "secret",
                "get",
                "-i",
                "perm-secret-002",
            ],
        )

        # Should be authorized in current project
        assert result.exit_code == 0
        assert "Authorized" in result.output
        assert (
            "Project:test-project1" in result.output or "project level" in result.output
        )

    def test_41_user12_check_permission_in_current_project(self, logged_in_user_12):
        """Test user12 checking permission without domain flag"""
        runner, user = logged_in_user_12

        # Should check in current project - use instance that matches manager role pattern
        result = runner.invoke(
            cli,
            [
                "permission",
                "check",
                "secret",
                "update",
                "-i",
                "managed-secret-003",
            ],
        )

        # Should be authorized
        assert result.exit_code == 0
        assert "Authorized" in result.output

    def test_42_user11_check_org_permission_inherited_in_project(self, logged_in_user_11):
        """Test that org-level permissions are checked when using default project"""
        runner, user = logged_in_user_11

        # User11 has org-level device viewer permission
        # When checking in project context, should also check org level
        result = runner.invoke(
            cli,
            [
                "permission",
                "check",
                "device",
                "get_device",
                "-i",
                "device-org-001",
            ],
        )

        # Should be authorized (may be found at either org or project level due to inheritance)
        assert result.exit_code == 0
        assert "Authorized" in result.output

    # =================
    # PERMISSION CHECK - INSTANCE PATTERNS
    # =================

    def test_50_user11_check_permission_with_pattern_match(self, logged_in_user_11):
        """Test permission check with instance pattern that matches"""
        runner, user = logged_in_user_11

        # Assuming user11 has permission for pattern ^perm-secret.*
        result = runner.invoke(
            cli,
            [
                "permission",
                "check",
                "secret",
                "get",
                "-d",
                "Project:test-project1",
                "-i",
                "perm-secret-123",
            ],
        )

        # Should be authorized if pattern matches
        assert result.exit_code == 0
        assert "Authorized" in result.output

    def test_51_user11_check_permission_with_pattern_mismatch(self, logged_in_user_11):
        """Test permission check with instance pattern that doesn't match"""
        runner, user = logged_in_user_11

        # Instance doesn't match user11's allowed patterns
        result = runner.invoke(
            cli,
            [
                "permission",
                "check",
                "secret",
                "get",
                "-d",
                "Project:test-project1",
                "-i",
                "unauthorized-secret-001",
            ],
        )

        # Should be unauthorized
        assert result.exit_code != 0
        assert "Unauthorized" in result.output

    def test_52_user12_check_permission_with_wildcard_pattern(self, logged_in_user_12):
        """Test permission check with instance pattern for list action"""
        runner, user = logged_in_user_12

        # User12 manager role has list action for managed-secret.* instances
        result = runner.invoke(
            cli,
            [
                "permission",
                "check",
                "secret",
                "list",
                "-d",
                "Project:test-project1",
                "-i",
                "managed-secret-001",
            ],
        )

        # Should be authorized for list action with matching instance
        assert result.exit_code == 0
        assert "Authorized" in result.output

    def test_53_user11_check_permission_with_regex_pattern(self, logged_in_user_11):
        """Test permission check with complex regex pattern"""
        runner, user = logged_in_user_11

        # Test with pattern like ^(perm|test)-secret-[0-9]+$
        result = runner.invoke(
            cli,
            [
                "permission",
                "check",
                "secret",
                "get",
                "-d",
                "Project:test-project1",
                "-i",
                "perm-secret-999",
            ],
        )

        # Should match the regex pattern
        assert result.exit_code == 0
        assert "Authorized" in result.output

    # =================
    # SERVICE ACCOUNT PERMISSION TESTS
    # =================

    # Note: These tests would require service account setup
    # Skipping for now but adding placeholders for future implementation

    @pytest.mark.skip(reason="Requires service account setup")
    def test_60_service_account_inspect_permissions(self):
        """Test service account can inspect its permissions"""
        # TODO: Implement when service account auth is available
        pass

    @pytest.mark.skip(reason="Requires service account setup")
    def test_61_service_account_check_permissions(self):
        """Test service account can check its permissions"""
        # TODO: Implement when service account auth is available
        pass

    # =================
    # ERROR HANDLING AND EDGE CASES
    # =================

    def test_70_check_permission_missing_resource(self, logged_in_user_11):
        """Test permission check with missing resource argument"""
        runner, user = logged_in_user_11

        # Missing resource and action arguments
        result = runner.invoke(cli, ["permission", "check"])

        # Should fail with usage error
        assert result.exit_code != 0
        assert "Missing argument" in result.output or "Usage:" in result.output

    def test_71_check_permission_missing_action(self, logged_in_user_11):
        """Test permission check with missing action argument"""
        runner, user = logged_in_user_11

        # Missing action argument
        result = runner.invoke(cli, ["permission", "check", "secret"])

        # Should fail with usage error
        assert result.exit_code != 0
        assert "Missing argument" in result.output or "Usage:" in result.output

    def test_72_check_permission_invalid_domain_format(self, logged_in_user_11):
        """Test permission check with invalid domain format"""
        runner, user = logged_in_user_11

        # Invalid domain format (missing colon)
        result = runner.invoke(
            cli,
            [
                "permission",
                "check",
                "secret",
                "get",
                "-d",
                "InvalidDomain",
            ],
        )

        # Should fail with validation error
        assert result.exit_code != 0
        assert "invalid" in result.output.lower()

    def test_73_check_permission_invalid_domain_kind(self, logged_in_user_11):
        """Test permission check with invalid domain kind"""
        runner, user = logged_in_user_11

        # Invalid domain kind (UserGroup not supported in permissions API)
        result = runner.invoke(
            cli,
            [
                "permission",
                "check",
                "secret",
                "get",
                "-d",
                "UserGroup:my-group",
            ],
        )

        # Should fail with validation error
        assert result.exit_code != 0
        assert "not supported" in result.output or "invalid" in result.output.lower()

    def test_74_check_permission_without_project_in_config(
        self, cli_runner, test_user_11, test_projects
    ):
        """Test permission check without domain flag when no project in config"""
        # Login without selecting a project
        test_user_11.login(cli_runner, project_name=None)

        # Try to check permission without domain flag
        # Should fall back to org level or use project from config if one exists
        result = cli_runner.invoke(
            cli,
            [
                "permission",
                "check",
                "device",
                "get_device",
            ],
        )

        # Should check org level permissions for devices (user11 has org-device-viewer)
        # or may use last project from config
        assert (
            result.exit_code == 0
            or "Unauthorized" in result.output
            or "Organization" in result.output
        )

    def test_75_user11_check_nonexistent_resource_type(self, logged_in_user_11):
        """Test permission check for non-existent resource type"""
        runner, user = logged_in_user_11

        # Check permission for a resource that doesn't exist in permissions
        result = runner.invoke(
            cli,
            [
                "permission",
                "check",
                "nonexistent-resource",
                "get",
                "-d",
                "Project:test-project1",
            ],
        )

        # Should be unauthorized (resource not in permissions)
        assert result.exit_code != 0
        assert "Unauthorized" in result.output

    def test_76_user11_check_nonexistent_action(self, logged_in_user_11):
        """Test permission check for non-existent action"""
        runner, user = logged_in_user_11

        # Check permission for an action that doesn't exist
        result = runner.invoke(
            cli,
            [
                "permission",
                "check",
                "secret",
                "nonexistent_action",
                "-d",
                "Project:test-project1",
            ],
        )

        # Should be unauthorized (action not in permissions)
        assert result.exit_code != 0
        assert "Unauthorized" in result.output

    # =================
    # MULTI-LEVEL PERMISSION TESTS
    # =================

    def test_80_check_project_permission_with_org_override(self, logged_in_user_11):
        """Test that org-level permissions work when checking project domain"""
        runner, user = logged_in_user_11

        # User11 has org-level device viewer permission
        # This should work even when specifying a project domain
        result = runner.invoke(
            cli,
            [
                "permission",
                "check",
                "device",
                "get_device",
                "-d",
                "Project:test-project1",
                "-i",
                "device-001",
            ],
        )

        # Should be authorized (may appear at either org or project level due to inheritance)
        assert result.exit_code == 0
        assert "Authorized" in result.output

    def test_81_check_project_only_permission(self, logged_in_user_11):
        """Test permission that exists only at project level"""
        runner, user = logged_in_user_11

        # User11 has project-level secret viewer permission but not org-level
        result = runner.invoke(
            cli,
            [
                "permission",
                "check",
                "secret",
                "get",
                "-d",
                "Project:test-project1",
                "-i",
                "perm-secret-001",
            ],
        )

        # Should be authorized at project level
        assert result.exit_code == 0
        assert "Authorized" in result.output
        assert "project level" in result.output

    # =================
    # CLEANUP TESTS (Run Last)
    # =================

    def test_90_super_user_unbinds_roles(
        self,
        cli_runner,
        super_user,
        test_projects,
        test_user_11_email,
        test_user_12_email,
    ):
        """Unbind roles from test users"""
        super_user.login(cli_runner, project_name=test_projects[0])

        # Unbind project-level roles
        cli_runner.invoke(
            cli,
            [
                "role",
                "unbind",
                "permission-viewer",
                f"Project:{test_projects[0]}",
                f"User:{test_user_11_email}",
            ],
        )

        cli_runner.invoke(
            cli,
            [
                "role",
                "unbind",
                "permission-manager",
                f"Project:{test_projects[0]}",
                f"User:{test_user_12_email}",
            ],
        )

        # Unbind org-level role
        cli_runner.invoke(
            cli,
            [
                "role",
                "unbind",
                "org-device-viewer",
                "Organization:CliTest",
                f"User:{test_user_11_email}",
            ],
        )

    def test_91_super_user_deletes_test_secrets(
        self, cli_runner, super_user, test_projects
    ):
        """Delete test secrets created for permission testing"""
        super_user.login(cli_runner, project_name=test_projects[0])

        result = cli_runner.invoke(
            cli, ["delete", "-f", str(self.secret_manifest), "--silent"]
        )

        # Should succeed or resources already deleted
        assert result.exit_code == 0 or "not found" in result.output.lower()

    def test_99_super_user_deletes_roles(self, cli_runner, super_user, test_projects):
        """Delete roles created for permission testing"""
        super_user.login(cli_runner, project_name=test_projects[0])

        result = cli_runner.invoke(
            cli, ["delete", "-f", str(self.role_manifest), "--silent"]
        )

        # Should succeed or roles already deleted
        assert result.exit_code == 0 or "not found" in result.output.lower()

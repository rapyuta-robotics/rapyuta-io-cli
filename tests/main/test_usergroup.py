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
Test module for UserGroup RBAC functionality.

This module tests role-based access control (RBAC) using usergroups with
embedded predefined role bindings. The usergroup manifests include role
assignments to project domains directly in the manifest, eliminating the
need for separate role binding commands.

Key features tested:
- Usergroup creation with embedded role bindings
- Project admin permissions (project_admin role)
- Project viewer permissions (project_viewer role)
- Resource access control for secrets, packages, and static routes
- Template processing for dynamic project name substitution

The test structure follows this flow:
1. Create test resources (secrets, packages, static routes)
2. Create usergroups with embedded role bindings using templates
3. Verify usergroups were created successfully
4. Test project admin permissions across all resource types
5. Test project viewer permissions across all resource types
6. Cleanup resources and usergroups
"""

from pathlib import Path

import pytest

from riocli.bootstrap import cli


class TestUsergroupPredefinedRoleRBAC:
    """
    Test RBAC scenarios using usergroups with predefined roles
    """

    @pytest.fixture(autouse=True)
    def setup_manifests(self):
        """Setup manifest file paths"""
        self.manifest_dir = Path(__file__).parent.parent / "fixtures" / "manifests"
        self.usergroup_manifest_dir = self.manifest_dir / "usergroups"
        self.secret_usergroups = self.usergroup_manifest_dir / "secret-usergroups.yaml"
        self.package_usergroups = self.usergroup_manifest_dir / "package-usergroups.yaml"
        self.staticroute_usergroups = (
            self.usergroup_manifest_dir / "staticroute-usergroups.yaml"
        )
        self.test_secrets = self.usergroup_manifest_dir / "test-secrets.yaml"
        self.test_packages = self.usergroup_manifest_dir / "test-packages.yaml"
        self.test_staticroutes = self.usergroup_manifest_dir / "test-staticroutes.yaml"
        self.test_secrets_proj2 = self.usergroup_manifest_dir / "test-secrets-proj2.yaml"
        self.custom_role = self.usergroup_manifest_dir / "custom-staticroute-role.yaml"
        self.staticroute_usergroups_with_custom = (
            self.usergroup_manifest_dir / "staticroute-usergroups-with-custom-role.yaml"
        )
        self.test_secret_managers_modified = (
            self.usergroup_manifest_dir / "test-secret-managers-modified.yaml"
        )
        self.custom_usergroup_modify_role = (
            self.usergroup_manifest_dir / "custom-usergroup-modify-role.yaml"
        )

    @pytest.fixture
    def logged_in_user_11(self, cli_runner, test_user_11, test_projects):
        """Fixture for test_user_11 logged in with CLI runner"""
        test_user_11.login(cli_runner, project_name="test-project1")
        return cli_runner, test_user_11

    @pytest.fixture
    def logged_in_user_12(self, cli_runner, test_user_12, test_projects):
        """Fixture for test_user_12 logged in with CLI runner"""
        test_user_12.login(cli_runner, project_name="test-project1")
        return cli_runner, test_user_12

    # =================
    # SETUP TESTS (Run First)
    # =================

    def test_01_super_user_creates_test_resources(
        self, cli_runner, super_user, test_projects
    ):
        """Create test resources for RBAC testing in test-project1"""
        super_user.login(cli_runner, project_name="test-project1")

        result = cli_runner.invoke(cli, ["apply", str(self.test_secrets), "--force"])
        assert result.exit_code == 0

        result = cli_runner.invoke(cli, ["apply", str(self.test_packages), "--force"])
        assert result.exit_code == 0

        result = cli_runner.invoke(cli, ["apply", str(self.test_staticroutes), "--force"])
        assert result.exit_code == 0

    def test_01b_super_user_creates_additional_resources(
        self, cli_runner, super_user, test_projects
    ):
        """Create additional test resources in test-project2 for broader testing"""
        super_user.login(cli_runner, project_name="test-project2")

        # Create test resources in test-project2 using manifest
        result = cli_runner.invoke(cli, ["apply", "-f", str(self.test_secrets_proj2)])
        assert result.exit_code == 0, result.output

    def test_02_super_user_creates_usergroups(
        self, cli_runner, super_user, test_projects
    ):
        """Test creation of usergroups with embedded role bindings"""
        super_user.login(cli_runner, project_name="test-project1")

        # Create usergroups from manifests (roles are embedded in manifests)
        result = cli_runner.invoke(cli, ["apply", str(self.secret_usergroups), "-f"])
        assert result.exit_code == 0, result.output

        result = cli_runner.invoke(cli, ["apply", str(self.package_usergroups), "-f"])
        assert result.exit_code == 0, result.output

        result = cli_runner.invoke(cli, ["apply", str(self.staticroute_usergroups), "-f"])
        assert result.exit_code == 0, result.output

    def test_03_verify_usergroups_created(self, cli_runner, super_user, test_projects):
        """Test that usergroups were created successfully"""
        super_user.login(cli_runner, project_name="test-project1")

        result = cli_runner.invoke(cli, ["usergroup", "list"])
        assert result.exit_code == 0

        # Verify usergroups exist
        assert "test-secret-viewers" in result.output
        assert "test-secret-managers" in result.output
        assert "test-package-viewers" in result.output
        assert "test-package-managers" in result.output
        assert "test-staticroute-viewers" in result.output
        assert "test-staticroute-managers" in result.output

    # =================
    # PROJECT ADMIN ROLE TESTS - ROLES ARE DEFINED IN USERGROUP MANIFESTS
    # =================

    def test_10_user11_project_admin_secret_permissions(self, logged_in_user_11):
        """Test user11 with project_admin permissions can manage secrets"""
        runner, user = logged_in_user_11

        # Should be able to list secrets
        result = runner.invoke(cli, ["secret", "list"])
        assert result.exit_code == 0

        # Should be able to inspect secrets
        result = runner.invoke(cli, ["secret", "inspect", "test-secret-1"])
        assert result.exit_code == 0

        # Note: Secret creation is only available via manifests, not CLI commands
        # Admin users would typically have permissions to apply manifests

    def test_11_user11_project_admin_package_permissions(self, logged_in_user_11):
        """Test user11 with project_admin permissions can manage packages"""
        runner, user = logged_in_user_11

        # Should be able to list packages
        result = runner.invoke(cli, ["package", "list"])
        assert result.exit_code == 0

        # Should be able to inspect packages
        result = runner.invoke(cli, ["package", "inspect", "test-package-1"])
        assert result.exit_code == 0

    def test_12_user11_project_admin_static_route_permissions(self, logged_in_user_11):
        """Test user11 with project_admin permissions can manage static routes"""
        runner, user = logged_in_user_11

        # Should be able to list static routes
        result = runner.invoke(cli, ["static-route", "list"])
        assert result.exit_code == 0, result.output
        assert "test-route-1-clitest" in result.output

        # Should be able to inspect static routes
        result = runner.invoke(cli, ["static-route", "inspect", "test-route-1-clitest"])
        assert result.exit_code == 0, result.output

    # =================
    # PROJECT VIEWER ROLE TESTS - ROLES ARE DEFINED IN USERGROUP MANIFESTS
    # =================

    def test_20_user12_project_viewer_secret_permissions(self, logged_in_user_12):
        """Test user12 with project_viewer permissions has read-only access to secrets"""
        runner, user = logged_in_user_12

        # Should be able to list secrets
        result = runner.invoke(cli, ["secret", "list"])
        assert result.exit_code == 0

        # Should be able to inspect secrets
        result = runner.invoke(cli, ["secret", "inspect", "test-secret-1"])
        assert result.exit_code == 0

        # Note: Secret creation is only available via manifests, not CLI commands
        # Viewer permissions would prevent applying new secret manifests

    def test_21_user12_project_viewer_package_permissions(self, logged_in_user_12):
        """Test user12 with project_viewer permissions has read-only access to packages"""
        runner, user = logged_in_user_12

        # Should be able to list packages
        result = runner.invoke(cli, ["package", "list"])
        assert result.exit_code == 0

        # Should be able to inspect packages
        result = runner.invoke(cli, ["package", "inspect", "test-package-1"])
        assert result.exit_code == 0

    def test_22_user12_project_viewer_static_route_permissions(self, logged_in_user_12):
        """Test user12 with project_viewer permissions has read-only access to static routes"""
        runner, user = logged_in_user_12

        # Should be able to list static routes
        result = runner.invoke(cli, ["static-route", "list"])
        assert result.exit_code == 0, result.output
        assert "test-route-1-clitest" in result.output

        # Should be able to inspect static routes
        result = runner.invoke(cli, ["static-route", "inspect", "test-route-1-clitest"])
        assert result.exit_code == 0, result.output

    def test_23_user11_cross_project_permissions(self, logged_in_user_11):
        """Test user11 cross-project permissions (viewer in test-project1, admin in test-project2)"""
        runner, user = logged_in_user_11

        # Switch to test-project2 where user should have admin permissions
        result = runner.invoke(cli, ["project", "select", "test-project2"])
        assert result.exit_code == 0

        # Should be able to list secrets in test-project2
        result = runner.invoke(cli, ["secret", "list"])
        assert result.exit_code == 0

        # Should be able to inspect the secret we created in test-project2
        result = runner.invoke(cli, ["secret", "inspect", "test-secret-proj2-1"])
        assert result.exit_code == 0

        # Should be able to inspect other secrets in test-project2
        result = runner.invoke(cli, ["secret", "inspect", "admin-test-secret-proj2"])
        assert result.exit_code == 0

        # Note: Secret creation/deletion is done via manifests, not CLI commands
        # Admin users would have permissions to apply/delete resource manifests

        # Switch back to test-project1 for other tests
        result = runner.invoke(cli, ["project", "select", "test-project1"])
        assert result.exit_code == 0

    # =================
    # CUSTOM ROLE TESTS
    # =================

    def test_24_super_user_creates_custom_role(
        self, cli_runner, super_user, test_projects
    ):
        """Test super user creates a custom role with StaticRoute create permissions"""
        super_user.login(cli_runner, project_name="test-project2")

        # Create custom role from manifest
        result = cli_runner.invoke(cli, ["apply", str(self.custom_role), "-f"])
        assert result.exit_code == 0, result.output

        # Verify role was created
        result = cli_runner.invoke(cli, ["role", "list"])
        assert result.exit_code == 0
        assert "custom-staticroute-creator" in result.output

    def test_25_super_user_updates_usergroup_with_custom_role(
        self, cli_runner, super_user, test_projects
    ):
        """Test super user updates usergroup to include custom role"""
        super_user.login(cli_runner, project_name="test-project1")

        # Update usergroup to include custom role
        result = cli_runner.invoke(
            cli, ["apply", str(self.staticroute_usergroups_with_custom), "-f"]
        )
        assert result.exit_code == 0, result.output

        # Verify usergroup still exists
        result = cli_runner.invoke(cli, ["usergroup", "list"])
        assert result.exit_code == 0
        assert "test-staticroute-viewers" in result.output

    def test_26_user12_custom_create_permissions(self, logged_in_user_12):
        """Test user12 can create static routes with custom-route.* pattern"""
        runner, user = logged_in_user_12

        # User12 should be able to create this static route
        result = runner.invoke(
            cli, ["static-route", "create", "custom-route-test-user12"]
        )
        assert result.exit_code == 0, result.output

        # Verify the route was created
        result = runner.invoke(cli, ["static-route", "list"])
        assert result.exit_code == 0
        assert "custom-route-test-user12" in result.output

        # User12 should not be able to delete the static route
        result = runner.invoke(
            cli, ["static-route", "delete", "custom-route-test-user12-clitest"]
        )
        assert result.exit_code != 0, (
            f"StaticRoute deletion should fail with unauthorized. "
            f"Exit code: {result.exit_code}, Output: {result.output}"
        )

    def test_27_user12_retains_view_permissions(self, logged_in_user_12):
        """Test user12 still has view permissions for all static routes"""
        runner, user = logged_in_user_12

        # Should be able to list all static routes (from rio-project_viewer)
        result = runner.invoke(cli, ["static-route", "list"])
        assert result.exit_code == 0, result.output

        # Should be able to inspect existing test routes
        result = runner.invoke(cli, ["static-route", "inspect", "test-route-1-clitest"])
        assert result.exit_code == 0, result.output

        # Should be able to inspect the custom route created in previous test
        result = runner.invoke(
            cli, ["static-route", "inspect", "custom-route-test-user12-clitest"]
        )
        assert result.exit_code == 0, result.output

    # =================
    # MODIFY_RULES PERMISSION TESTS
    # =================

    def test_28_user11_cannot_modify_usergroup_without_modify_role(
        self, logged_in_user_11
    ):
        """Test user11 (rio-group_admin) cannot modify usergroup roles without modify_rules permission"""
        runner, user = logged_in_user_11

        # User11 is rio-group_admin in test-secret-managers, but should not be able to
        # modify the usergroup's project role bindings without modify_rules permission
        result = runner.invoke(
            cli, ["apply", str(self.test_secret_managers_modified), "-f"]
        )
        assert result.exit_code != 0, (
            f"Usergroup modification should fail without modify_rules permission. "
            f"Exit code: {result.exit_code}, Output: {result.output}"
        )

    def test_29_super_user_creates_custom_modify_role(
        self, cli_runner, super_user, test_projects
    ):
        """Test super user creates a custom role with modify_rules permission for usergroups"""
        super_user.login(cli_runner, project_name="test-project1")

        # Create custom role with modify_rules permission
        result = cli_runner.invoke(
            cli, ["apply", str(self.custom_usergroup_modify_role), "-f"]
        )
        assert result.exit_code == 0, result.output

        # Verify role was created
        result = cli_runner.invoke(cli, ["role", "list"])
        assert result.exit_code == 0
        assert "custom-usergroup-modifier" in result.output

    def test_30_super_user_binds_custom_role_to_user11(
        self, cli_runner, super_user, test_user_11, test_projects
    ):
        """Test super user binds custom modify_rules role to user11 at project level"""
        super_user.login(cli_runner, project_name="test-project1")

        result = cli_runner.invoke(
            cli,
            [
                "role",
                "bind",
                "rio-org_viewer",
                "Organization:CliTest",
                f"User:{test_user_11.email}",
            ],
        )
        assert result.exit_code == 0, result.output

        # Bind custom role to user11 at project level
        result = cli_runner.invoke(
            cli,
            [
                "role",
                "bind",
                "custom-usergroup-modifier",
                "UserGroup:test-secret-managers",
                f"User:{test_user_11.email}",
            ],
        )
        assert result.exit_code == 0, result.output

    def test_31_user11_can_modify_usergroup_with_modify_rules(self, logged_in_user_11):
        """Test user11 can now modify usergroup roles with modify_rules permission"""
        runner, user = logged_in_user_11

        # User11 should now be able to modify test-secret-managers with additional roles
        result = runner.invoke(
            cli, ["apply", str(self.test_secret_managers_modified), "-f"]
        )
        assert result.exit_code == 0, result.output

        # Verify the usergroup was modified by inspecting it
        result = runner.invoke(cli, ["usergroup", "inspect", "test-secret-managers"])
        assert result.exit_code == 0, result.output
        # The modified manifest adds test-project2 viewer role
        assert "test-project2" in result.output

    def test_32_user11_cannot_modify_other_usergroup_without_permission(
        self, logged_in_user_11
    ):
        """Test user11 cannot modify another usergroup where they don't have modify_rules"""
        runner, user = logged_in_user_11

        # User11 has modify_rules only for test-secret-managers (via pattern '^test-secret-managers$')
        # Try to modify test-package-managers which is a different usergroup
        # First, let's create a modified version inline or expect it to fail
        result = runner.invoke(cli, ["apply", str(self.package_usergroups), "-f"])
        assert result.exit_code != 0, (
            f"Modifying other usergroups should fail without modify_rules permission. "
            f"Exit code: {result.exit_code}, Output: {result.output}"
        )

    # =================
    # CLEANUP TESTS - ROLES ARE EMBEDDED IN USERGROUP MANIFESTS
    # =================

    def test_90_cleanup_resources(
        self, cli_runner, super_user, test_user_11, test_projects
    ):
        """Cleanup test resources"""
        super_user.login(cli_runner, project_name="test-project1")

        # Delete custom static route created by user12
        result = cli_runner.invoke(
            cli,
            [
                "static-route",
                "delete",
                "custom-route-test-user12-clitest",
                "--force",
                "--silent",
            ],
        )
        # Allow this to fail if the route doesn't exist

        # Unbind custom-usergroup-modifier role from user11
        result = cli_runner.invoke(
            cli,
            [
                "role",
                "unbind",
                "custom-usergroup-modifier",
                "UserGroup:test-secret-managers",
                f"User:{test_user_11.email}",
            ],
        )
        # Allow this to fail if the binding doesn't exist

        result = cli_runner.invoke(
            cli,
            [
                "role",
                "unbind",
                "rio-org_viewer",
                "Organization:CliTest",
                f"User:{test_user_11.email}",
            ],
        )

        # Delete custom usergroup modify role
        result = cli_runner.invoke(
            cli, ["delete", "--silent", str(self.custom_usergroup_modify_role)]
        )
        # Continue even if this fails

        # Delete custom staticroute role
        result = cli_runner.invoke(cli, ["delete", "--silent", str(self.custom_role)])
        # Continue even if this fails

        # Delete all usergroups and other resources
        result = cli_runner.invoke(
            cli, ["delete", "--silent", str(self.usergroup_manifest_dir)]
        )
        assert result.exit_code == 0, result.output

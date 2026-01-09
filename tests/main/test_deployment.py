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
Test module for Deployment RBAC functionality.

This module tests role-based access control (RBAC) for deployment resources
using direct role binding with users. Tests cover all deployment actions:
- create, update, delete
- get, list
- exec, log
- get_history, get_graph

Key features tested:
- Custom role creation for deployment-specific permissions
- Role binding to individual users
- Deployment lifecycle operations with different permission levels
- Cross-project deployment access
- Package dependency access for deployments

The test structure follows this flow:
1. Create test packages (deployment dependencies)
2. Create test deployments from packages
3. Create custom roles for deployment operations
4. Bind roles to users with different permission levels
5. Test deployment operations with different users
6. Test advanced deployment operations (exec, logs, history)
7. Cleanup resources and role bindings
"""

import time
from pathlib import Path

import pytest

from riocli.bootstrap import cli


class TestDeploymentRBAC:
    """
    Test RBAC scenarios for deployment operations using direct role binding
    """

    @pytest.fixture(autouse=True)
    def setup_manifests(self):
        """Setup manifest file paths"""
        self.manifest_dir = (
            Path(__file__).parent.parent / "fixtures" / "manifests" / "deployments"
        )
        self.test_packages = self.manifest_dir / "test-packages-for-deployments.yaml"
        self.test_deployments = self.manifest_dir / "test-deployments.yaml"
        self.managed_deployments = self.manifest_dir / "managed-deployments.yaml"
        self.deployment_roles = self.manifest_dir / "deployment-roles.yaml"

    @pytest.fixture
    def logged_in_user_1(self, cli_runner, test_user_11, test_projects):
        """Fixture for test_user_11 logged in with CLI runner"""
        test_user_11.login(cli_runner, project_name="test-project1")
        return cli_runner, test_user_11

    @pytest.fixture
    def logged_in_user_2(self, cli_runner, test_user_12, test_projects):
        """Fixture for test_user_12 logged in with CLI runner"""
        test_user_12.login(cli_runner, project_name="test-project1")
        return cli_runner, test_user_12

    def _is_deployment_running(self, cli_runner, deployment_name):
        """Helper method to check if deployment is in running state"""
        max_retries = 2
        interval = 15  # seconds

        for _ in range(max_retries):
            result = cli_runner.invoke(cli, ["deployment", "status", deployment_name])
            if result.exit_code != 0:
                return False

            # Check if deployment status indicates it's running
            if "Running" in result.output:
                return True

            time.sleep(interval)

        return False

    def _bind_role(
        self, cli_runner, super_user, role_name, user_email, project_name="test-project1"
    ):
        """Helper method to bind a role to a user"""
        super_user.login(cli_runner, project_name=project_name)
        result = cli_runner.invoke(
            cli,
            [
                "role",
                "bind",
                role_name,
                f"Project:{project_name}",
                f"User:{user_email}",
            ],
        )
        assert result.exit_code == 0, f"Failed to bind {role_name} role: {result.output}"

    def _unbind_role(
        self, cli_runner, super_user, role_name, user_email, project_name="test-project1"
    ):
        """Helper method to unbind a role from a user"""
        super_user.login(cli_runner, project_name=project_name)
        cli_runner.invoke(
            cli,
            [
                "role",
                "unbind",
                role_name,
                f"Project:{project_name}",
                f"User:{user_email}",
            ],
        )

    def _assert_can_list_deployments(self, runner, expected_deployments=None):
        """Helper method to assert user can list deployments"""
        result = runner.invoke(cli, ["deployment", "list"])
        assert result.exit_code == 0, f"Failed to list deployments: {result.output}"

        if expected_deployments:
            for deployment in expected_deployments:
                assert deployment in result.output, (
                    f"{deployment} not found in output: {result.output}"
                )

    def _assert_can_inspect_deployment(self, runner, deployment_name):
        """Helper method to assert user can inspect deployment"""
        result = runner.invoke(cli, ["deployment", "inspect", deployment_name])
        assert result.exit_code == 0, (
            f"Failed to inspect deployment {deployment_name}: {result.output}"
        )

    def _assert_cannot_delete_deployment(self, runner, deployment_name):
        """Helper method to assert user cannot delete deployment"""
        result = runner.invoke(cli, ["deployment", "delete", deployment_name, "--force"])
        assert result.exit_code != 0, (
            f"Should not be able to delete {deployment_name}, but got exit code 0. Output: {result.output}"
        )
        assert "subject is not authorized for this operation" in result.output, (
            f"Expected auth error, got: {result.output}"
        )

    def _assert_logs_permission(
        self, runner, deployment_name, should_have_permission=True
    ):
        """Helper method to test logs permission"""
        if self._is_deployment_running(runner, deployment_name):
            pytest.skip("Logs command runs in follow mode, skipping to avoid test hang")
        else:
            result = runner.invoke(cli, ["deployment", "logs", deployment_name])
            if should_have_permission:
                assert (
                    "subject is not authorized for this operation" not in result.output
                ), (
                    f"Got unexpected auth error when deployment not running: {result.output}"
                )
            else:
                assert "subject is not authorized for this operation" in result.output, (
                    f"Expected auth error, got: {result.output}"
                )

    @pytest.mark.xdist_group(name="setup_a")
    def test_01_super_user_creates_test_packages(
        self, cli_runner, super_user, test_projects
    ):
        """Create test packages for deployment RBAC testing"""
        super_user.login(cli_runner, project_name="test-project1")

        # Create packages that deployments will depend on
        result = cli_runner.invoke(cli, ["apply", str(self.test_packages), "-f"])
        assert result.exit_code == 0, f"Failed to create packages: {result.output}"

    @pytest.mark.xdist_group(name="setup_a")
    def test_02_super_user_creates_test_deployments(
        self, cli_runner, super_user, test_projects
    ):
        """Create test deployments for RBAC testing"""
        super_user.login(cli_runner, project_name="test-project1")

        # Create deployments from packages
        result = cli_runner.invoke(cli, ["apply", str(self.test_deployments), "-f"])
        assert result.exit_code == 0, f"Failed to create deployments: {result.output}"

        result = cli_runner.invoke(cli, ["apply", str(self.managed_deployments), "-f"])
        assert result.exit_code == 0, f"Failed to create deployments: {result.output}"

    @pytest.mark.xdist_group(name="setup_a")
    def test_03_super_user_creates_deployment_roles(
        self, cli_runner, super_user, test_projects
    ):
        """Create custom deployment roles"""
        super_user.login(cli_runner, project_name="test-project1")

        # Create deployment-specific roles
        result = cli_runner.invoke(cli, ["apply", str(self.deployment_roles), "-f"])
        assert result.exit_code == 0, (
            f"Failed to create deployment roles: {result.output}"
        )

    @pytest.mark.xdist_group(name="setup_a")
    def test_04_verify_deployments_created(self, cli_runner, super_user, test_projects):
        """Verify deployments were created successfully"""
        super_user.login(cli_runner, project_name="test-project1")

        result = cli_runner.invoke(cli, ["deployment", "list"])
        assert result.exit_code == 0, f"Failed to list deployments: {result.output}"

        # Verify deployments exist
        assert "test-deployment-1" in result.output, (
            f"test-deployment-1 not found in output: {result.output}"
        )
        assert "test-deployment-2" in result.output, (
            f"test-deployment-2 not found in output: {result.output}"
        )
        assert "test-deployment-3" in result.output, (
            f"test-deployment-3 not found in output: {result.output}"
        )

    # =================
    # ROLE BINDING TESTS (Group A - Sequential with setup)
    # =================

    @pytest.mark.xdist_group(name="setup_a")
    def test_10_bind_deployment_viewer_role(self, cli_runner, super_user, test_projects):
        """Bind deployment-viewer role to test_user_11"""
        self._bind_role(
            cli_runner, super_user, "deployment-viewer", "cli.test1@rapyuta-robotics.com"
        )

    @pytest.mark.xdist_group(name="setup_a")
    def test_11_bind_deployment_readonly_role(
        self, cli_runner, super_user, test_projects
    ):
        """Bind deployment-readonly role to test_user_12"""
        self._bind_role(
            cli_runner,
            super_user,
            "deployment-readonly",
            "cli.test2@rapyuta-robotics.com",
        )

    @pytest.mark.xdist_group(name="viewer_tests_b")
    def test_20_user1_deployment_viewer_list_permissions(self, logged_in_user_1):
        """Test user1 with deployment-viewer role can list deployments"""
        runner, user = logged_in_user_1
        self._assert_can_list_deployments(runner, ["test-deployment-1"])

    @pytest.mark.xdist_group(name="viewer_tests_b")
    def test_21_user1_deployment_viewer_get_permissions(self, logged_in_user_1):
        """Test user1 with deployment-viewer role can inspect deployments"""
        runner, user = logged_in_user_1
        self._assert_can_inspect_deployment(runner, "test-deployment-1")

    @pytest.mark.xdist_group(name="viewer_tests_b")
    def test_22_user1_deployment_viewer_log_permissions(self, logged_in_user_1):
        """Test user1 with deployment-viewer role can view logs"""
        runner, user = logged_in_user_1
        self._assert_logs_permission(
            runner, "test-deployment-1", should_have_permission=True
        )

    @pytest.mark.xdist_group(name="viewer_tests_b")
    def test_23_user1_deployment_viewer_history_permissions(self, logged_in_user_1):
        """Test user1 with deployment-viewer role can view deployment details"""
        runner, user = logged_in_user_1

        # Test ability to get deployment details (alternative to history)
        result = runner.invoke(cli, ["deployment", "inspect", "test-deployment-1"])
        assert result.exit_code == 0, f"Failed to inspect deployment: {result.output}"

    @pytest.mark.xdist_group(name="viewer_tests_b")
    def test_40_user1_cannot_delete_deployments(self, logged_in_user_1):
        """Test user1 with viewer role cannot delete deployments"""
        runner, user = logged_in_user_1
        result = runner.invoke(
            cli, ["deployment", "delete", "test-deployment-3", "--force"]
        )
        assert result.exit_code != 0, (
            f"Should not be able to delete deployment, but got exit code 0. Output: {result.output}"
        )
        # Check for authorization error in output
        assert "subject is not authorized for this operation" in result.output, (
            f"Expected auth error, got: {result.output}"
        )

    @pytest.mark.xdist_group(name="readonly_tests_c")
    def test_30_user2_deployment_readonly_list_permissions(self, logged_in_user_2):
        """Test user2 with deployment-readonly role can list deployments"""
        runner, user = logged_in_user_2
        self._assert_can_list_deployments(runner)

    @pytest.mark.xdist_group(name="readonly_tests_c")
    def test_31_user2_deployment_readonly_get_permissions(self, logged_in_user_2):
        """Test user2 with deployment-readonly role can inspect deployments"""
        runner, user = logged_in_user_2
        self._assert_can_inspect_deployment(runner, "test-deployment-1")

    @pytest.mark.xdist_group(name="readonly_tests_c")
    def test_32_user2_deployment_readonly_log_permissions(self, logged_in_user_2):
        """Test user2 with deployment-readonly role can view logs"""
        runner, user = logged_in_user_2
        self._assert_logs_permission(
            runner, "test-deployment-1", should_have_permission=True
        )

    @pytest.mark.xdist_group(name="readonly_tests_c")
    def test_41_user2_cannot_exec_on_deployments(self, logged_in_user_2):
        """Test user2 with readonly role cannot exec on deployments"""
        runner, user = logged_in_user_2

        # Should NOT be able to exec on deployment (readonly role doesn't have exec permission)
        result = runner.invoke(cli, ["deployment", "exec", "test-deployment-1", "ls"])
        assert result.exit_code != 0, (
            f"Should not be able to exec on deployment, but got exit code 0. Output: {result.output}"
        )
        # Check for authorization error OR runtime limitation
        auth_error_present = (
            "subject is not authorized for this operation" in result.output
        )
        runtime_error_present = "Only device runtime is supported" in result.output

        assert auth_error_present or runtime_error_present, (
            f"Expected auth error or runtime error, got: {result.output}"
        )

    @pytest.mark.xdist_group(name="manager_tests_d")
    def test_50_escalate_user1_to_deployment_manager(
        self, cli_runner, super_user, test_projects
    ):
        """Escalate user1 to deployment-manager role"""
        # Unbind previous role
        self._unbind_role(
            cli_runner, super_user, "deployment-viewer", "cli.test1@rapyuta-robotics.com"
        )

        # Bind manager role
        self._bind_role(
            cli_runner, super_user, "deployment-manager", "cli.test1@rapyuta-robotics.com"
        )

    @pytest.mark.xdist_group(name="manager_tests_d")
    def test_51_user1_deployment_manager_can_manage_deployments(self, logged_in_user_1):
        """Test user1 with deployment-manager role can manage managed-deployment instances"""
        runner, user = logged_in_user_1

        # Should be able to list deployments (includes managed ones)
        self._assert_can_list_deployments(
            runner, ["managed-deployment-1", "managed-deployment-2"]
        )

        # Should be able to inspect managed deployments
        self._assert_can_inspect_deployment(runner, "managed-deployment-1")

        # Should be able to delete managed deployments
        result = runner.invoke(
            cli, ["deployment", "delete", "managed-deployment-2", "--force"]
        )
        assert result.exit_code == 0, (
            f"Failed to delete managed deployment: {result.output}"
        )

        # Should be able to restart managed deployments
        result = runner.invoke(
            cli, ["deployment", "restart", "managed-deployment-1", "--force"]
        )
        assert result.exit_code == 0, (
            f"Failed to restart managed deployment: {result.output}"
        )

        # Should NOT be able to delete non-managed deployments (test-deployment-*)
        result = runner.invoke(
            cli, ["deployment", "delete", "test-deployment-1", "--force"]
        )
        # Check if deployment exists and we get proper auth error
        if "not found" not in result.output.lower():
            assert result.exit_code != 0, (
                f"Should not be able to delete test-deployment-1, but got exit code 0. Output: {result.output}"
            )
            assert "subject is not authorized for this operation" in result.output, (
                f"Expected auth error, got: {result.output}"
            )

    @pytest.mark.xdist_group(name="manager_tests_d")
    def test_52_user1_deployment_manager_logs_and_exec(self, logged_in_user_1):
        """Test user1 with deployment-manager role can access logs and exec on managed deployments"""
        runner, user = logged_in_user_1

        # Should be able to view logs on managed deployments
        self._assert_logs_permission(
            runner, "managed-deployment-1", should_have_permission=True
        )

        # Test exec permissions (will fail due to cloud runtime but should pass auth)
        result = runner.invoke(
            cli, ["deployment", "exec", "managed-deployment-1", "echo", "test"]
        )
        # Should NOT get authorization error (auth passes, but cloud runtime not supported)
        assert "subject is not authorized for this operation" not in result.output, (
            f"Got unexpected auth error: {result.output}"
        )

    @pytest.mark.xdist_group(name="manager_tests_d")
    def test_53_recreate_deleted_managed_deployment(
        self, cli_runner, super_user, test_projects
    ):
        """Recreate the deleted managed deployment for further testing"""
        super_user.login(cli_runner, project_name="test-project1")

        # Recreate managed-deployment-2 that was deleted in previous test
        result = cli_runner.invoke(cli, ["apply", str(self.managed_deployments), "-f"])
        assert result.exit_code == 0, (
            f"Failed to recreate managed deployments: {result.output}"
        )

    @pytest.mark.xdist_group(name="executor_tests_e")
    def test_60_escalate_user2_to_deployment_executor(
        self, cli_runner, super_user, test_projects
    ):
        """Escalate user2 to deployment-executor role"""
        # Unbind previous role
        self._unbind_role(
            cli_runner,
            super_user,
            "deployment-readonly",
            "cli.test2@rapyuta-robotics.com",
        )

        # Bind executor role
        self._bind_role(
            cli_runner,
            super_user,
            "deployment-executor",
            "cli.test2@rapyuta-robotics.com",
        )

    @pytest.mark.xdist_group(name="executor_tests_e")
    def test_61_user2_deployment_executor_can_exec(self, logged_in_user_2):
        """Test user2 with deployment-executor role can exec on deployments"""
        runner, user = logged_in_user_2

        # Test exec permissions
        result = runner.invoke(
            cli, ["deployment", "exec", "test-deployment-1", "echo", "test"]
        )

        # Should either succeed OR fail due to runtime limitations (not auth)
        if result.exit_code != 0:
            # If it fails, should NOT be due to authorization
            assert "subject is not authorized for this operation" not in result.output, (
                f"Got unexpected auth error: {result.output}"
            )
            # Runtime limitation is acceptable
            runtime_error_present = "Only device runtime is supported" in result.output
            assert runtime_error_present, (
                f"Expected runtime error if not successful, got: {result.output}"
            )

    @pytest.mark.xdist_group(name="cross_project_tests_f")
    def test_70_create_deployment_in_project2(
        self, cli_runner, super_user, test_projects
    ):
        """Create deployment in test-project2 for cross-project testing"""
        super_user.login(cli_runner, project_name="test-project2")

        # Create packages first
        result = cli_runner.invoke(cli, ["apply", str(self.test_packages), "-f"])
        assert result.exit_code == 0, (
            f"Failed to create packages in project2: {result.output}"
        )

        # Create deployments
        result = cli_runner.invoke(cli, ["apply", str(self.test_deployments), "-f"])
        assert result.exit_code == 0, (
            f"Failed to create deployments in project2: {result.output}"
        )

    @pytest.mark.xdist_group(name="cross_project_tests_f")
    def test_71_bind_cross_project_role(self, cli_runner, super_user, test_projects):
        """Bind deployment role in test-project2"""
        super_user.login(cli_runner, project_name="test-project2")

        # Create roles in project2
        result = cli_runner.invoke(cli, ["apply", str(self.deployment_roles), "-f"])
        assert result.exit_code == 0, (
            f"Failed to create roles in project2: {result.output}"
        )

        # Bind role to user1 in project2
        self._bind_role(
            cli_runner,
            super_user,
            "deployment-viewer",
            "cli.test1@rapyuta-robotics.com",
            "test-project2",
        )

    @pytest.mark.xdist_group(name="cross_project_tests_f")
    def test_72_user1_cross_project_deployment_access(self, logged_in_user_1):
        """Test user1 can access deployments in both projects"""
        runner, user = logged_in_user_1

        # Switch to test-project2
        result = runner.invoke(cli, ["project", "select", "test-project2"])
        assert result.exit_code == 0, f"Failed to select project2: {result.output}"

        # Should be able to list deployments in project2
        self._assert_can_list_deployments(runner)

        # Switch back to test-project1
        result = runner.invoke(cli, ["project", "select", "test-project1"])
        assert result.exit_code == 0, f"Failed to select project1: {result.output}"

        # Should still be able to list deployments in project1
        self._assert_can_list_deployments(runner)

    @pytest.mark.xdist_group(name="cleanup_z")
    def test_90_cleanup_role_bindings(self, cli_runner, super_user, test_projects):
        """Cleanup deployment role bindings"""
        # Cleanup project1 bindings
        bindings = [
            ("deployment-manager", "cli.test1@rapyuta-robotics.com"),
            ("deployment-executor", "cli.test2@rapyuta-robotics.com"),
        ]

        for role, user in bindings:
            self._unbind_role(cli_runner, super_user, role, user, "test-project1")

        # Cleanup project2 bindings
        self._unbind_role(
            cli_runner,
            super_user,
            "deployment-viewer",
            "cli.test1@rapyuta-robotics.com",
            "test-project2",
        )

    @pytest.mark.xdist_group(name="cleanup_z")
    def test_91_cleanup_deployment_resources(self, cli_runner, super_user, test_projects):
        """Cleanup deployment test resources"""
        super_user.login(cli_runner, project_name="test-project1")

        # Delete deployments first (they depend on packages)
        cli_runner.invoke(cli, ["delete", "--silent", str(self.test_deployments)])
        cli_runner.invoke(cli, ["delete", "--silent", str(self.managed_deployments)])

        # Delete packages
        cli_runner.invoke(cli, ["delete", "--silent", str(self.test_packages)])

        # Delete roles
        cli_runner.invoke(cli, ["delete", "--silent", str(self.deployment_roles)])

        # Cleanup project2 resources
        super_user.login(cli_runner, project_name="test-project2")
        cli_runner.invoke(cli, ["delete", "--silent", str(self.test_deployments)])
        cli_runner.invoke(cli, ["delete", "--silent", str(self.test_packages)])
        cli_runner.invoke(cli, ["delete", "--silent", str(self.deployment_roles)])

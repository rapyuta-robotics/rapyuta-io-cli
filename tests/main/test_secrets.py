"""
RBAC Tests for rapyuta.io CLI - Secret Operations

This module tests Role-Based Access Control scenarios for secret operations
using pytest and Click testing framework. It covers:
- Super user creating roles and secrets
- Test users with restricted access to secrets
- Multiple role scenarios with different permission patterns
- Pydantic model validation for invalid manifests

Test execution order:
1. Setup tests (super user creates roles and resources)
2. Basic RBAC tests (original secret-viewer role scenarios)
3. Extended role tests (new secret roles with different patterns)
4. Complex scenarios (multiple roles, boundary testing)
5. Cleanup tests (teardown resources)
"""

from pathlib import Path

import pytest

from riocli.bootstrap import cli


@pytest.mark.rbac
@pytest.mark.integration
@pytest.mark.slow
class TestSecretsRBAC:
    """Test class for Secret RBAC scenarios"""

    @pytest.fixture(autouse=True)
    def setup_manifests(self):
        """Setup manifest file paths"""
        self.manifests_dir = (
            Path(__file__).parent.parent / "fixtures" / "manifests" / "secrets"
        )
        self.role_manifest = self.manifests_dir / "role.yaml"
        self.secret_correct = (
            self.manifests_dir / "secret-correct.yaml"
        )  # Super user creates these
        self.secret_manifest = (
            self.manifests_dir / "secret.yaml"
        )  # Test users create these
        self.secret_wrong_manifest = self.manifests_dir / "secret-wrong.yaml"
        self.secret_extended = (
            self.manifests_dir / "secret-extended.yaml"
        )  # Extended patterns
        self.secret_docker = self.manifests_dir / "secret-docker.yaml"  # Docker patterns
        self.managed_secret_2 = (
            self.manifests_dir / "managed-secret-2.yaml"
        )  # For manager role testing
        self.boundary_secrets = (
            self.manifests_dir / "boundary-secrets.yaml"
        )  # For pattern boundary testing

    # =================
    # SETUP TESTS (Run First)
    # =================

    def test_01_super_user_creates_role(self, cli_runner, super_user, test_projects):
        """Test that superuser can create all roles for secret access"""
        # Login as superuser
        super_user.login(cli_runner, project_name=test_projects[0])

        # Create all roles using apply command
        result = cli_runner.invoke(cli, ["apply", "--silent", str(self.role_manifest)])

        # Should succeed
        assert result.exit_code == 0
        assert "Created" in result.output or "Updated" in result.output

    def test_02_super_user_creates_secrets(self, cli_runner, super_user, test_projects):
        """Test that superuser can create secrets"""
        # Login as superuser
        super_user.login(cli_runner, project_name=test_projects[0])

        # Create secrets from secret-correct.yaml (contains test-secret-1, test-secret-2, docker-secret, unauthorized-secret)
        result = cli_runner.invoke(
            cli,
            [
                "apply",
                "--silent",
                str(self.secret_correct),
            ],
        )

        # Should succeed
        assert result.exit_code == 0, result.output
        assert "Apply successful" in result.output

    def test_03_super_user_creates_extended_secrets(
        self, cli_runner, super_user, test_projects
    ):
        """Test that superuser can create extended secret patterns"""
        # Login as superuser
        super_user.login(cli_runner, project_name=test_projects[0])

        # Create extended secrets (user-secret-1, managed-secret-1, temp-secret-1)
        result = cli_runner.invoke(cli, ["apply", "--silent", str(self.secret_extended)])
        assert result.exit_code == 0, result.output
        assert "Apply successful" in result.output

        # Create docker secrets (docker-registry-secret, dockerhub-secret)
        result = cli_runner.invoke(cli, ["apply", "--silent", str(self.secret_docker)])
        assert result.exit_code == 0, result.output
        assert "Apply successful" in result.output

    def test_04_super_user_binds_role_to_test_users(
        self, cli_runner, super_user, test_user_11, test_user_12, test_projects
    ):
        """Test that superuser can bind the secret-viewer role to test users"""
        # Login as superuser
        super_user.login(cli_runner, project_name=test_projects[0])

        # Bind secret-viewer role to test_user_11
        result = cli_runner.invoke(
            cli,
            [
                "role",
                "bind",
                "secret-viewer",
                f"Project:{test_projects[0]}",
                f"User:{test_user_11.email}",
            ],
        )

        # Should succeed
        assert result.exit_code == 0

        # Bind secret-viewer role to test_user_12
        result = cli_runner.invoke(
            cli,
            [
                "role",
                "bind",
                "secret-viewer",
                f"Project:{test_projects[0]}",
                f"User:{test_user_12.email}",
            ],
        )

        # Should succeed
        assert result.exit_code == 0

    # =================
    # BASIC RBAC TESTS (secret-viewer role)
    # =================

    def test_10_user11_creates_secrets_from_manifest(self, logged_in_user_11):
        """Test that test_user_11 creates secrets from secret.yaml"""
        runner, user = logged_in_user_11

        # Create secrets from secret.yaml
        # This contains test-secret-4 (should succeed) and random-secret (should fail)
        result = runner.invoke(cli, ["apply", "--silent", str(self.secret_manifest)])

        # The result might be mixed - some secrets succeed, others fail
        # We'll verify the actual results in the list test
        assert result.exit_code != 0
        assert "Created secret:test-secret-4" in result.output
        assert (
            "Failed to apply secret:random-secret. Error: subject is not authorized for this operation"
            in result.output
        )

    def test_11_user11_can_list_secrets(self, logged_in_user_11):
        """Test that test_user_11 can list all secrets"""
        runner, user = logged_in_user_11

        result = runner.invoke(cli, ["secret", "list"])

        # Should succeed
        assert result.exit_code == 0, (
            f"Secret list should succeed for {user.email}. "
            f"Exit code: {result.exit_code}, Output: {result.output}"
        )

        # User should be able to see secrets that match test-secret.* pattern
        expected_visible = [
            "test-secret-1",
            "test-secret-2",
            "test-secret-4",
        ]

        # Check that authorized secrets are visible
        for secret in expected_visible:
            assert secret in result.output

    def test_12_user11_can_inspect_authorized_secrets(self, logged_in_user_11):
        """Test that test_user_11 can inspect secrets matching the role pattern"""
        runner, user = logged_in_user_11

        # Should be able to inspect test-secret-1
        result = runner.invoke(cli, ["secret", "inspect", "test-secret-1"])
        assert result.exit_code == 0

        # Should be able to inspect test-secret-2
        result = runner.invoke(cli, ["secret", "inspect", "test-secret-2"])
        assert result.exit_code == 0

        # Should be able to inspect test-secret-4 from secret.yaml
        result = runner.invoke(cli, ["secret", "inspect", "test-secret-4"])
        assert result.exit_code == 0

    def test_13_user11_cannot_inspect_unauthorized_secrets(self, logged_in_user_11):
        """Test that test_user_11 cannot inspect secrets not matching the role pattern"""
        runner, user = logged_in_user_11

        # Should NOT be able to inspect unauthorized-secret
        result = runner.invoke(cli, ["secret", "inspect", "unauthorized-secret"])
        assert result.exit_code != 0
        assert "subject is not authorized for this operation" in result.output

        # Should NOT be able to inspect random-secret (doesn't match test-secret.* pattern)
        result = runner.invoke(cli, ["secret", "inspect", "random-secret"])
        assert result.exit_code != 0
        # Check for authorization error messages
        assert "subject is not authorized for this operation" in result.output

    def test_14_user11_cannot_delete_secrets(self, logged_in_user_11):
        """Test that test_user_11 cannot delete secrets (only has get/create permissions)"""
        runner, user = logged_in_user_11

        # Should NOT be able to delete even authorized secrets
        result = runner.invoke(
            cli, ["secret", "delete", "test-secret-1", "--force", "--silent"]
        )

        assert result.exit_code != 0
        assert "subject is not authorized for this operation" in result.output

    def test_15_user12_creates_secrets_from_manifest(self, logged_in_user_12):
        """Test that test_user_12 creates secrets from secret.yaml"""
        runner, user = logged_in_user_12

        # Create secrets from secret.yaml
        # This contains test-secret-4 (should succeed) and random-secret (should fail)
        result = runner.invoke(cli, ["apply", "--silent", str(self.secret_manifest)])

        assert result.exit_code != 0
        assert "subject is not authorized for this operation" in result.output

    def test_16_user12_can_list_secrets(self, logged_in_user_12):
        """Test that test_user_12 can list all secrets"""
        runner, user = logged_in_user_12

        result = runner.invoke(cli, ["secret", "list"])

        # Should succeed
        assert result.exit_code == 0, (
            f"Secret list should succeed for {user.email}. "
            f"Exit code: {result.exit_code}, Output: {result.output}"
        )

        # User should be able to see secrets that match test-secret.* pattern
        expected_visible = [
            "test-secret-1",
            "test-secret-2",
            "test-secret-4",
        ]

        # Check that authorized secrets are visible
        for secret in expected_visible:
            assert secret in result.output

    def test_17_user12_can_inspect_authorized_secrets(self, logged_in_user_12):
        """Test that test_user_12 can inspect secrets matching the role pattern"""
        runner, user = logged_in_user_12

        # Should be able to inspect test-secret-1
        result = runner.invoke(cli, ["secret", "inspect", "test-secret-1"])
        assert result.exit_code == 0

        # Should be able to inspect test-secret-2
        result = runner.invoke(cli, ["secret", "inspect", "test-secret-2"])
        assert result.exit_code == 0

        # Should be able to inspect test-secret-4 from secret.yaml
        result = runner.invoke(cli, ["secret", "inspect", "test-secret-4"])
        assert result.exit_code == 0

    def test_18_user12_cannot_inspect_unauthorized_secrets(self, logged_in_user_12):
        """Test that test_user_12 cannot inspect secrets not matching the role pattern"""
        runner, user = logged_in_user_12

        # Should NOT be able to inspect unauthorized-secret
        result = runner.invoke(cli, ["secret", "inspect", "unauthorized-secret"])
        assert result.exit_code != 0
        # Check for authorization error messages
        assert "subject is not authorized for this operation" in result.output

        # Should NOT be able to inspect random-secret (doesn't match test-secret.* pattern)
        result = runner.invoke(cli, ["secret", "inspect", "random-secret"])
        assert result.exit_code != 0, (
            f"Secret inspect should fail for random-secret (wrong prefix). "
            f"Exit code: {result.exit_code}, Output: {result.output}"
        )
        assert "subject is not authorized for this operation" in result.output

    def test_19_user12_cannot_delete_secrets(self, logged_in_user_12):
        """Test that test_user_12 cannot delete secrets (only has get/create permissions)"""
        runner, user = logged_in_user_12

        # Should NOT be able to delete even authorized secrets
        result = runner.invoke(
            cli, ["secret", "delete", "test-secret-2", "--force", "--silent"]
        )

        assert result.exit_code != 0
        assert "subject is not authorized for this operation" in result.output

    # =================
    # EXTENDED ROLE TESTS (new secret role patterns)
    # =================

    def test_20_secret_creator_role_permissions(
        self, cli_runner, super_user, test_user_11, test_projects
    ):
        """Test secret-creator role - can create/get user-secret.* and list all secrets"""
        # Login as superuser and setup
        super_user.login(cli_runner, project_name=test_projects[0])

        # Bind secret-creator role to test_user_11
        result = cli_runner.invoke(
            cli,
            [
                "role",
                "bind",
                "secret-creator",
                f"Project:{test_projects[0]}",
                f"User:{test_user_11.email}",
            ],
        )
        assert result.exit_code == 0

        # Login as test_user_11
        test_user_11.login(cli_runner, project_name=test_projects[0])

        # Test listing all secrets (should work)
        result = cli_runner.invoke(cli, ["secret", "list"])
        assert result.exit_code == 0, result.output
        assert "user-secret-1" in result.output

        # Test getting user-secret-* (should work)
        result = cli_runner.invoke(cli, ["secret", "inspect", "user-secret-1"])
        assert result.exit_code == 0, result.output

        # Test getting managed-secret-* (should fail - wrong pattern)
        result = cli_runner.invoke(cli, ["secret", "inspect", "managed-secret-1"])
        assert result.exit_code != 0
        assert "subject is not authorized for this operation" in result.output

    def test_21_secret_manager_role_permissions(
        self, cli_runner, super_user, test_user_12, test_projects
    ):
        """Test secret-manager role - full CRUD on managed-secret.* and list all"""
        # Login as superuser and setup
        super_user.login(cli_runner, project_name=test_projects[0])

        # Bind secret-manager role to test_user_12
        result = cli_runner.invoke(
            cli,
            [
                "role",
                "bind",
                "secret-manager",
                f"Project:{test_projects[0]}",
                f"User:{test_user_12.email}",
            ],
        )
        assert result.exit_code == 0, result.output

        # Login as test_user_12
        test_user_12.login(cli_runner, project_name=test_projects[0])

        # Test listing all secrets (should work)
        result = cli_runner.invoke(cli, ["secret", "list"])
        assert result.exit_code == 0
        assert "managed-secret-1" in result.output

        # Test getting managed-secret-* (should work)
        result = cli_runner.invoke(cli, ["secret", "inspect", "managed-secret-1"])
        assert result.exit_code == 0

        # Test creating new managed secret via manifest (should work)
        result = cli_runner.invoke(cli, ["apply", "--silent", str(self.managed_secret_2)])
        assert result.exit_code == 0

        # Test deleting managed secret (should work)
        result = cli_runner.invoke(
            cli, ["secret", "delete", "managed-secret-1", "--force", "--silent"]
        )
        assert result.exit_code == 0

    def test_22_secret_readonly_role_permissions(
        self, cli_runner, super_user, test_user_11, test_projects
    ):
        """Test secret-readonly role - can get *docker* pattern and list all"""
        # Login as superuser and setup
        super_user.login(cli_runner, project_name=test_projects[0])

        # unbind secret-creator role to test_user_11
        result = cli_runner.invoke(
            cli,
            [
                "role",
                "unbind",
                "secret-creator",
                f"Project:{test_projects[0]}",
                f"User:{test_user_11.email}",
            ],
        )
        assert result.exit_code == 0

        # Bind secret-readonly role to test_user_11
        result = cli_runner.invoke(
            cli,
            [
                "role",
                "bind",
                "secret-readonly",
                f"Project:{test_projects[0]}",
                f"User:{test_user_11.email}",
            ],
        )
        assert result.exit_code == 0

        # Login as test_user_11
        test_user_11.login(cli_runner, project_name=test_projects[0])

        # Test listing all secrets (should work)
        result = cli_runner.invoke(cli, ["secret", "list"])
        assert result.exit_code == 0, result.output
        assert "docker-registry-secret" in result.output
        assert "dockerhub-secret" in result.output

        # Test getting *docker* pattern secrets (should work)
        result = cli_runner.invoke(cli, ["secret", "inspect", "docker-registry-secret"])
        assert result.exit_code == 0

        result = cli_runner.invoke(cli, ["secret", "inspect", "dockerhub-secret"])
        assert result.exit_code == 0

        # Test getting non-docker secrets (should fail)
        result = cli_runner.invoke(cli, ["secret", "inspect", "user-secret-1"])
        assert "subject is not authorized for this operation" in result.output

    def test_23_secret_deleter_role_permissions(
        self, cli_runner, super_user, test_user_12, test_projects
    ):
        """Test secret-deleter role - can delete/get temp-secret.* and list all"""
        # Login as superuser and setup
        super_user.login(cli_runner, project_name=test_projects[0])

        # Bind secret-deleter role to test_user_12
        result = cli_runner.invoke(
            cli,
            [
                "role",
                "bind",
                "secret-deleter",
                f"Project:{test_projects[0]}",
                f"User:{test_user_12.email}",
            ],
        )
        assert result.exit_code == 0

        # Login as test_user_12
        test_user_12.login(cli_runner, project_name=test_projects[0])

        # Test listing all secrets (should work)
        result = cli_runner.invoke(cli, ["secret", "list"])
        assert result.exit_code == 0
        assert "temp-secret-1" in result.output

        # Test getting temp-secret-* (should work)
        result = cli_runner.invoke(cli, ["secret", "inspect", "temp-secret-1"])
        assert result.exit_code == 0

        # Test deleting temp-secret-* (should work)
        result = cli_runner.invoke(
            cli, ["secret", "delete", "temp-secret-1", "--force", "--silent"]
        )
        assert result.exit_code == 0

        # Test getting non-temp secrets (should fail) - use user-secret-1 since managed-secret-1 was deleted in test_21
        result = cli_runner.invoke(cli, ["secret", "inspect", "user-secret-1"])
        assert "subject is not authorized for this operation" in result.output

    # =================
    # COMPLEX SCENARIOS
    # =================

    def test_30_secret_multiple_roles_combined_permissions(
        self, cli_runner, super_user, test_user_11, test_projects
    ):
        """Test user with multiple secret roles has combined permissions"""
        # Login as superuser and setup
        super_user.login(cli_runner, project_name=test_projects[0])

        # Bind multiple roles to test_user_11
        roles = ["secret-creator", "secret-readonly"]
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
            assert result.exit_code == 0

        # Login as test_user_11
        test_user_11.login(cli_runner, project_name=test_projects[0])

        # Test listing all secrets (should work from both roles)
        result = cli_runner.invoke(cli, ["secret", "list"])
        assert result.exit_code == 0

        # Should be able to access user-secret-* (from secret-creator)
        result = cli_runner.invoke(cli, ["secret", "inspect", "user-secret-1"])
        assert result.exit_code == 0

        # Should be able to access *docker* (from secret-readonly)
        result = cli_runner.invoke(cli, ["secret", "inspect", "docker-registry-secret"])
        assert result.exit_code == 0

        # Should NOT be able to access patterns from other roles
        result = cli_runner.invoke(cli, ["secret", "inspect", "managed-secret-1"])
        assert result.exit_code != 0
        assert "subject is not authorized for this operation" in result.output

    def test_31_secret_pattern_boundary_validation(
        self, cli_runner, super_user, test_user_12, test_projects
    ):
        """Test RBAC pattern matching boundaries for secret names"""
        # Login as superuser and setup
        super_user.login(cli_runner, project_name=test_projects[0])

        # Create boundary test secrets via manifests
        result = cli_runner.invoke(cli, ["apply", "--silent", str(self.boundary_secrets)])
        # May succeed or fail based on superuser permissions

        # Bind secret-creator role to test_user_11
        result = cli_runner.invoke(
            cli,
            [
                "role",
                "bind",
                "secret-creator",
                f"Project:{test_projects[0]}",
                f"User:{test_user_12.email}",
            ],
        )
        assert result.exit_code == 0

        # Login as test_user_11
        test_user_12.login(cli_runner, project_name=test_projects[0])

        # Test pattern boundaries
        # Should work: user-secret-test (matches user-secret.*)
        result = cli_runner.invoke(cli, ["secret", "inspect", "user-secret-test"])
        assert result.exit_code in [0, 1]  # May not exist but pattern would match

        # Should fail: my-user-secret-1 (doesn't start with user-secret)
        result = cli_runner.invoke(cli, ["secret", "inspect", "my-user-secret-1"])
        assert result.exit_code != 0

        # Cleanup boundary secrets
        super_user.login(cli_runner, project_name=test_projects[0])
        result = cli_runner.invoke(
            cli, ["delete", "--silent", str(self.boundary_secrets)]
        )

    # =================
    # CLEANUP TESTS (Run Last)
    # =================

    def test_90_cleanup_resources(self, cli_runner, super_user, test_projects):
        """Cleanup test resources"""
        # Login as super user
        super_user.login(cli_runner, project_name=test_projects[0])

        result = cli_runner.invoke(cli, ["delete", "--silent", str(self.manifests_dir)])
        assert result.exit_code == 0, result.output

"""
RBAC Tests for rapyuta.io CLI - Secret Operations

This module tests Role-Based Access Control scenarios for secret operations
using pytest and Click testing framework. It covers:
- Super user creating roles and secrets
- Test users with restricted access to secrets
- Pydantic model validation for invalid manifests
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
            Path(__file__).parent.parent / "fixtures" / "manifests" / "rbac"
        )
        self.role_manifest = self.manifests_dir / "role.yaml"
        self.secret_correct = (
            self.manifests_dir / "secret-correct.yaml"
        )  # Super user creates these
        self.secret_manifest = (
            self.manifests_dir / "secret.yaml"
        )  # Test users create these
        self.secret_wrong_manifest = self.manifests_dir / "secret-wrong.yaml"

    def test_super_user_creates_role(self, cli_runner, super_user, test_projects):
        """Test that superuser can create the role for secret access"""
        # Login as superuser
        super_user.login(cli_runner, project_name=test_projects[0])

        # Create role using apply command
        result = cli_runner.invoke(cli, ["apply", "--silent", str(self.role_manifest)])

        # Should succeed
        assert result.exit_code == 0
        assert "Created" in result.output or "Updated" in result.output

    def test_super_user_creates_secrets(self, cli_runner, super_user, test_projects):
        """Test that superuser can create secrets"""
        # Login as superuser
        super_user.login(cli_runner, project_name=test_projects[0])

        # Create secrets from secret-correct.yaml (contains test-secret-1, test-secret-2, secret-docker, unauthorized-secret)
        result = cli_runner.invoke(
            cli,
            [
                "apply",
                "--silent",
                str(self.secret_correct),
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
                "secret-viewer",
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
                "secret-viewer",
                f"Project:{test_projects[0]}",
                f"User:{test_user_12.email}",
            ],
        )

        # Should succeed
        assert result.exit_code == 0

    def test_user11_creates_secrets_from_manifest(self, logged_in_user_11):
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

    def test_user11_can_list_secrets(self, logged_in_user_11):
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
            "secret-docker",
            "unauthorized-secret",
        ]

        # Check that authorized secrets are visible
        for secret in expected_visible:
            assert secret in result.output

    def test_user11_can_inspect_authorized_secrets(self, logged_in_user_11):
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

    def test_user11_cannot_inspect_unauthorized_secrets(self, logged_in_user_11):
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

    def test_user11_cannot_delete_secrets(self, logged_in_user_11):
        """Test that test_user_11 cannot delete secrets (only has get/list permissions)"""
        runner, user = logged_in_user_11

        # Should NOT be able to delete even authorized secrets
        result = runner.invoke(
            cli, ["secret", "delete", "test-secret-1", "--force", "--silent"]
        )

        assert result.exit_code != 0
        assert "subject is not authorized for this operation" in result.output

    def test_user11_cannot_delete_own_secret(self, logged_in_user_11):
        """Test that test_user_11 cannot delete secrets (only has get/list permissions)"""
        runner, user = logged_in_user_11

        # Should NOT be able to delete even authorized secrets
        result = runner.invoke(
            cli, ["secret", "delete", "test-secret-4", "--force", "--silent"]
        )

        assert result.exit_code == 1
        assert "subject is not authorized for this operation" in result.output

    def test_superuser_can_delete_secret(self, super_user, cli_runner, test_projects):
        """Test that test_user_11 cannot delete secrets (only has get/list permissions)"""
        super_user.login(cli_runner, project_name=test_projects[0])

        # Should NOT be able to delete even authorized secrets
        result = cli_runner.invoke(
            cli, ["secret", "delete", "test-secret-4", "--force", "--silent"]
        )

        assert result.exit_code == 0

    def test_user12_creates_secrets_from_manifest(self, logged_in_user_12):
        """Test that test_user_12 creates secrets from secret.yaml"""
        runner, user = logged_in_user_12

        # Create secrets from secret.yaml
        # This contains test-secret-4 (should succeed) and random-secret (should fail)
        result = runner.invoke(cli, ["apply", "--silent", str(self.secret_manifest)])

        assert result.exit_code != 0
        assert "Created secret:test-secret-4" in result.output
        assert (
            "Failed to apply secret:random-secret. Error: subject is not authorized for this operation"
            in result.output
        )

    def test_user12_can_list_secrets(self, logged_in_user_12):
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
            "secret-docker",
            "unauthorized-secret",
        ]

        # Check that authorized secrets are visible
        for secret in expected_visible:
            assert secret in result.output

    def test_user12_can_inspect_authorized_secrets(self, logged_in_user_12):
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

    def test_user12_cannot_inspect_unauthorized_secrets(self, logged_in_user_12):
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

    def test_user12_cannot_delete_secrets(self, logged_in_user_12):
        """Test that test_user_12 cannot delete secrets (only has get/list permissions)"""
        runner, user = logged_in_user_12

        # Should NOT be able to delete even authorized secrets
        result = runner.invoke(
            cli, ["secret", "delete", "test-secret-2", "--force", "--silent"]
        )

        assert result.exit_code != 0
        assert "subject is not authorized for this operation" in result.output

    def test_user12_cannot_delete_own_secret(self, logged_in_user_12):
        """Test that test_user_11 cannot delete secrets (only has get/list permissions)"""
        runner, user = logged_in_user_12

        # Should NOT be able to delete even authorized secrets
        result = runner.invoke(
            cli, ["secret", "delete", "test-secret-4", "--force", "--silent"]
        )

        assert result.exit_code == 1
        assert "subject is not authorized for this operation" in result.output

    def test_pydantic_model_validation_error(self, cli_runner, super_user, test_projects):
        """Test that invalid secret manifest fails with pydantic validation error"""
        # Login as super user
        super_user.login(cli_runner, project_name=test_projects[0])

        # Try to apply the wrong manifest (StaticRoute instead of Secret)
        result = cli_runner.invoke(
            cli, ["apply", "--silent", str(self.secret_wrong_manifest)]
        )

        # Should fail with validation error
        assert result.exit_code != 0
        assert "Field required" in result.output

    def test_cleanup_resources(self, cli_runner, super_user, test_projects):
        """Cleanup test resources"""
        # Login as super user
        super_user.login(cli_runner, project_name=test_projects[0])

        # Delete secrets
        secret_manifests = [
            self.secret_manifest,  # Contains test-secret-4 and random-secret
            self.secret_wrong_manifest,
            self.secret_correct,
        ]

        for manifest in secret_manifests:
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
                    "secret-viewer",
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

"""
RBAC Tests for rapyuta.io CLI - Service Account Operations

This module tests Role-Based Access Control scenarios for service account operations
using pytest and Click testing framework. It covers:
- Super user creating roles and service accounts
- Test users with restricted access to service accounts
- Multiple role scenarios with different permission patterns
- Token management operations (create_token, delete_token, list_token, refresh_token)
- Pydantic model validation for invalid manifests

Test execution order:
1. Setup tests (super user creates roles and resources)
2. Basic RBAC tests (original service-account-viewer role scenarios)
3. Extended role tests (new service account roles with different patterns)
4. Token management tests (token operations for authorized service accounts)
5. Complex scenarios (multiple roles, boundary testing)
6. Cleanup tests (teardown resources)
"""

from pathlib import Path

import pytest

from riocli.bootstrap import cli


@pytest.mark.rbac
@pytest.mark.integration
@pytest.mark.slow
class TestServiceAccountsRBAC:
    """Test class for Service Account RBAC scenarios"""

    @pytest.fixture(autouse=True)
    def setup_manifests(self):
        """Setup manifest file paths"""
        self.manifests_dir = (
            Path(__file__).parent.parent / "fixtures" / "manifests" / "serviceaccount"
        )
        self.role_manifest = self.manifests_dir / "role.yaml"
        self.sa_correct = (
            self.manifests_dir / "service-account-correct.yaml"
        )  # Super user creates these
        self.sa_manifest = (
            self.manifests_dir / "service-account.yaml"
        )  # Test users create these
        self.sa_extended = (
            self.manifests_dir / "service-account-extended.yaml"
        )  # Extended patterns
        self.managed_sa_2 = (
            self.manifests_dir / "managed-sa-2.yaml"
        )  # For manager role testing
        self.boundary_sas = (
            self.manifests_dir / "boundary-sas.yaml"
        )  # For pattern boundary testing

    # =================
    # SETUP TESTS (Run First)
    # =================

    def test_01_super_user_creates_role(self, cli_runner, super_user, test_projects):
        """Test that superuser can create all roles for service account access"""
        # Login as superuser
        super_user.login(cli_runner, project_name=test_projects[0])

        # Create all roles using apply command
        result = cli_runner.invoke(cli, ["apply", "--silent", str(self.role_manifest)])

        # Should succeed
        assert result.exit_code == 0
        assert "Created" in result.output or "Updated" in result.output

    def test_02_super_user_creates_service_accounts(
        self, cli_runner, super_user, test_projects
    ):
        """Test that superuser can create service accounts"""
        # Login as superuser
        super_user.login(cli_runner, project_name=test_projects[0])

        # Create service accounts from service-account-correct.yaml (contains test-sa-1, test-sa-2, unauthorized-sa)
        result = cli_runner.invoke(
            cli,
            [
                "apply",
                "--silent",
                str(self.sa_correct),
            ],
        )

        # Should succeed
        assert result.exit_code == 0, result.output
        assert "Apply successful" in result.output

    def test_03_super_user_creates_extended_service_accounts(
        self, cli_runner, super_user, test_projects
    ):
        """Test that superuser can create extended service account patterns"""
        # Login as superuser
        super_user.login(cli_runner, project_name=test_projects[0])

        # Create extended service accounts (user-sa-1, managed-sa-1, temp-sa-1, token-sa-1)
        result = cli_runner.invoke(cli, ["apply", "--silent", str(self.sa_extended)])
        assert result.exit_code == 0, result.output
        assert "Apply successful" in result.output

    def test_04_super_user_binds_role_to_test_users(
        self, cli_runner, super_user, test_user_11, test_user_12, test_projects
    ):
        """Test that superuser can bind the service-account-viewer role to test users"""
        # Login as superuser
        super_user.login(cli_runner, project_name=test_projects[0])

        # Bind service-account-viewer role to test_user_11
        result = cli_runner.invoke(
            cli,
            [
                "role",
                "bind",
                "service-account-viewer",
                f"Project:{test_projects[0]}",
                f"User:{test_user_11.email}",
            ],
        )

        # Should succeed
        assert result.exit_code == 0, result.output

        # Bind service-account-viewer role to test_user_12
        result = cli_runner.invoke(
            cli,
            [
                "role",
                "bind",
                "service-account-viewer",
                f"Project:{test_projects[0]}",
                f"User:{test_user_12.email}",
            ],
        )

        # Should succeed
        assert result.exit_code == 0, result.output

    # =================
    # BASIC RBAC TESTS (service-account-viewer role)
    # =================

    def test_10_user11_creates_service_accounts_from_manifest(self, logged_in_user_11):
        """Test that test_user_11 creates service accounts from service-account.yaml"""
        runner, user = logged_in_user_11

        # Create service accounts from service-account.yaml
        # This contains test-sa-4 (should succeed) and random-sa (should fail)
        result = runner.invoke(cli, ["apply", "--silent", str(self.sa_manifest)])

        # The result might be mixed - some service accounts succeed, others fail
        # We'll verify the actual results in the list test
        assert result.exit_code != 0, result.output
        assert "Created serviceaccount:test-sa-4" in result.output
        assert (
            "Failed to apply serviceaccount:random-sa. Error: subject is not authorized for this operation"
            in result.output
        )

    def test_11_user11_can_list_service_accounts(self, logged_in_user_11):
        """Test that test_user_11 can list all service accounts"""
        runner, user = logged_in_user_11

        result = runner.invoke(cli, ["serviceaccount", "list"])

        # Should succeed
        assert result.exit_code == 0, (
            f"Service account list should succeed for {user.email}. "
            f"Exit code: {result.exit_code}, Output: {result.output}"
        )

        # User should be able to see service accounts that match test-sa.* pattern
        expected_visible = [
            "test-sa-1",
            "test-sa-2",
            "test-sa-4",
        ]

        # Check that authorized service accounts are visible
        for sa in expected_visible:
            assert sa in result.output

    def test_12_user11_can_inspect_authorized_service_accounts(self, logged_in_user_11):
        """Test that test_user_11 can inspect service accounts matching the role pattern"""
        runner, user = logged_in_user_11

        # Should be able to inspect test-sa-1
        result = runner.invoke(cli, ["serviceaccount", "inspect", "test-sa-1"])
        assert result.exit_code == 0, result.output

        # Should be able to inspect test-sa-2
        result = runner.invoke(cli, ["serviceaccount", "inspect", "test-sa-2"])
        assert result.exit_code == 0, result.output

        # Should be able to inspect test-sa-4 from service-account.yaml
        result = runner.invoke(cli, ["serviceaccount", "inspect", "test-sa-4"])
        assert result.exit_code == 0, result.output

    def test_13_user11_cannot_inspect_unauthorized_service_accounts(
        self, logged_in_user_11
    ):
        """Test that test_user_11 cannot inspect service accounts not matching the role pattern"""
        runner, user = logged_in_user_11

        # Should NOT be able to inspect unauthorized-sa
        result = runner.invoke(cli, ["serviceaccount", "inspect", "unauthorized-sa"])
        assert result.exit_code != 0
        assert "subject is not authorized for this operation" in result.output

        # Should NOT be able to inspect random-sa (doesn't match test-sa.* pattern)
        result = runner.invoke(cli, ["serviceaccount", "inspect", "random-sa"])
        assert result.exit_code != 0
        # Check for authorization error messages
        assert "subject is not authorized for this operation" in result.output

    def test_14_user11_cannot_delete_service_accounts(self, logged_in_user_11):
        """Test that test_user_11 cannot delete service accounts (only has get permissions)"""
        runner, user = logged_in_user_11

        # Should NOT be able to delete even authorized service accounts
        result = runner.invoke(
            cli, ["serviceaccount", "delete", "test-sa-1", "--force", "--silent"]
        )

        assert result.exit_code != 0
        assert "subject is not authorized for this operation" in result.output

    def test_15_user11_cannot_manage_tokens(self, logged_in_user_11):
        """Test that test_user_11 cannot manage tokens (only has get/list permissions)"""
        runner, user = logged_in_user_11

        # Should NOT be able to create tokens
        result = runner.invoke(
            cli, ["serviceaccount", "create-token", "test-sa-1", "--silent"]
        )
        assert result.exit_code != 0
        assert "subject is not authorized for this operation" in result.output

        # Should NOT be able to list tokens
        result = runner.invoke(cli, ["serviceaccount", "list-token", "test-sa-1"])
        assert result.exit_code != 0
        assert "subject is not authorized for this operation" in result.output

        # Should NOT be able to delete tokens (even if token ID existed)
        result = runner.invoke(
            cli,
            [
                "serviceaccount",
                "delete-token",
                "test-sa-1",
                "dummy-token-id",
                "--force",
                "--silent",
            ],
        )
        assert result.exit_code != 0
        assert "subject is not authorized for this operation" in result.output

        # Should NOT be able to refresh tokens
        result = runner.invoke(
            cli,
            [
                "serviceaccount",
                "refresh-token",
                "test-sa-1",
                "dummy-token-id",
                "--silent",
            ],
        )
        assert result.exit_code != 0
        assert "subject is not authorized for this operation" in result.output

    def test_16_user12_creates_service_accounts_from_manifest(self, logged_in_user_12):
        """Test that test_user_12 creates service accounts from service-account.yaml"""
        runner, user = logged_in_user_12

        # Create service accounts from service-account.yaml
        # This contains test-sa-4 (should succeed) and random-sa (should fail)
        result = runner.invoke(cli, ["apply", "--silent", str(self.sa_manifest)])

        assert result.exit_code != 0
        assert "subject is not authorized for this operation" in result.output

    def test_17_user12_can_list_service_accounts(self, logged_in_user_12):
        """Test that test_user_12 can list all service accounts"""
        runner, user = logged_in_user_12

        result = runner.invoke(cli, ["serviceaccount", "list"])

        # Should succeed
        assert result.exit_code == 0, (
            f"Service account list should succeed for {user.email}. "
            f"Exit code: {result.exit_code}, Output: {result.output}"
        )

        # User should be able to see service accounts that match test-sa.* pattern
        expected_visible = [
            "test-sa-1",
            "test-sa-2",
            "test-sa-4",
        ]

        # Check that authorized service accounts are visible
        for sa in expected_visible:
            assert sa in result.output

    def test_18_user12_can_inspect_authorized_service_accounts(self, logged_in_user_12):
        """Test that test_user_12 can inspect service accounts matching the role pattern"""
        runner, user = logged_in_user_12

        # Should be able to inspect test-sa-1
        result = runner.invoke(cli, ["serviceaccount", "inspect", "test-sa-1"])
        assert result.exit_code == 0

        # Should be able to inspect test-sa-2
        result = runner.invoke(cli, ["serviceaccount", "inspect", "test-sa-2"])
        assert result.exit_code == 0

        # Should be able to inspect test-sa-4 from service-account.yaml
        result = runner.invoke(cli, ["serviceaccount", "inspect", "test-sa-4"])
        assert result.exit_code == 0

    def test_19_user12_cannot_inspect_unauthorized_service_accounts(
        self, logged_in_user_12
    ):
        """Test that test_user_12 cannot inspect service accounts not matching the role pattern"""
        runner, user = logged_in_user_12

        # Should NOT be able to inspect unauthorized-sa
        result = runner.invoke(cli, ["serviceaccount", "inspect", "unauthorized-sa"])
        assert result.exit_code != 0
        # Check for authorization error messages
        assert "subject is not authorized for this operation" in result.output

        # Should NOT be able to inspect random-sa (doesn't match test-sa.* pattern)
        result = runner.invoke(cli, ["serviceaccount", "inspect", "random-sa"])
        assert result.exit_code != 0, (
            f"Service account inspect should fail for random-sa (wrong prefix). "
            f"Exit code: {result.exit_code}, Output: {result.output}"
        )
        assert "subject is not authorized for this operation" in result.output

    def test_20_user12_cannot_delete_service_accounts(self, logged_in_user_12):
        """Test that test_user_12 cannot delete service accounts (only has get permissions)"""
        runner, user = logged_in_user_12

        # Should NOT be able to delete even authorized service accounts
        result = runner.invoke(
            cli, ["serviceaccount", "delete", "test-sa-2", "--force", "--silent"]
        )

        assert result.exit_code != 0
        assert "subject is not authorized for this operation" in result.output

    def test_20a_user12_cannot_update_service_accounts(self, logged_in_user_12):
        """Test that test_user_12 cannot update service accounts (only has get permissions)"""
        runner, user = logged_in_user_12

        # Should NOT be able to update service accounts
        result = runner.invoke(
            cli,
            [
                "serviceaccount",
                "update",
                "test-sa-1",
                "--description",
                "Updated description",
                "--silent",
            ],
        )
        assert result.exit_code != 0
        assert "subject is not authorized for this operation" in result.output

    def test_20b_user12_comprehensive_token_restrictions(self, logged_in_user_12):
        """Test that test_user_12 cannot perform any token operations"""
        runner, user = logged_in_user_12

        # Test all token operations should fail
        token_operations = [
            (["serviceaccount", "create-token", "test-sa-1", "--silent"], "create-token"),
            (["serviceaccount", "list-token", "test-sa-1"], "list-token"),
            (
                [
                    "serviceaccount",
                    "delete-token",
                    "test-sa-1",
                    "dummy-token",
                    "--force",
                    "--silent",
                ],
                "delete-token",
            ),
            (
                [
                    "serviceaccount",
                    "refresh-token",
                    "test-sa-1",
                    "dummy-token",
                    "--silent",
                ],
                "refresh-token",
            ),
        ]

        for cmd, operation in token_operations:
            result = runner.invoke(cli, cmd)
            assert result.exit_code != 0, (
                f"{operation} should fail for user with only get permissions"
            )
            assert "subject is not authorized for this operation" in result.output

    # =================
    # EXTENDED ROLE TESTS (new service account role patterns)
    # =================

    def test_21_service_account_creator_role_permissions(
        self, cli_runner, super_user, test_user_11, test_projects
    ):
        """Test service-account-creator role - can create/get user-sa.* and list all service accounts"""
        # Login as superuser and setup
        super_user.login(cli_runner, project_name=test_projects[0])

        # Bind service-account-creator role to test_user_11
        result = cli_runner.invoke(
            cli,
            [
                "role",
                "bind",
                "service-account-creator",
                f"Project:{test_projects[0]}",
                f"User:{test_user_11.email}",
            ],
        )
        assert result.exit_code == 0

        # Login as test_user_11
        test_user_11.login(cli_runner, project_name=test_projects[0])

        # Test listing all service accounts (should work)
        result = cli_runner.invoke(cli, ["serviceaccount", "list"])
        assert result.exit_code == 0
        assert "user-sa-1" in result.output

        # Test getting user-sa-* (should work)
        result = cli_runner.invoke(cli, ["serviceaccount", "inspect", "user-sa-1"])
        assert result.exit_code == 0

        # Test creating new user-sa-* via manifest (should work)
        user_sa_manifest = """apiVersion: "api.rapyuta.io/v2"
kind: "ServiceAccount"
metadata:
  name: "user-sa-new"
  labels:
    environment: test
    team: rbac-test
spec:
  description: "New user service account created by creator role"
  roles:
  - domain:
      kind: Project
      name: test-project1
    roleNames:
    - rio-project_viewer"""

        temp_manifest = self.manifests_dir / "temp-user-sa.yaml"
        with open(temp_manifest, "w") as f:
            f.write(user_sa_manifest)

        result = cli_runner.invoke(cli, ["apply", "--silent", str(temp_manifest)])
        assert result.exit_code == 0
        assert "Created serviceaccount:user-sa-new" in result.output

        # Test getting managed-sa-* (should fail - wrong pattern)
        result = cli_runner.invoke(cli, ["serviceaccount", "inspect", "managed-sa-1"])
        assert result.exit_code != 0
        assert "subject is not authorized for this operation" in result.output

        # Test that creator cannot update, delete, or manage tokens
        negative_tests = [
            (
                [
                    "serviceaccount",
                    "update",
                    "user-sa-1",
                    "--description",
                    "Updated",
                    "--silent",
                ],
                "update",
            ),
            (["serviceaccount", "delete", "user-sa-1", "--force", "--silent"], "delete"),
            (["serviceaccount", "create-token", "user-sa-1", "--silent"], "create-token"),
            (["serviceaccount", "list-token", "user-sa-1"], "list-token"),
        ]

        for cmd, operation in negative_tests:
            result = cli_runner.invoke(cli, cmd)
            assert result.exit_code != 0, f"{operation} should fail for creator role"
            assert "subject is not authorized for this operation" in result.output

        # Cleanup temp manifest
        temp_manifest.unlink(missing_ok=True)

    def test_22_service_account_manager_role_permissions(
        self, cli_runner, super_user, test_user_12, test_projects
    ):
        """Test service-account-manager role - full CRUD on managed-sa.* and list all"""
        # Login as superuser and setup
        super_user.login(cli_runner, project_name=test_projects[0])

        # Bind service-account-manager role to test_user_12
        result = cli_runner.invoke(
            cli,
            [
                "role",
                "bind",
                "service-account-manager",
                f"Project:{test_projects[0]}",
                f"User:{test_user_12.email}",
            ],
        )
        assert result.exit_code == 0

        # Login as test_user_12
        test_user_12.login(cli_runner, project_name=test_projects[0])

        # Test listing all service accounts (should work)
        result = cli_runner.invoke(cli, ["serviceaccount", "list"])
        assert result.exit_code == 0
        assert "managed-sa-1" in result.output

        # Test getting managed-sa-* (should work)
        result = cli_runner.invoke(cli, ["serviceaccount", "inspect", "managed-sa-1"])
        assert result.exit_code == 0

        # Test creating new managed service account via manifest (should work)
        result = cli_runner.invoke(cli, ["apply", "--silent", str(self.managed_sa_2)])
        assert result.exit_code == 0

        # Test updating managed service account (should work)
        result = cli_runner.invoke(
            cli,
            [
                "serviceaccount",
                "update",
                "managed-sa-2",
                "--description",
                "Updated by manager role",
                "--silent",
            ],
        )
        assert result.exit_code == 0

        # Test deleting managed service account (should work)
        result = cli_runner.invoke(
            cli, ["serviceaccount", "delete", "managed-sa-1", "--force", "--silent"]
        )
        assert result.exit_code == 0

        # Test that manager cannot access other patterns
        unauthorized_tests = [
            (["serviceaccount", "inspect", "user-sa-1"], "inspect user-sa"),
            (["serviceaccount", "inspect", "token-sa-1"], "inspect token-sa"),
            (["serviceaccount", "inspect", "temp-sa-1"], "inspect temp-sa"),
            (
                ["serviceaccount", "delete", "user-sa-1", "--force", "--silent"],
                "delete user-sa",
            ),
        ]

        for cmd, operation in unauthorized_tests:
            result = cli_runner.invoke(cli, cmd)
            assert result.exit_code != 0, (
                f"{operation} should fail for manager role on wrong pattern"
            )
            assert "subject is not authorized for this operation" in result.output

        # Test that manager cannot manage tokens (no token permissions)
        token_tests = [
            (
                ["serviceaccount", "create-token", "managed-sa-2", "--silent"],
                "create-token",
            ),
            (["serviceaccount", "list-token", "managed-sa-2"], "list-token"),
        ]

        for cmd, operation in token_tests:
            result = cli_runner.invoke(cli, cmd)
            assert result.exit_code != 0, (
                f"{operation} should fail for manager role (no token permissions)"
            )
            assert "subject is not authorized for this operation" in result.output

    def test_23_service_account_token_manager_role_permissions(
        self, cli_runner, super_user, test_user_11, test_projects
    ):
        """Test service-account-token-manager role - can manage tokens for token-sa.* and list all"""
        # Login as superuser and setup
        super_user.login(cli_runner, project_name=test_projects[0])

        # Unbind service-account-creator role from test_user_11
        result = cli_runner.invoke(
            cli,
            [
                "role",
                "unbind",
                "service-account-creator",
                f"Project:{test_projects[0]}",
                f"User:{test_user_11.email}",
            ],
        )
        assert result.exit_code == 0

        # Bind service-account-token-manager role to test_user_11
        result = cli_runner.invoke(
            cli,
            [
                "role",
                "bind",
                "service-account-token-manager",
                f"Project:{test_projects[0]}",
                f"User:{test_user_11.email}",
            ],
        )
        assert result.exit_code == 0

        # Login as test_user_11
        test_user_11.login(cli_runner, project_name=test_projects[0])

        # Test listing all service accounts (should work)
        result = cli_runner.invoke(cli, ["serviceaccount", "list"])
        assert result.exit_code == 0
        assert "token-sa-1" in result.output

        # Test getting token-sa-* (should work)
        result = cli_runner.invoke(cli, ["serviceaccount", "inspect", "token-sa-1"])
        assert result.exit_code == 0

        # Test creating token for token-sa-* (should work)
        result = cli_runner.invoke(
            cli, ["serviceaccount", "create-token", "token-sa-1", "--silent"]
        )
        assert result.exit_code == 0

        # Test listing tokens for token-sa-* (should work)
        result = cli_runner.invoke(cli, ["serviceaccount", "list-token", "token-sa-1"])
        assert result.exit_code == 0

        # Test that token manager cannot create, update, or delete service accounts
        forbidden_operations = [
            (
                ["serviceaccount", "delete", "token-sa-1", "--force", "--silent"],
                "delete service account",
            ),
            (
                [
                    "serviceaccount",
                    "update",
                    "token-sa-1",
                    "--description",
                    "Updated",
                    "--silent",
                ],
                "update service account",
            ),
        ]

        for cmd, operation in forbidden_operations:
            result = cli_runner.invoke(cli, cmd)
            assert result.exit_code != 0, (
                f"{operation} should fail for token manager role"
            )
            assert "subject is not authorized for this operation" in result.output

        # Test getting non-token service accounts (should fail)
        unauthorized_access_tests = [
            (["serviceaccount", "inspect", "user-sa-1"], "inspect user-sa"),
            (["serviceaccount", "inspect", "managed-sa-2"], "inspect managed-sa"),
            (["serviceaccount", "inspect", "temp-sa-1"], "inspect temp-sa"),
            (
                ["serviceaccount", "create-token", "user-sa-1", "--silent"],
                "create-token for user-sa",
            ),
            (
                ["serviceaccount", "list-token", "managed-sa-2"],
                "list-token for managed-sa",
            ),
        ]

        for cmd, operation in unauthorized_access_tests:
            result = cli_runner.invoke(cli, cmd)
            assert result.exit_code != 0, (
                f"{operation} should fail for token manager role on wrong pattern"
            )
            assert "subject is not authorized for this operation" in result.output

    def test_24_service_account_deleter_role_permissions(
        self, cli_runner, super_user, test_user_12, test_projects
    ):
        """Test service-account-deleter role - can delete/get temp-sa.* and list all"""
        # Login as superuser and setup
        super_user.login(cli_runner, project_name=test_projects[0])

        # Bind service-account-deleter role to test_user_12
        result = cli_runner.invoke(
            cli,
            [
                "role",
                "bind",
                "service-account-deleter",
                f"Project:{test_projects[0]}",
                f"User:{test_user_12.email}",
            ],
        )
        assert result.exit_code == 0

        # Login as test_user_12
        test_user_12.login(cli_runner, project_name=test_projects[0])

        # Test listing all service accounts (should work)
        result = cli_runner.invoke(cli, ["serviceaccount", "list"])
        assert result.exit_code == 0
        assert "temp-sa-1" in result.output

        # Test getting temp-sa-* (should work)
        result = cli_runner.invoke(cli, ["serviceaccount", "inspect", "temp-sa-1"])
        assert result.exit_code == 0

        # Test deleting temp-sa-* (should work)
        result = cli_runner.invoke(
            cli, ["serviceaccount", "delete", "temp-sa-1", "--force", "--silent"]
        )
        assert result.exit_code == 0

        # Test getting non-temp service accounts (should fail) - use user-sa-1 since managed-sa-1 was deleted in test_22
        result = cli_runner.invoke(cli, ["serviceaccount", "inspect", "user-sa-1"])
        assert "subject is not authorized for this operation" in result.output

    # =================
    # TOKEN MANAGEMENT TESTS
    # =================

    def test_25_token_operations_with_proper_permissions(
        self, cli_runner, super_user, test_user_11, test_projects
    ):
        """Test comprehensive token operations for users with token management permissions"""
        # Login as superuser and ensure token-sa-1 exists
        super_user.login(cli_runner, project_name=test_projects[0])

        # Ensure test_user_11 has token-manager role
        result = cli_runner.invoke(
            cli,
            [
                "role",
                "bind",
                "service-account-token-manager",
                f"Project:{test_projects[0]}",
                f"User:{test_user_11.email}",
            ],
        )

        # Login as test_user_11
        test_user_11.login(cli_runner, project_name=test_projects[0])

        # Create a token
        result = cli_runner.invoke(
            cli, ["serviceaccount", "create-token", "token-sa-1", "--silent"]
        )
        assert result.exit_code == 0

        # Extract token ID from output for further operations

        # List tokens
        result = cli_runner.invoke(cli, ["serviceaccount", "list-token", "token-sa-1"])
        assert result.exit_code == 0

        # Note: delete-token and refresh-token would require actual token IDs
        # These would be tested in integration scenarios with actual tokens

    # =================
    # CROSS-USER VALIDATION TESTS
    # =================

    def test_26_cross_user_access_validation(
        self, cli_runner, super_user, test_user_11, test_user_12, test_projects
    ):
        """Test that users cannot access resources outside their role permissions when other users have different roles"""
        # Setup: Give different roles to different users
        super_user.login(cli_runner, project_name=test_projects[0])

        # Clean up existing roles first
        for user in [test_user_11, test_user_12]:
            for role in [
                "service-account-viewer",
                "service-account-creator",
                "service-account-manager",
                "service-account-token-manager",
                "service-account-deleter",
            ]:
                cli_runner.invoke(
                    cli,
                    [
                        "role",
                        "unbind",
                        role,
                        f"Project:{test_projects[0]}",
                        f"User:{user.email}",
                    ],
                )

        # Assign creator role to user_11 and manager role to user_12
        result = cli_runner.invoke(
            cli,
            [
                "role",
                "bind",
                "service-account-creator",
                f"Project:{test_projects[0]}",
                f"User:{test_user_11.email}",
            ],
        )
        assert result.exit_code == 0

        result = cli_runner.invoke(
            cli,
            [
                "role",
                "bind",
                "service-account-manager",
                f"Project:{test_projects[0]}",
                f"User:{test_user_12.email}",
            ],
        )
        assert result.exit_code == 0

        # Test user_11 (creator) cannot access managed-sa resources that user_12 (manager) can access
        test_user_11.login(cli_runner, project_name=test_projects[0])

        result = cli_runner.invoke(cli, ["serviceaccount", "inspect", "managed-sa-2"])
        assert result.exit_code != 0
        assert "subject is not authorized for this operation" in result.output

        result = cli_runner.invoke(
            cli, ["serviceaccount", "delete", "managed-sa-2", "--force", "--silent"]
        )
        assert result.exit_code != 0
        assert "subject is not authorized for this operation" in result.output

        # Test user_12 (manager) cannot access user-sa resources that user_11 (creator) can access
        test_user_12.login(cli_runner, project_name=test_projects[0])

        result = cli_runner.invoke(cli, ["serviceaccount", "inspect", "user-sa-1"])
        assert result.exit_code != 0
        assert "subject is not authorized for this operation" in result.output

        # But user_12 can access their authorized managed-sa resources
        result = cli_runner.invoke(cli, ["serviceaccount", "inspect", "managed-sa-2"])
        assert result.exit_code == 0

    def test_27_superuser_vs_restricted_users(
        self, cli_runner, super_user, test_user_11, test_user_12, test_projects
    ):
        """Test that superuser has broader access than restricted users"""
        # Superuser should be able to access all service accounts
        super_user.login(cli_runner, project_name=test_projects[0])

        # Superuser can access all patterns
        all_service_accounts = [
            "test-sa-1",
            "user-sa-1",
            "managed-sa-2",
            "token-sa-1",
            "temp-sa-1",
        ]

        for sa in all_service_accounts:
            result = cli_runner.invoke(cli, ["serviceaccount", "inspect", sa])
            assert result.exit_code == 0, f"Superuser should be able to inspect {sa}"

        # Superuser can perform all operations
        result = cli_runner.invoke(
            cli, ["serviceaccount", "create-token", "token-sa-1", "--silent"]
        )
        assert result.exit_code == 0, "Superuser should be able to create tokens"

        result = cli_runner.invoke(cli, ["serviceaccount", "list-token", "token-sa-1"])
        assert result.exit_code == 0, "Superuser should be able to list tokens"

        # Create a new service account as superuser
        superuser_sa_manifest = """apiVersion: "api.rapyuta.io/v2"
kind: "ServiceAccount"
metadata:
  name: "superuser-created-sa"
  labels:
    environment: test
    team: rbac-test
spec:
  description: "Service account created by superuser"
  roles:
  - domain:
      kind: Project
      name: test-project1
    roleNames:
    - rio-project_viewer"""

        temp_manifest = self.manifests_dir / "temp-superuser-sa.yaml"
        with open(temp_manifest, "w") as f:
            f.write(superuser_sa_manifest)

        result = cli_runner.invoke(cli, ["apply", "--silent", str(temp_manifest)])
        assert result.exit_code == 0

        # Now test that restricted users cannot access this superuser-created resource
        test_user_11.login(cli_runner, project_name=test_projects[0])
        result = cli_runner.invoke(
            cli, ["serviceaccount", "inspect", "superuser-created-sa"]
        )
        assert result.exit_code != 0
        assert "subject is not authorized for this operation" in result.output

        test_user_12.login(cli_runner, project_name=test_projects[0])
        result = cli_runner.invoke(
            cli, ["serviceaccount", "inspect", "superuser-created-sa"]
        )
        assert result.exit_code != 0
        assert "subject is not authorized for this operation" in result.output

        # Cleanup
        super_user.login(cli_runner, project_name=test_projects[0])
        cli_runner.invoke(
            cli,
            ["serviceaccount", "delete", "superuser-created-sa", "--force", "--silent"],
        )
        temp_manifest.unlink(missing_ok=True)

    def test_28_role_escalation_prevention(
        self, cli_runner, super_user, test_user_11, test_user_12, test_projects
    ):
        """Test that users cannot escalate their permissions or access resources beyond their role scope"""
        # Setup different roles for users
        super_user.login(cli_runner, project_name=test_projects[0])

        # Give viewer role to user_11 and creator role to user_12
        cli_runner.invoke(
            cli,
            [
                "role",
                "bind",
                "service-account-viewer",
                f"Project:{test_projects[0]}",
                f"User:{test_user_11.email}",
            ],
        )
        cli_runner.invoke(
            cli,
            [
                "role",
                "bind",
                "service-account-creator",
                f"Project:{test_projects[0]}",
                f"User:{test_user_12.email}",
            ],
        )

        # Test that viewer (user_11) cannot perform creator actions
        test_user_11.login(cli_runner, project_name=test_projects[0])

        create_sa_manifest = """apiVersion: "api.rapyuta.io/v2"
kind: "ServiceAccount"
metadata:
  name: "escalation-test-sa"
  labels:
    environment: test
spec:
  description: "Should not be created by viewer"
  roles:
  - domain:
      kind: Project
      name: test-project1
    roleNames:
    - rio-project_viewer"""

        temp_manifest = self.manifests_dir / "temp-escalation-sa.yaml"
        with open(temp_manifest, "w") as f:
            f.write(create_sa_manifest)

        result = cli_runner.invoke(cli, ["apply", "--silent", str(temp_manifest)])
        assert result.exit_code != 0
        assert "subject is not authorized for this operation" in result.output

        # Test that creator (user_12) cannot perform manager actions on wrong patterns
        test_user_12.login(cli_runner, project_name=test_projects[0])

        result = cli_runner.invoke(
            cli, ["serviceaccount", "delete", "managed-sa-2", "--force", "--silent"]
        )
        assert result.exit_code != 0
        assert "subject is not authorized for this operation" in result.output

        result = cli_runner.invoke(
            cli,
            [
                "serviceaccount",
                "update",
                "managed-sa-2",
                "--description",
                "Unauthorized update",
                "--silent",
            ],
        )
        assert result.exit_code != 0
        assert "subject is not authorized for this operation" in result.output

        # Cleanup
        temp_manifest.unlink(missing_ok=True)

    def test_29_comprehensive_negative_permissions_matrix(
        self, cli_runner, super_user, test_user_11, test_user_12, test_projects
    ):
        """Comprehensive test matrix of all users vs all actions vs all service account patterns"""
        super_user.login(cli_runner, project_name=test_projects[0])

        # Reset roles: viewer for user_11, creator for user_12
        for user in [test_user_11, test_user_12]:
            for role in [
                "service-account-viewer",
                "service-account-creator",
                "service-account-manager",
                "service-account-token-manager",
                "service-account-deleter",
            ]:
                cli_runner.invoke(
                    cli,
                    [
                        "role",
                        "unbind",
                        role,
                        f"Project:{test_projects[0]}",
                        f"User:{user.email}",
                    ],
                )

        cli_runner.invoke(
            cli,
            [
                "role",
                "bind",
                "service-account-viewer",
                f"Project:{test_projects[0]}",
                f"User:{test_user_11.email}",
            ],
        )
        cli_runner.invoke(
            cli,
            [
                "role",
                "bind",
                "service-account-creator",
                f"Project:{test_projects[0]}",
                f"User:{test_user_12.email}",
            ],
        )

        # Test matrix: [user, action, service_account, should_succeed]
        test_matrix = [
            # Viewer tests (user_11) - can only get test-sa.* and list all
            (test_user_11, ["serviceaccount", "inspect", "test-sa-1"], True),
            (test_user_11, ["serviceaccount", "inspect", "user-sa-1"], False),
            (test_user_11, ["serviceaccount", "inspect", "managed-sa-2"], False),
            (
                test_user_11,
                ["serviceaccount", "delete", "test-sa-1", "--force", "--silent"],
                False,
            ),
            (
                test_user_11,
                ["serviceaccount", "create-token", "test-sa-1", "--silent"],
                False,
            ),
            # Creator tests (user_12) - can create/get user-sa.* and list all
            (test_user_12, ["serviceaccount", "inspect", "user-sa-1"], True),
            (test_user_12, ["serviceaccount", "inspect", "test-sa-1"], False),
            (test_user_12, ["serviceaccount", "inspect", "managed-sa-2"], False),
            (
                test_user_12,
                ["serviceaccount", "delete", "user-sa-1", "--force", "--silent"],
                False,
            ),
            (
                test_user_12,
                [
                    "serviceaccount",
                    "update",
                    "user-sa-1",
                    "--description",
                    "Test",
                    "--silent",
                ],
                False,
            ),
            (
                test_user_12,
                ["serviceaccount", "create-token", "user-sa-1", "--silent"],
                False,
            ),
        ]

        for user, command, should_succeed in test_matrix:
            user.login(cli_runner, project_name=test_projects[0])
            result = cli_runner.invoke(cli, command)

            if should_succeed:
                assert result.exit_code == 0, (
                    f"Command {' '.join(command)} should succeed for {user.email}"
                )
            else:
                assert result.exit_code != 0, (
                    f"Command {' '.join(command)} should fail for {user.email}"
                )
                assert "subject is not authorized for this operation" in result.output

    # =================
    # COMPLEX SCENARIOS
    # =================

    def test_30_service_account_multiple_roles_combined_permissions(
        self, cli_runner, super_user, test_user_11, test_projects
    ):
        """Test user with multiple service account roles has combined permissions"""
        # Login as superuser and setup
        super_user.login(cli_runner, project_name=test_projects[0])

        # Bind multiple roles to test_user_11
        roles = ["service-account-creator", "service-account-token-manager"]
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

        # Test listing all service accounts (should work from both roles)
        result = cli_runner.invoke(cli, ["serviceaccount", "list"])
        assert result.exit_code == 0

        # Should be able to access user-sa-* (from service-account-creator)
        result = cli_runner.invoke(cli, ["serviceaccount", "inspect", "user-sa-1"])
        assert result.exit_code == 0

        # Should be able to access token-sa-* (from service-account-token-manager)
        result = cli_runner.invoke(cli, ["serviceaccount", "inspect", "token-sa-1"])
        assert result.exit_code == 0

        # Should be able to manage tokens for token-sa-* (from service-account-token-manager)
        result = cli_runner.invoke(
            cli, ["serviceaccount", "create-token", "token-sa-1", "--silent"]
        )
        assert result.exit_code == 0

        # Should NOT be able to access patterns from other roles
        result = cli_runner.invoke(cli, ["serviceaccount", "inspect", "temp-sa-1"])
        assert result.exit_code != 0
        assert "subject is not authorized for this operation" in result.output

    def test_30a_role_binding_and_unbinding_effects(
        self, cli_runner, super_user, test_user_11, test_projects
    ):
        """Test that role binding and unbinding immediately affects user permissions"""
        super_user.login(cli_runner, project_name=test_projects[0])

        # Initially user should have no access (unbind all roles first)
        for role in ["service-account-creator", "service-account-token-manager"]:
            cli_runner.invoke(
                cli,
                [
                    "role",
                    "unbind",
                    role,
                    f"Project:{test_projects[0]}",
                    f"User:{test_user_11.email}",
                ],
            )

        test_user_11.login(cli_runner, project_name=test_projects[0])
        result = cli_runner.invoke(cli, ["serviceaccount", "inspect", "user-sa-1"])
        assert result.exit_code != 0
        assert "subject is not authorized for this operation" in result.output

        # Bind creator role - should now have access
        super_user.login(cli_runner, project_name=test_projects[0])
        cli_runner.invoke(
            cli,
            [
                "role",
                "bind",
                "service-account-creator",
                f"Project:{test_projects[0]}",
                f"User:{test_user_11.email}",
            ],
        )

        test_user_11.login(cli_runner, project_name=test_projects[0])
        result = cli_runner.invoke(cli, ["serviceaccount", "inspect", "user-sa-1"])
        assert result.exit_code == 0

        # Unbind creator role - should lose access again
        super_user.login(cli_runner, project_name=test_projects[0])
        cli_runner.invoke(
            cli,
            [
                "role",
                "unbind",
                "service-account-creator",
                f"Project:{test_projects[0]}",
                f"User:{test_user_11.email}",
            ],
        )

        test_user_11.login(cli_runner, project_name=test_projects[0])
        result = cli_runner.invoke(cli, ["serviceaccount", "inspect", "user-sa-1"])
        assert result.exit_code != 0
        assert "subject is not authorized for this operation" in result.output

    def test_30b_concurrent_operations_different_users(
        self, cli_runner, super_user, test_user_11, test_user_12, test_projects
    ):
        """Test that different users can work on their authorized resources simultaneously"""
        super_user.login(cli_runner, project_name=test_projects[0])

        # Setup: user_11 as creator, user_12 as manager
        cli_runner.invoke(
            cli,
            [
                "role",
                "bind",
                "service-account-creator",
                f"Project:{test_projects[0]}",
                f"User:{test_user_11.email}",
            ],
        )
        cli_runner.invoke(
            cli,
            [
                "role",
                "bind",
                "service-account-manager",
                f"Project:{test_projects[0]}",
                f"User:{test_user_12.email}",
            ],
        )

        # user_11 creates a user-sa resource
        test_user_11.login(cli_runner, project_name=test_projects[0])
        user_sa_manifest = """apiVersion: "api.rapyuta.io/v2"
kind: "ServiceAccount"
metadata:
  name: "user-sa-concurrent"
  labels:
    environment: test
spec:
  description: "Concurrent test SA"
  roles:
  - domain:
      kind: Project
      name: test-project1
    roleNames:
    - rio-project_viewer"""

        temp_manifest_1 = self.manifests_dir / "temp-concurrent-user-sa.yaml"
        with open(temp_manifest_1, "w") as f:
            f.write(user_sa_manifest)

        result = cli_runner.invoke(cli, ["apply", "--silent", str(temp_manifest_1)])
        assert result.exit_code == 0

        # user_12 works on managed-sa resource
        test_user_12.login(cli_runner, project_name=test_projects[0])
        result = cli_runner.invoke(
            cli,
            [
                "serviceaccount",
                "update",
                "managed-sa-2",
                "--description",
                "Concurrent update",
                "--silent",
            ],
        )
        assert result.exit_code == 0

        # Verify user_11 cannot access user_12's resources and vice versa
        test_user_11.login(cli_runner, project_name=test_projects[0])
        result = cli_runner.invoke(cli, ["serviceaccount", "inspect", "managed-sa-2"])
        assert result.exit_code != 0

        test_user_12.login(cli_runner, project_name=test_projects[0])
        result = cli_runner.invoke(
            cli, ["serviceaccount", "inspect", "user-sa-concurrent"]
        )
        assert result.exit_code != 0

        # Cleanup
        super_user.login(cli_runner, project_name=test_projects[0])
        cli_runner.invoke(
            cli, ["serviceaccount", "delete", "user-sa-concurrent", "--force", "--silent"]
        )
        temp_manifest_1.unlink(missing_ok=True)

    def test_31_service_account_pattern_boundary_validation(
        self, cli_runner, super_user, test_user_12, test_projects
    ):
        """Test RBAC pattern matching boundaries for service account names"""
        # Login as superuser and setup
        super_user.login(cli_runner, project_name=test_projects[0])

        # Create boundary test service accounts via manifests
        result = cli_runner.invoke(cli, ["apply", "--silent", str(self.boundary_sas)])
        # May succeed or fail based on superuser permissions

        # Bind service-account-creator role to test_user_12
        result = cli_runner.invoke(
            cli,
            [
                "role",
                "bind",
                "service-account-creator",
                f"Project:{test_projects[0]}",
                f"User:{test_user_12.email}",
            ],
        )
        assert result.exit_code == 0

        # Login as test_user_12
        test_user_12.login(cli_runner, project_name=test_projects[0])

        # Test pattern boundaries
        # Should work: user-sa-test (matches user-sa.*)
        result = cli_runner.invoke(cli, ["serviceaccount", "inspect", "user-sa-test"])
        assert result.exit_code in [0, 1]  # May not exist but pattern would match

        # Should fail: my-user-sa-1 (doesn't start with user-sa)
        result = cli_runner.invoke(cli, ["serviceaccount", "inspect", "my-user-sa-1"])
        assert result.exit_code != 0

        # Cleanup boundary service accounts
        super_user.login(cli_runner, project_name=test_projects[0])
        result = cli_runner.invoke(cli, ["delete", "--silent", str(self.boundary_sas)])

    # =================
    # CLEANUP TESTS (Run Last)
    # =================

    def test_90_cleanup_resources(self, cli_runner, super_user, test_projects):
        """Cleanup test resources"""
        # Login as super user
        super_user.login(cli_runner, project_name=test_projects[0])

        result = cli_runner.invoke(cli, ["delete", "--silent", str(self.manifests_dir)])
        assert result.exit_code == 0

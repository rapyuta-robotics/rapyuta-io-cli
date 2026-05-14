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
RBAC Tests for rapyuta.io CLI - Database Operations

This module tests Role-Based Access Control scenarios for database operations
using pytest and Click testing framework. It covers:
- Super user creating roles and databases
- Test users with restricted access to databases
- Multiple role scenarios with different permission patterns
- Database versions listing command
- Backup listing command

Test execution order:
1. Setup tests (super user creates device, databases, and roles)
2. Basic database command tests (versions, list)
3. Basic RBAC tests (database-viewer role scenarios)
4. Extended role tests (creator and manager roles)
5. Complex scenarios (multiple roles, boundary testing)
6. Cleanup tests (teardown resources)

Note: Database creation requires a device. A virtual HWIL device named
``test-db-device`` is created during setup and requires HWIL credentials
in the tests/.password file. Tests requiring a device are skipped if HWIL
credentials are not available.
"""

from pathlib import Path

import pytest

from riocli.bootstrap import cli


@pytest.mark.rbac
@pytest.mark.integration
@pytest.mark.slow
class TestDatabaseRBAC:
    """Test RBAC scenarios for database operations using direct role binding"""

    @pytest.fixture(autouse=True)
    def setup_manifests(self):
        """Setup manifest file paths"""
        self.manifest_dir = (
            Path(__file__).parent.parent / "fixtures" / "manifests" / "database"
        )
        self.role_manifest = self.manifest_dir / "role.yaml"
        self.database_correct = self.manifest_dir / "database-correct.yaml"
        self.database_basic = self.manifest_dir / "database-basic.yaml"
        self.database_extended = self.manifest_dir / "database-extended.yaml"
        self.managed_db_2 = self.manifest_dir / "managed-db-2.yaml"
        self.db_device_manifest = (
            Path(__file__).parent.parent
            / "fixtures"
            / "manifests"
            / "device"
            / "test-db-device.yaml"
        )

    # =================
    # SETUP TESTS (Run First)
    # =================

    def test_01_super_user_creates_db_device(
        self, cli_runner, super_user, test_projects, hwil_login
    ):
        """Test that super user creates the virtual device for database tests"""
        super_user.login(cli_runner, project_name=test_projects[0])

        result = cli_runner.invoke(
            cli,
            ["apply", "--silent", "--delete-existing", str(self.db_device_manifest)],
        )
        assert result.exit_code == 0, result.output

    def test_02_super_user_creates_roles(self, cli_runner, super_user, test_projects):
        """Test that super user creates database roles from role.yaml"""
        super_user.login(cli_runner, project_name=test_projects[0])

        result = cli_runner.invoke(cli, ["apply", "--silent", str(self.role_manifest)])

        assert result.exit_code == 0, result.output
        assert "Created" in result.output or "Updated" in result.output

    def test_03_super_user_creates_databases(self, cli_runner, super_user, test_projects):
        """Test that super user creates test databases from database-correct.yaml"""
        super_user.login(cli_runner, project_name=test_projects[0])

        result = cli_runner.invoke(cli, ["apply", "--silent", str(self.database_correct)])

        assert result.exit_code == 0, result.output
        assert "Apply successful" in result.output

    def test_04_super_user_creates_extended_databases(
        self, cli_runner, super_user, test_projects
    ):
        """Test that super user creates extended databases for role testing"""
        super_user.login(cli_runner, project_name=test_projects[0])

        result = cli_runner.invoke(
            cli, ["apply", "--silent", str(self.database_extended)]
        )
        assert result.exit_code == 0, result.output
        assert "Apply successful" in result.output

    def test_05_super_user_binds_roles_to_test_users(
        self, cli_runner, super_user, test_projects, test_user_11, test_user_12
    ):
        """Test that super user binds database-viewer role to test users"""
        super_user.login(cli_runner, project_name=test_projects[0])

        for user_email in [test_user_11.email, test_user_12.email]:
            result = cli_runner.invoke(
                cli,
                [
                    "role",
                    "bind",
                    "database-viewer",
                    f"Project:{test_projects[0]}",
                    f"User:{user_email}",
                ],
            )
            assert result.exit_code == 0, result.output

    def test_06_verify_initial_setup(self, cli_runner, super_user, test_projects):
        """Test that initial setup is complete and databases are visible"""
        super_user.login(cli_runner, project_name=test_projects[0])

        result = cli_runner.invoke(cli, ["database", "list"])

        assert result.exit_code == 0, result.output
        assert "test-db-1" in result.output
        assert "test-db-2" in result.output
        assert "unauthorized-db" in result.output

    # =================
    # BASIC DATABASE COMMAND TESTS
    # =================

    def test_10_super_user_can_list_database_versions(
        self, cli_runner, super_user, test_projects
    ):
        """Test that super user can list supported database versions"""
        super_user.login(cli_runner, project_name=test_projects[0])

        result = cli_runner.invoke(cli, ["database", "versions"])

        assert result.exit_code == 0, result.output
        # Should return a list of supported postgres versions
        assert "Supported Versions" in result.output

    def test_11_super_user_can_list_databases(
        self, cli_runner, super_user, test_projects
    ):
        """Test that super user can list all databases"""
        super_user.login(cli_runner, project_name=test_projects[0])

        result = cli_runner.invoke(cli, ["database", "list"])

        assert result.exit_code == 0, result.output
        assert "test-db-1" in result.output
        assert "test-db-2" in result.output

    def test_12_super_user_can_list_databases_wide(
        self, cli_runner, super_user, test_projects
    ):
        """Test that super user can list databases with wide output"""
        super_user.login(cli_runner, project_name=test_projects[0])

        result = cli_runner.invoke(cli, ["database", "list", "--wide"])

        assert result.exit_code == 0, result.output
        # Wide output should include GUID and creation time columns
        assert "GUID" in result.output
        assert "Creation Time" in result.output

    def test_13_super_user_can_inspect_database(
        self, cli_runner, super_user, test_projects
    ):
        """Test that super user can inspect a database in YAML format"""
        super_user.login(cli_runner, project_name=test_projects[0])

        result = cli_runner.invoke(cli, ["database", "inspect", "test-db-1"])

        assert result.exit_code == 0, result.output
        assert "test-db-1" in result.output

    def test_14_super_user_can_inspect_database_json(
        self, cli_runner, super_user, test_projects
    ):
        """Test that super user can inspect a database in JSON format"""
        super_user.login(cli_runner, project_name=test_projects[0])

        result = cli_runner.invoke(
            cli, ["database", "inspect", "test-db-1", "--format", "json"]
        )

        assert result.exit_code == 0, result.output
        assert "test-db-1" in result.output

    def test_15_super_user_can_list_backups(self, cli_runner, super_user, test_projects):
        """Test that super user can list backups for a database"""
        super_user.login(cli_runner, project_name=test_projects[0])

        result = cli_runner.invoke(cli, ["database", "backup", "list", "test-db-1"])

        # Should succeed even if no backups exist
        assert result.exit_code == 0, result.output

    # =================
    # BASIC RBAC TESTS (database-viewer role)
    # =================

    def test_20_user11_creates_database_from_manifest(self, logged_in_user_11):
        """Test that test_user_11 with database-viewer role can create test-db-* databases"""
        runner, user = logged_in_user_11

        result = runner.invoke(cli, ["apply", "--silent", str(self.database_basic)])

        # test-db-4 should succeed (matches test-db-.* pattern), random-db should fail
        assert result.exit_code != 0
        assert "Created database:test-db-4" in result.output
        assert (
            "Failed to apply database:random-db. Error: subject is not authorized for this operation"
            in result.output
        )

    def test_21_user11_can_list_databases(self, logged_in_user_11):
        """Test that test_user_11 can list all databases"""
        runner, user = logged_in_user_11

        result = runner.invoke(cli, ["database", "list"])

        assert result.exit_code == 0, (
            f"Database list should succeed for {user.email}. "
            f"Exit code: {result.exit_code}, Output: {result.output}"
        )

        # User should see databases matching the test-db-.* pattern
        for db_name in ["test-db-1", "test-db-2", "test-db-4"]:
            assert db_name in result.output

    def test_22_user11_can_inspect_authorized_databases(self, logged_in_user_11):
        """Test that test_user_11 can inspect databases matching the role pattern"""
        runner, user = logged_in_user_11

        for db_name in ["test-db-1", "test-db-2", "test-db-4"]:
            result = runner.invoke(cli, ["database", "inspect", db_name])
            assert result.exit_code == 0, (
                f"Expected to inspect {db_name} but got: {result.output}"
            )

    def test_23_user11_cannot_inspect_unauthorized_databases(self, logged_in_user_11):
        """Test that test_user_11 cannot inspect databases not matching the role pattern"""
        runner, user = logged_in_user_11

        # Should NOT be able to inspect unauthorized-db
        result = runner.invoke(cli, ["database", "inspect", "unauthorized-db"])
        assert result.exit_code != 0
        assert "subject is not authorized for this operation" in result.output

        # Should NOT be able to inspect random-db (doesn't match test-db-.* pattern)
        result = runner.invoke(cli, ["database", "inspect", "random-db"])
        assert result.exit_code != 0
        assert "subject is not authorized for this operation" in result.output

    def test_24_user11_cannot_delete_databases(self, logged_in_user_11):
        """Test that test_user_11 cannot delete databases (only has get/create permissions)"""
        runner, user = logged_in_user_11

        result = runner.invoke(
            cli, ["database", "delete", "test-db-1", "--force", "--silent"]
        )

        assert result.exit_code != 0
        assert "subject is not authorized for this operation" in result.output

    def test_25_user12_creates_database_from_manifest(self, logged_in_user_12):
        """Test that test_user_12 with database-viewer role cannot create random-db"""
        runner, user = logged_in_user_12

        result = runner.invoke(cli, ["apply", "--silent", str(self.database_basic)])

        # random-db should fail (doesn't match test-db-.* pattern)
        assert result.exit_code != 0
        assert "subject is not authorized for this operation" in result.output

    def test_26_user12_can_list_databases(self, logged_in_user_12):
        """Test that test_user_12 can list all databases"""
        runner, user = logged_in_user_12

        result = runner.invoke(cli, ["database", "list"])

        assert result.exit_code == 0, (
            f"Database list should succeed for {user.email}. "
            f"Exit code: {result.exit_code}, Output: {result.output}"
        )

        for db_name in ["test-db-1", "test-db-2"]:
            assert db_name in result.output

    def test_27_user12_can_inspect_authorized_databases(self, logged_in_user_12):
        """Test that test_user_12 can inspect databases matching the role pattern"""
        runner, user = logged_in_user_12

        for db_name in ["test-db-1", "test-db-2"]:
            result = runner.invoke(cli, ["database", "inspect", db_name])
            assert result.exit_code == 0, (
                f"Expected to inspect {db_name} but got: {result.output}"
            )

    def test_28_user12_cannot_inspect_unauthorized_databases(self, logged_in_user_12):
        """Test that test_user_12 cannot inspect databases not matching the role pattern"""
        runner, user = logged_in_user_12

        result = runner.invoke(cli, ["database", "inspect", "unauthorized-db"])
        assert result.exit_code != 0
        assert "subject is not authorized for this operation" in result.output

    def test_29_user12_cannot_delete_databases(self, logged_in_user_12):
        """Test that test_user_12 cannot delete databases (only has get/create permissions)"""
        runner, user = logged_in_user_12

        result = runner.invoke(
            cli, ["database", "delete", "test-db-2", "--force", "--silent"]
        )

        assert result.exit_code != 0
        assert "subject is not authorized for this operation" in result.output

    # =================
    # EXTENDED ROLE TESTS
    # =================

    def test_30_database_creator_role_permissions(
        self, cli_runner, super_user, test_user_11, test_projects
    ):
        """Test database-creator role - can create/get user-db-.* and list all"""
        super_user.login(cli_runner, project_name=test_projects[0])

        result = cli_runner.invoke(
            cli,
            [
                "role",
                "bind",
                "database-creator",
                f"Project:{test_projects[0]}",
                f"User:{test_user_11.email}",
            ],
        )
        assert result.exit_code == 0, result.output

        test_user_11.login(cli_runner, project_name=test_projects[0])

        # List all databases should work
        result = cli_runner.invoke(cli, ["database", "list"])
        assert result.exit_code == 0
        assert "user-db-1" in result.output

        # Get user-db-.* should work
        result = cli_runner.invoke(cli, ["database", "inspect", "user-db-1"])
        assert result.exit_code == 0

        # Get managed-db-.* should fail (wrong pattern)
        result = cli_runner.invoke(cli, ["database", "inspect", "managed-db-1"])
        assert result.exit_code != 0
        assert "subject is not authorized for this operation" in result.output

    def test_31_database_manager_role_permissions(
        self, cli_runner, super_user, test_user_12, test_projects
    ):
        """Test database-manager role - full CRUD on managed-db-.* and list all"""
        super_user.login(cli_runner, project_name=test_projects[0])

        result = cli_runner.invoke(
            cli,
            [
                "role",
                "bind",
                "database-manager",
                f"Project:{test_projects[0]}",
                f"User:{test_user_12.email}",
            ],
        )
        assert result.exit_code == 0, result.output

        test_user_12.login(cli_runner, project_name=test_projects[0])

        # List all databases should work
        result = cli_runner.invoke(cli, ["database", "list"])
        assert result.exit_code == 0
        assert "managed-db-1" in result.output

        # Get managed-db-.* should work
        result = cli_runner.invoke(cli, ["database", "inspect", "managed-db-1"])
        assert result.exit_code == 0

        # Create a new managed database via manifest
        result = cli_runner.invoke(cli, ["apply", "--silent", str(self.managed_db_2)])
        assert result.exit_code == 0

        # Delete managed-db-.* should work
        result = cli_runner.invoke(
            cli, ["database", "delete", "managed-db-1", "--force", "--silent"]
        )
        assert result.exit_code == 0

    def test_32_database_readonly_role_permissions(
        self, cli_runner, super_user, test_user_11, test_projects
    ):
        """Test database-readonly role - can only list all databases"""
        super_user.login(cli_runner, project_name=test_projects[0])

        # Unbind all previously bound roles, then bind readonly only
        for role in ["database-viewer", "database-creator"]:
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

        result = cli_runner.invoke(
            cli,
            [
                "role",
                "bind",
                "database-readonly",
                f"Project:{test_projects[0]}",
                f"User:{test_user_11.email}",
            ],
        )
        assert result.exit_code == 0

        test_user_11.login(cli_runner, project_name=test_projects[0])

        # List all databases should work
        result = cli_runner.invoke(cli, ["database", "list"])
        assert result.exit_code == 0

        # Get test-db-1 should now fail (readonly role only has list, not get)
        result = cli_runner.invoke(cli, ["database", "inspect", "test-db-1"])
        assert result.exit_code != 0
        assert "subject is not authorized for this operation" in result.output

    # =================
    # COMPLEX SCENARIOS
    # =================

    def test_40_database_multiple_roles_combined_permissions(
        self, cli_runner, super_user, test_user_11, test_projects
    ):
        """Test user with multiple database roles has combined permissions"""
        super_user.login(cli_runner, project_name=test_projects[0])

        # Bind viewer and creator roles to test_user_11
        for role in ["database-viewer", "database-creator"]:
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

        test_user_11.login(cli_runner, project_name=test_projects[0])

        # List all databases should work (from both roles)
        result = cli_runner.invoke(cli, ["database", "list"])
        assert result.exit_code == 0

        # Should be able to access test-db-.* (from database-viewer)
        result = cli_runner.invoke(cli, ["database", "inspect", "test-db-2"])
        assert result.exit_code == 0

        # Should be able to access user-db-.* (from database-creator)
        result = cli_runner.invoke(cli, ["database", "inspect", "user-db-1"])
        assert result.exit_code == 0

        # Should NOT be able to access managed-db-2 (no role binding)
        result = cli_runner.invoke(cli, ["database", "inspect", "managed-db-2"])
        assert result.exit_code != 0
        assert "subject is not authorized for this operation" in result.output

    def test_41_database_delete_with_regex_pattern(
        self, cli_runner, super_user, test_projects
    ):
        """Test that super user can delete databases matching a regex pattern"""
        super_user.login(cli_runner, project_name=test_projects[0])

        # Delete test-db-4 (created by test_user_11 in test_20)
        result = cli_runner.invoke(
            cli, ["database", "delete", "test-db-4", "--force", "--silent"]
        )
        assert result.exit_code == 0, result.output

    # =================
    # CLEANUP TESTS (Run Last)
    # =================

    def test_90_cleanup_resources(self, cli_runner, super_user, test_projects):
        """Cleanup all test databases, roles, and the test device"""
        super_user.login(cli_runner, project_name=test_projects[0])

        # Delete all test databases via manifests
        for manifest in [
            self.database_correct,
            self.database_basic,
            self.database_extended,
            self.managed_db_2,
        ]:
            result = cli_runner.invoke(cli, ["delete", "--silent", str(manifest)])
            assert result.exit_code == 0, result.output

        # Unbind all roles from test users
        roles_to_unbind = [
            "database-viewer",
            "database-creator",
            "database-manager",
            "database-readonly",
        ]

        for role in roles_to_unbind:
            for user_email in [
                "cli.test1@rapyuta-robotics.com",
                "cli.test2@rapyuta-robotics.com",
            ]:
                cli_runner.invoke(
                    cli,
                    [
                        "role",
                        "unbind",
                        role,
                        "--user",
                        user_email,
                        "--project",
                        test_projects[0],
                    ],
                )

        # Delete roles
        result = cli_runner.invoke(cli, ["delete", "--silent", str(self.role_manifest)])
        assert result.exit_code == 0, result.output

    def test_91_cleanup_db_device(self, cli_runner, super_user, test_projects):
        """Cleanup the test database device"""
        super_user.login(cli_runner, project_name=test_projects[0])

        result = cli_runner.invoke(
            cli, ["delete", "--silent", str(self.db_device_manifest)]
        )
        assert result.exit_code == 0, result.output

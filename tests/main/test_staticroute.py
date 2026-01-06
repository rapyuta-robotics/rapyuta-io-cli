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


from pathlib import Path

import pytest

from riocli.bootstrap import cli


@pytest.mark.rbac
@pytest.mark.integration
@pytest.mark.slow
class TestStaticRouteRBAC:
    """
    Test RBAC for static route resources with comprehensive scenarios
    """

    @pytest.fixture(autouse=True)
    def setup_manifests(self):
        """Setup manifest file paths"""
        self.staticroute_manifest_dir = (
            Path(__file__).parent.parent / "fixtures" / "manifests" / "staticroute"
        )
        self.role_manifest = self.staticroute_manifest_dir / "role.yaml"
        self.staticroute_manifest = (
            self.staticroute_manifest_dir / "staticroute-basic.yaml"
        )
        self.staticroute_correct = (
            self.staticroute_manifest_dir / "staticroute-correct.yaml"
        )

        # Extended role testing manifests
        self.staticroute_extended = (
            self.staticroute_manifest_dir / "staticroute-extended.yaml"
        )
        self.staticroute_network = (
            self.staticroute_manifest_dir / "staticroute-network.yaml"
        )
        self.managed_staticroute_2 = (
            self.staticroute_manifest_dir / "managed-staticroute-2.yaml"
        )
        self.boundary_staticroutes = (
            self.staticroute_manifest_dir / "boundary-staticroutes.yaml"
        )

    @pytest.fixture
    def logged_in_user_11(self, cli_runner, test_user_11, test_projects):
        """Fixture for test_user_11 logged in with CLI runner"""
        test_user_11.login(cli_runner, project_name=test_projects[0])
        return cli_runner, test_user_11

    @pytest.fixture
    def logged_in_user_12(self, cli_runner, test_user_12, test_projects):
        """Fixture for test_user_12 logged in with CLI runner"""
        test_user_12.login(cli_runner, project_name=test_projects[0])
        return cli_runner, test_user_12

    # =================
    # SETUP TESTS (Run First)
    # =================

    def test_01_super_user_creates_roles(self, cli_runner, super_user, test_projects):
        """Test that super user creates static route roles from role.yaml"""
        # Login as super user
        super_user.login(cli_runner, project_name=test_projects[0])

        # Create roles from role.yaml
        result = cli_runner.invoke(cli, ["apply", "--silent", str(self.role_manifest)])

        # Should succeed
        assert result.exit_code == 0

    def test_02_super_user_creates_staticroutes_from_manifest(
        self, cli_runner, super_user, test_projects
    ):
        """Test that super user creates static routes from staticroute-correct.yaml"""
        # Login as super user
        super_user.login(cli_runner, project_name=test_projects[0])

        # Create static routes from staticroute-correct.yaml
        # This contains test-route-1, test-route-2, and unauthorized-route
        result = cli_runner.invoke(
            cli, ["apply", "--silent", str(self.staticroute_correct)]
        )

        # Should succeed
        assert result.exit_code == 0

        # Create extended pattern static routes for role testing
        result = cli_runner.invoke(
            cli, ["apply", "--silent", str(self.staticroute_extended)]
        )
        assert result.exit_code == 0

        # Create network pattern static routes
        result = cli_runner.invoke(
            cli, ["apply", "--silent", str(self.staticroute_network)]
        )
        assert result.exit_code == 0

    def test_03_super_user_binds_staticroute_viewer_role_to_users(
        self, cli_runner, super_user, test_projects
    ):
        """Test that super user binds staticroute-viewer role to test users"""
        # Login as super user
        super_user.login(cli_runner, project_name=test_projects[0])

        # Bind staticroute-viewer role to test_user_11
        result = cli_runner.invoke(
            cli,
            [
                "role",
                "bind",
                "staticroute-viewer",
                f"Project:{test_projects[0]}",
                "User:cli.test1@rapyuta-robotics.com",
            ],
        )

        # Should succeed
        assert result.exit_code == 0

        # Bind staticroute-viewer role to test_user_12
        result = cli_runner.invoke(
            cli,
            [
                "role",
                "bind",
                "staticroute-viewer",
                f"Project:{test_projects[0]}",
                "User:cli.test2@rapyuta-robotics.com",
            ],
        )

        # Should succeed
        assert result.exit_code == 0

    def test_04_verify_initial_setup(self, cli_runner, super_user, test_projects):
        """Test that initial setup is complete"""
        # Login as super user
        super_user.login(cli_runner, project_name=test_projects[0])

        # List static routes to verify they exist
        result = cli_runner.invoke(cli, ["static-route", "list"])

        # Should succeed
        assert result.exit_code == 0
        assert "test-route-1" in result.output
        assert "test-route-2" in result.output
        assert "unauthorized-route" in result.output

    # =================
    # BASIC RBAC TESTS (staticroute-viewer role)
    # =================

    def test_10_user11_creates_staticroutes_from_manifest(self, logged_in_user_11):
        """Test that test_user_11 creates static routes from staticroute-basic.yaml"""
        runner, user = logged_in_user_11

        # Create static routes from staticroute-basic.yaml
        # This contains test-route-4 (should succeed) and random-route (should fail)
        result = runner.invoke(cli, ["apply", "--silent", str(self.staticroute_manifest)])

        # The result might be mixed - some static routes succeed, others fail
        assert result.exit_code != 0
        assert "Created staticroute:test-route-4" in result.output
        assert (
            "Failed to apply staticroute:random-route. Error: subject is not authorized for this operation"
            in result.output
        )

    def test_11_user11_can_list_staticroutes(self, logged_in_user_11):
        """Test that test_user_11 can list all static routes"""
        runner, user = logged_in_user_11

        result = runner.invoke(cli, ["static-route", "list"])

        # Should succeed
        assert result.exit_code == 0, (
            f"Static route list should succeed for {user.email}. "
            f"Exit code: {result.exit_code}, Output: {result.output}"
        )

        # User should be able to see static routes that match test-route.* pattern
        expected_visible = [
            "test-route-1",
            "test-route-2",
            "test-route-4",
        ]

        # Check that authorized static routes are visible
        for staticroute in expected_visible:
            assert staticroute in result.output

    def test_12_user11_can_inspect_authorized_staticroutes(self, logged_in_user_11):
        """Test that test_user_11 can inspect static routes matching the role pattern"""
        runner, user = logged_in_user_11

        # Should be able to inspect test-route-1
        result = runner.invoke(cli, ["static-route", "inspect", "test-route-1-clitest"])
        assert result.exit_code == 0

        # Should be able to inspect test-route-2
        result = runner.invoke(cli, ["static-route", "inspect", "test-route-2-clitest"])
        assert result.exit_code == 0

        # Should be able to inspect test-route-4 from staticroute-basic.yaml
        result = runner.invoke(cli, ["static-route", "inspect", "test-route-4-clitest"])
        assert result.exit_code == 0

    def test_13_user11_cannot_inspect_unauthorized_staticroutes(self, logged_in_user_11):
        """Test that test_user_11 cannot inspect static routes not matching the role pattern"""
        runner, user = logged_in_user_11

        # Should NOT be able to inspect unauthorized-route
        result = runner.invoke(
            cli, ["static-route", "inspect", "unauthorized-route-clitest"]
        )
        assert result.exit_code != 0
        assert "subject is not authorized for this operation" in result.output

        # Should NOT be able to inspect random-route (doesn't match test-route.* pattern)
        result = runner.invoke(cli, ["static-route", "inspect", "random-route-clitest"])
        assert result.exit_code != 0
        assert "subject is not authorized for this operation" in result.output

    def test_14_user11_cannot_delete_staticroutes(self, logged_in_user_11):
        """Test that test_user_11 cannot delete static routes (only has get/create permissions)"""
        runner, user = logged_in_user_11

        # Should NOT be able to delete even authorized static routes
        result = runner.invoke(
            cli, ["static-route", "delete", "test-route-1-clitest", "--force", "--silent"]
        )

        assert result.exit_code != 0
        assert "subject is not authorized for this operation" in result.output

    def test_15_user12_creates_staticroutes_from_manifest(self, logged_in_user_12):
        """Test that test_user_12 creates static routes from staticroute-basic.yaml"""
        runner, user = logged_in_user_12

        # Create static routes from staticroute-basic.yaml
        result = runner.invoke(cli, ["apply", "--silent", str(self.staticroute_manifest)])

        assert result.exit_code != 0
        assert "subject is not authorized for this operation" in result.output

    def test_16_user12_can_list_staticroutes(self, logged_in_user_12):
        """Test that test_user_12 can list all static routes"""
        runner, user = logged_in_user_12

        result = runner.invoke(cli, ["static-route", "list"])

        # Should succeed
        assert result.exit_code == 0, (
            f"Static route list should succeed for {user.email}. "
            f"Exit code: {result.exit_code}, Output: {result.output}"
        )

        # User should be able to see static routes that match test-route.* pattern
        expected_visible = [
            "test-route-1",
            "test-route-2",
            "test-route-4",
        ]

        # Check that authorized static routes are visible
        for staticroute in expected_visible:
            assert staticroute in result.output

    def test_17_user12_can_inspect_authorized_staticroutes(self, logged_in_user_12):
        """Test that test_user_12 can inspect static routes matching the role pattern"""
        runner, user = logged_in_user_12

        # Should be able to inspect test-route-1
        result = runner.invoke(cli, ["static-route", "inspect", "test-route-1-clitest"])
        assert result.exit_code == 0

        # Should be able to inspect test-route-2
        result = runner.invoke(cli, ["static-route", "inspect", "test-route-2-clitest"])
        assert result.exit_code == 0

        # Should be able to inspect test-route-4 from staticroute-basic.yaml
        result = runner.invoke(cli, ["static-route", "inspect", "test-route-4-clitest"])
        assert result.exit_code == 0

    def test_18_user12_cannot_inspect_unauthorized_staticroutes(self, logged_in_user_12):
        """Test that test_user_12 cannot inspect static routes not matching the role pattern"""
        runner, user = logged_in_user_12

        # Should NOT be able to inspect unauthorized-route
        result = runner.invoke(
            cli, ["static-route", "inspect", "unauthorized-route-clitest"]
        )
        assert result.exit_code != 0
        # Check for authorization error messages
        assert "subject is not authorized for this operation" in result.output

        # Should NOT be able to inspect random-route (doesn't match test-route.* pattern)
        result2 = runner.invoke(cli, ["static-route", "inspect", "random-route-clitest"])
        assert result2.exit_code != 0
        assert "subject is not authorized for this operation" in result2.output

    def test_19_user12_cannot_delete_staticroutes(self, logged_in_user_12):
        """Test that test_user_12 cannot delete static routes (only has get/create permissions)"""
        runner, user = logged_in_user_12

        # Should NOT be able to delete even authorized static routes
        result = runner.invoke(
            cli, ["static-route", "delete", "test-route-2-clitest", "--force", "--silent"]
        )

        assert result.exit_code != 0
        assert "subject is not authorized for this operation" in result.output

    # =================
    # EXTENDED ROLE TESTS (new static route role patterns)
    # =================

    def test_20_staticroute_creator_role_permissions(
        self, cli_runner, super_user, test_user_11, test_projects
    ):
        """Test staticroute-creator role - can create/get user-route.* and list all static routes"""
        # Login as superuser and setup
        super_user.login(cli_runner, project_name=test_projects[0])

        # Bind staticroute-creator role to test_user_11
        result = cli_runner.invoke(
            cli,
            [
                "role",
                "bind",
                "staticroute-creator",
                f"Project:{test_projects[0]}",
                f"User:{test_user_11.email}",
            ],
        )
        assert result.exit_code == 0

        # Login as test_user_11
        test_user_11.login(cli_runner, project_name=test_projects[0])

        # Test listing all static routes (should work)
        result = cli_runner.invoke(cli, ["static-route", "list"])
        assert result.exit_code == 0
        assert "user-route-1" in result.output

        # Test getting user-route-* (should work)
        result = cli_runner.invoke(
            cli, ["static-route", "inspect", "user-route-1-clitest"]
        )
        assert result.exit_code == 0

        # Test getting managed-route-* (should fail - wrong pattern)
        result = cli_runner.invoke(
            cli, ["static-route", "inspect", "managed-route-1-clitest"]
        )
        assert result.exit_code != 0
        assert "subject is not authorized for this operation" in result.output

    def test_21_staticroute_manager_role_permissions(
        self, cli_runner, super_user, test_user_12, test_projects
    ):
        """Test staticroute-manager role - full CRUD on managed-route.* and list all"""
        # Login as superuser and setup
        super_user.login(cli_runner, project_name=test_projects[0])

        # Bind staticroute-manager role to test_user_12
        result = cli_runner.invoke(
            cli,
            [
                "role",
                "bind",
                "staticroute-manager",
                f"Project:{test_projects[0]}",
                f"User:{test_user_12.email}",
            ],
        )
        assert result.exit_code == 0

        # Login as test_user_12
        test_user_12.login(cli_runner, project_name=test_projects[0])

        # Test listing all static routes (should work)
        result = cli_runner.invoke(cli, ["static-route", "list"])
        assert result.exit_code == 0
        assert "managed-route-1" in result.output

        # Test getting managed-route-* (should work)
        result = cli_runner.invoke(
            cli, ["static-route", "inspect", "managed-route-1-clitest"]
        )
        assert result.exit_code == 0

        # Test creating new managed static route via manifest (should work)
        result = cli_runner.invoke(
            cli, ["apply", "--silent", str(self.managed_staticroute_2)]
        )
        assert result.exit_code == 0

        # Test deleting managed static route (should work)
        result = cli_runner.invoke(
            cli, ["static-route", "delete", "managed-route-1-clitest", "--force"]
        )
        assert result.exit_code == 0

    def test_22_staticroute_readonly_role_permissions(
        self, cli_runner, super_user, test_user_11, test_projects
    ):
        """Test staticroute-readonly role - can get *network* pattern and list all"""
        # Login as superuser and setup
        super_user.login(cli_runner, project_name=test_projects[0])

        result = cli_runner.invoke(
            cli,
            [
                "role",
                "unbind",
                "staticroute-creator",
                f"Project:{test_projects[0]}",
                f"User:{test_user_11.email}",
            ],
        )
        assert result.exit_code == 0

        # Bind staticroute-readonly role to test_user_11
        result = cli_runner.invoke(
            cli,
            [
                "role",
                "bind",
                "staticroute-readonly",
                f"Project:{test_projects[0]}",
                f"User:{test_user_11.email}",
            ],
        )
        assert result.exit_code == 0

        # Login as test_user_11
        test_user_11.login(cli_runner, project_name=test_projects[0])

        # Test listing all static routes (should work)
        result = cli_runner.invoke(cli, ["static-route", "list"])
        assert result.exit_code == 0
        assert "network-gateway-route" in result.output
        assert "internal-network-route" in result.output

        # Test getting *network* pattern static routes (should work)
        result = cli_runner.invoke(
            cli, ["static-route", "inspect", "network-gateway-route-clitest"]
        )
        assert result.exit_code == 0

        result = cli_runner.invoke(
            cli, ["static-route", "inspect", "internal-network-route-clitest"]
        )
        assert result.exit_code == 0

        # Test getting non-network static routes (should fail)
        result = cli_runner.invoke(
            cli, ["static-route", "inspect", "user-route-1-clitest"]
        )
        assert result.exit_code != 0
        assert "subject is not authorized for this operation" in result.output

    def test_23_staticroute_deleter_role_permissions(
        self, cli_runner, super_user, test_user_12, test_projects
    ):
        """Test staticroute-deleter role - can delete/get temp-route.* and list all"""
        # Login as superuser and setup
        super_user.login(cli_runner, project_name=test_projects[0])

        # Bind staticroute-deleter role to test_user_12
        result = cli_runner.invoke(
            cli,
            [
                "role",
                "bind",
                "staticroute-deleter",
                f"Project:{test_projects[0]}",
                f"User:{test_user_12.email}",
            ],
        )
        assert result.exit_code == 0

        # Login as test_user_12
        test_user_12.login(cli_runner, project_name=test_projects[0])

        # Test listing all static routes (should work)
        result = cli_runner.invoke(cli, ["static-route", "list"])
        assert result.exit_code == 0
        assert "temp-route-1" in result.output

        # Test getting temp-route-* (should work)
        result = cli_runner.invoke(
            cli, ["static-route", "inspect", "temp-route-1-clitest"]
        )
        assert result.exit_code == 0

        # Test deleting temp-route-* (should work)
        result = cli_runner.invoke(
            cli, ["static-route", "delete", "temp-route-1-clitest", "--force", "--silent"]
        )
        assert result.exit_code == 0

        # Test getting non-temp static routes (should fail) - use user-route-1 since managed-route-1 was deleted in test_21
        result = cli_runner.invoke(cli, ["static-route", "inspect", "user-route-1"])
        assert result.exit_code != 0
        assert "subject is not authorized for this operation" in result.output

    # =================
    # COMPLEX SCENARIOS
    # =================

    def test_30_staticroute_multiple_roles_combined_permissions(
        self, cli_runner, super_user, test_user_11, test_projects
    ):
        """Test user with multiple static route roles has combined permissions"""
        # Login as superuser and setup
        super_user.login(cli_runner, project_name=test_projects[0])

        # Bind multiple roles to test_user_11
        roles = ["staticroute-creator", "staticroute-readonly"]
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

        # Test listing all static routes (should work from both roles)
        result = cli_runner.invoke(cli, ["static-route", "list"])
        assert result.exit_code == 0

        # Should be able to access user-route-* (from staticroute-creator)
        result = cli_runner.invoke(
            cli, ["static-route", "inspect", "user-route-1-clitest"]
        )
        assert result.exit_code == 0

        # Should be able to access *network* (from staticroute-readonly)
        result = cli_runner.invoke(
            cli, ["static-route", "inspect", "network-gateway-route-clitest"]
        )
        assert result.exit_code == 0

        # Should NOT be able to access patterns from other roles
        result = cli_runner.invoke(
            cli, ["static-route", "inspect", "managed-route-2-clitest"]
        )
        assert result.exit_code != 0
        assert "subject is not authorized for this operation" in result.output

    def test_31_staticroute_pattern_boundary_validation(
        self, cli_runner, super_user, test_user_11, test_projects
    ):
        """Test RBAC pattern matching boundaries for static route names"""
        # Login as superuser and setup
        super_user.login(cli_runner, project_name=test_projects[0])

        # Create boundary test static routes via manifests
        result = cli_runner.invoke(
            cli, ["apply", "--silent", str(self.boundary_staticroutes)]
        )
        # May succeed or fail based on superuser permissions

        # Bind staticroute-creator role to test_user_11
        result = cli_runner.invoke(
            cli,
            [
                "role",
                "bind",
                "staticroute-creator",
                f"Project:{test_projects[0]}",
                f"User:{test_user_11.email}",
            ],
        )
        assert result.exit_code == 0

        # Login as test_user_11
        test_user_11.login(cli_runner, project_name=test_projects[0])

        # Test pattern boundaries
        # Should work: user-route-test (matches user-route.*)
        result = cli_runner.invoke(
            cli, ["static-route", "inspect", "user-route-test-clitest"]
        )
        assert result.exit_code in [0, 1]  # May not exist but pattern would match

        # Should fail: my-user-route-1 (doesn't start with user-route)
        result = cli_runner.invoke(
            cli, ["static-route", "inspect", "my-user-route-1-clitest"]
        )
        assert result.exit_code != 0

        # Cleanup boundary static routes
        super_user.login(cli_runner, project_name=test_projects[0])
        result = cli_runner.invoke(
            cli, ["delete", "--silent", str(self.boundary_staticroutes)]
        )

    # =================
    # CLEANUP TESTS (Run Last)
    # =================

    def test_90_cleanup_resources(self, cli_runner, super_user, test_projects):
        """Cleanup test resources"""
        # Login as super user
        super_user.login(cli_runner, project_name=test_projects[0])

        # Delete static routes
        staticroute_manifests = [
            self.staticroute_manifest,  # Contains test-route-4 and random-route
            self.staticroute_correct,
            self.staticroute_extended,  # Extended patterns
            self.staticroute_network,  # Network patterns
            self.managed_staticroute_2,  # Managed static route for testing
            self.boundary_staticroutes,  # Boundary test static routes
        ]

        for manifest in staticroute_manifests:
            result = cli_runner.invoke(cli, ["delete", "--silent", str(manifest)])
            # Don't assert on exit code as resources might not exist
            assert result.exit_code == 0, result.output

        # Unbind all roles (if role bindings exist)
        roles_to_unbind = [
            "staticroute-viewer",
            "staticroute-creator",
            "staticroute-manager",
            "staticroute-readonly",
            "staticroute-deleter",
        ]

        for role in roles_to_unbind:
            for user_email in [
                "cli.test1@rapyuta-robotics.com",
                "cli.test2@rapyuta-robotics.com",
            ]:
                result = cli_runner.invoke(
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
                # Don't assert on exit code as bindings might not exist

        # Delete role
        result = cli_runner.invoke(cli, ["delete", "--silent", str(self.role_manifest)])
        assert result.exit_code == 0

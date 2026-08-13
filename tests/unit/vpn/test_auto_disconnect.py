from unittest.mock import MagicMock, patch

from click.testing import CliRunner


def _make_project_ctx(auto_disconnect_vpn=True, project_id="old-guid"):
    obj = MagicMock()
    obj.auto_disconnect_vpn = auto_disconnect_vpn
    obj.current_project_id = project_id
    obj.data = {
        "project_id": project_id,
        "project_name": "old-project",
        "organization_id": "org-guid",
    }
    return obj


def _make_org_ctx(auto_disconnect_vpn=True):
    obj = MagicMock()
    obj.auto_disconnect_vpn = auto_disconnect_vpn
    obj.data = {
        "organization_id": "different-org-guid",
        "organization_name": "old-org",
        "organization_short_id": "old-short",
    }
    return obj


class TestProjectSelectVpnDisconnect:
    def _invoke(self, args, ctx_obj):
        from riocli.project.select import select_project

        with (
            patch("riocli.project.util.new_v2_client"),
            patch("riocli.project.util.find_project_guid", return_value="new-guid"),
            patch("riocli.project.util.get_project_name", return_value="new-project"),
            patch("riocli.project.select.get_root_context") as mock_get_ctx,
        ):
            mock_get_ctx.return_value.obj = ctx_obj
            return CliRunner().invoke(select_project, args, obj=ctx_obj), mock_get_ctx

    @patch("riocli.vpn.util.is_tailscale_up", return_value=True)
    @patch("riocli.vpn.util.stop_tailscale", return_value=True)
    @patch("riocli.vpn.util.cleanup_hosts_file")
    def test_disconnects_vpn_when_tailscale_up(self, mock_cleanup, mock_stop, mock_is_up):
        result, _ = self._invoke(["new-project"], _make_project_ctx())
        assert result.exit_code == 0
        mock_stop.assert_called_once()
        mock_cleanup.assert_called_once()

    @patch("riocli.vpn.util.is_tailscale_up", return_value=False)
    @patch("riocli.vpn.util.stop_tailscale")
    @patch("riocli.vpn.util.cleanup_hosts_file")
    def test_skips_stop_when_tailscale_not_up(self, mock_cleanup, mock_stop, mock_is_up):
        result, _ = self._invoke(["new-project"], _make_project_ctx())
        assert result.exit_code == 0
        mock_stop.assert_not_called()
        mock_cleanup.assert_called_once()

    @patch("riocli.vpn.util.is_tailscale_up", return_value=True)
    @patch("riocli.vpn.util.stop_tailscale")
    @patch("riocli.vpn.util.cleanup_hosts_file")
    def test_keep_vpn_flag_skips_disconnect_and_cleanup(
        self, mock_cleanup, mock_stop, mock_is_up
    ):
        result, _ = self._invoke(["new-project", "--keep-vpn"], _make_project_ctx())
        assert result.exit_code == 0
        mock_stop.assert_not_called()
        mock_cleanup.assert_not_called()

    @patch("riocli.vpn.util.is_tailscale_up", return_value=True)
    @patch("riocli.vpn.util.stop_tailscale")
    @patch("riocli.vpn.util.cleanup_hosts_file")
    def test_config_opt_out_skips_disconnect_and_cleanup(
        self, mock_cleanup, mock_stop, mock_is_up
    ):
        result, _ = self._invoke(
            ["new-project"], _make_project_ctx(auto_disconnect_vpn=False)
        )
        assert result.exit_code == 0
        mock_stop.assert_not_called()
        mock_cleanup.assert_not_called()

    @patch("riocli.vpn.util.is_tailscale_up", return_value=True)
    @patch("riocli.vpn.util.stop_tailscale", return_value=False)
    @patch("riocli.vpn.util.cleanup_hosts_file")
    def test_hosts_not_cleaned_when_stop_fails(self, mock_cleanup, mock_stop, mock_is_up):
        result, _ = self._invoke(["new-project"], _make_project_ctx())
        assert result.exit_code == 0
        mock_stop.assert_called_once()
        mock_cleanup.assert_not_called()

    @patch("riocli.vpn.util.is_tailscale_up", return_value=True)
    @patch("riocli.vpn.util.stop_tailscale")
    @patch("riocli.vpn.util.cleanup_hosts_file")
    def test_noop_switch_skips_vpn_disconnect(self, mock_cleanup, mock_stop, mock_is_up):
        # Selecting the already-selected project must not touch VPN.
        result, _ = self._invoke(
            ["new-project"], _make_project_ctx(project_id="new-guid")
        )
        assert result.exit_code == 0
        mock_stop.assert_not_called()
        mock_cleanup.assert_not_called()


class TestOrgSelectVpnDisconnect:
    def _invoke(self, args, ctx_obj):
        from riocli.organization.select import select_organization

        with (
            patch("riocli.organization.util.new_v2_client"),
            patch(
                "riocli.organization.util.find_organization_guid",
                return_value=("new-org-guid", "new-short"),
            ),
            patch("riocli.organization.select.get_root_context") as mock_get_ctx,
        ):
            mock_get_ctx.return_value.obj = ctx_obj
            return CliRunner().invoke(select_organization, args), mock_get_ctx

    @patch("riocli.vpn.util.is_tailscale_up", return_value=True)
    @patch("riocli.vpn.util.stop_tailscale", return_value=True)
    @patch("riocli.vpn.util.cleanup_hosts_file")
    def test_disconnects_vpn_when_tailscale_up(self, mock_cleanup, mock_stop, mock_is_up):
        result, _ = self._invoke(["new-org", "--no-interactive"], _make_org_ctx())
        assert result.exit_code == 0
        mock_stop.assert_called_once()
        mock_cleanup.assert_called_once()

    @patch("riocli.vpn.util.is_tailscale_up", return_value=True)
    @patch("riocli.vpn.util.stop_tailscale")
    @patch("riocli.vpn.util.cleanup_hosts_file")
    def test_keep_vpn_flag_skips_disconnect_and_cleanup(
        self, mock_cleanup, mock_stop, mock_is_up
    ):
        result, _ = self._invoke(
            ["new-org", "--keep-vpn", "--no-interactive"], _make_org_ctx()
        )
        assert result.exit_code == 0
        mock_stop.assert_not_called()
        mock_cleanup.assert_not_called()

    @patch("riocli.vpn.util.is_tailscale_up", return_value=True)
    @patch("riocli.vpn.util.stop_tailscale")
    @patch("riocli.vpn.util.cleanup_hosts_file")
    def test_config_opt_out_skips_disconnect_and_cleanup(
        self, mock_cleanup, mock_stop, mock_is_up
    ):
        result, _ = self._invoke(
            ["new-org", "--no-interactive"], _make_org_ctx(auto_disconnect_vpn=False)
        )
        assert result.exit_code == 0
        mock_stop.assert_not_called()
        mock_cleanup.assert_not_called()

    @patch("riocli.vpn.util.is_tailscale_up", return_value=True)
    @patch("riocli.vpn.util.stop_tailscale", return_value=False)
    @patch("riocli.vpn.util.cleanup_hosts_file")
    def test_hosts_not_cleaned_when_stop_fails(self, mock_cleanup, mock_stop, mock_is_up):
        result, _ = self._invoke(["new-org", "--no-interactive"], _make_org_ctx())
        assert result.exit_code == 0
        mock_stop.assert_called_once()
        mock_cleanup.assert_not_called()

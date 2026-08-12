from unittest.mock import MagicMock, patch

from click.testing import CliRunner

from riocli.vpn.util import should_disconnect_vpn


class TestShouldDisconnectVpn:
    def test_disconnects_by_default(self):
        assert should_disconnect_vpn({}, keep_vpn=False) is True

    def test_keep_vpn_flag_suppresses_disconnect(self):
        assert should_disconnect_vpn({}, keep_vpn=True) is False

    def test_config_opt_out_suppresses_disconnect(self):
        assert should_disconnect_vpn({"auto_disconnect_vpn": False}, keep_vpn=False) is False

    def test_config_opt_out_with_keep_vpn_flag(self):
        assert should_disconnect_vpn({"auto_disconnect_vpn": False}, keep_vpn=True) is False

    def test_config_explicitly_true_disconnects(self):
        assert should_disconnect_vpn({"auto_disconnect_vpn": True}, keep_vpn=False) is True

    def test_keep_vpn_flag_overrides_config_true(self):
        assert should_disconnect_vpn({"auto_disconnect_vpn": True}, keep_vpn=True) is False


def _make_project_ctx(config_data=None):
    obj = MagicMock()
    obj.data = {
        "project_id": "old-guid",
        "project_name": "old-project",
        "organization_id": "org-guid",
        **(config_data or {}),
    }
    return obj


def _make_org_ctx(config_data=None):
    obj = MagicMock()
    obj.data = {
        "organization_id": "different-org-guid",  # different so "already in org" check passes
        "organization_name": "old-org",
        "organization_short_id": "old-short",
        **(config_data or {}),
    }
    return obj


PROJECT_PATCHES = [
    patch("riocli.project.util.new_v2_client"),
    patch("riocli.project.util.find_project_guid", return_value="new-project-guid"),
    patch("riocli.project.util.get_project_name", return_value="new-project"),
    patch("riocli.project.select.get_root_context"),
]

ORG_PATCHES = [
    patch("riocli.organization.util.new_v2_client"),
    patch("riocli.organization.util.find_organization_guid", return_value=("new-org-guid", "new-short")),
    patch("riocli.organization.select.get_root_context"),
]


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
            # Pass obj so click.get_current_context().obj works inside name_to_guid
            return CliRunner().invoke(select_project, args, obj=ctx_obj), mock_get_ctx

    @patch("riocli.project.select.is_tailscale_up", return_value=True)
    @patch("riocli.project.select.stop_tailscale", return_value=True)
    @patch("riocli.project.select.cleanup_hosts_file")
    def test_disconnects_vpn_when_tailscale_up(self, mock_cleanup, mock_stop, mock_is_up):
        result, _ = self._invoke(["new-project"], _make_project_ctx())
        assert result.exit_code == 0
        mock_stop.assert_called_once()
        mock_cleanup.assert_called_once()

    @patch("riocli.project.select.is_tailscale_up", return_value=False)
    @patch("riocli.project.select.stop_tailscale")
    @patch("riocli.project.select.cleanup_hosts_file")
    def test_skips_stop_when_tailscale_not_up(self, mock_cleanup, mock_stop, mock_is_up):
        result, _ = self._invoke(["new-project"], _make_project_ctx())
        assert result.exit_code == 0
        mock_stop.assert_not_called()
        mock_cleanup.assert_called_once()

    @patch("riocli.project.select.is_tailscale_up", return_value=True)
    @patch("riocli.project.select.stop_tailscale")
    @patch("riocli.project.select.cleanup_hosts_file")
    def test_keep_vpn_flag_skips_disconnect_and_cleanup(self, mock_cleanup, mock_stop, mock_is_up):
        result, _ = self._invoke(["new-project", "--keep-vpn"], _make_project_ctx())
        assert result.exit_code == 0
        mock_stop.assert_not_called()
        mock_cleanup.assert_not_called()

    @patch("riocli.project.select.is_tailscale_up", return_value=True)
    @patch("riocli.project.select.stop_tailscale")
    @patch("riocli.project.select.cleanup_hosts_file")
    def test_config_opt_out_skips_disconnect_and_cleanup(self, mock_cleanup, mock_stop, mock_is_up):
        result, _ = self._invoke(["new-project"], _make_project_ctx({"auto_disconnect_vpn": False}))
        assert result.exit_code == 0
        mock_stop.assert_not_called()
        mock_cleanup.assert_not_called()


class TestOrgSelectVpnDisconnect:
    def _invoke(self, args, ctx_obj):
        from riocli.organization.select import select_organization

        with (
            patch("riocli.organization.util.new_v2_client"),
            patch("riocli.organization.util.find_organization_guid", return_value=("new-org-guid", "new-short")),
            patch("riocli.organization.select.get_root_context") as mock_get_ctx,
        ):
            mock_get_ctx.return_value.obj = ctx_obj
            return CliRunner().invoke(select_organization, args), mock_get_ctx

    @patch("riocli.organization.select.is_tailscale_up", return_value=True)
    @patch("riocli.organization.select.stop_tailscale", return_value=True)
    @patch("riocli.organization.select.cleanup_hosts_file")
    def test_disconnects_vpn_when_tailscale_up(self, mock_cleanup, mock_stop, mock_is_up):
        result, _ = self._invoke(["new-org", "--no-interactive"], _make_org_ctx())
        assert result.exit_code == 0
        mock_stop.assert_called_once()
        mock_cleanup.assert_called_once()

    @patch("riocli.organization.select.is_tailscale_up", return_value=True)
    @patch("riocli.organization.select.stop_tailscale")
    @patch("riocli.organization.select.cleanup_hosts_file")
    def test_keep_vpn_flag_skips_disconnect_and_cleanup(self, mock_cleanup, mock_stop, mock_is_up):
        result, _ = self._invoke(["new-org", "--keep-vpn", "--no-interactive"], _make_org_ctx())
        assert result.exit_code == 0
        mock_stop.assert_not_called()
        mock_cleanup.assert_not_called()

    @patch("riocli.organization.select.is_tailscale_up", return_value=True)
    @patch("riocli.organization.select.stop_tailscale")
    @patch("riocli.organization.select.cleanup_hosts_file")
    def test_config_opt_out_skips_disconnect_and_cleanup(self, mock_cleanup, mock_stop, mock_is_up):
        result, _ = self._invoke(["new-org", "--no-interactive"], _make_org_ctx({"auto_disconnect_vpn": False}))
        assert result.exit_code == 0
        mock_stop.assert_not_called()
        mock_cleanup.assert_not_called()

from unittest.mock import MagicMock, patch

from click.testing import CliRunner

from riocli.compose.up import up


class TestUpCommandChartFlag:
    def test_chart_flag_requires_chart_name(self, tmp_path):
        runner = CliRunner()
        result = runner.invoke(up, ["--chart", "-p", str(tmp_path)])
        assert result.exit_code != 0
        assert "Chart name is required" in result.output

    def test_chart_flag_rejects_multiple_names(self, tmp_path):
        runner = CliRunner()
        result = runner.invoke(up, ["--chart", "-p", str(tmp_path), "chart-a", "chart-b"])
        assert result.exit_code != 0
        assert "Only one chart name is allowed" in result.output

    @patch("riocli.compose.up.write_compose_yaml")
    @patch("riocli.compose.up.DockerComposeManager")
    @patch("riocli.compose.up.generate_compose_file")
    @patch("riocli.compose.up.resolve_chart_inputs")
    def test_chart_flag_cleanup_called_on_success(
        self, mock_resolve, mock_gen, mock_mgr_cls, mock_write, tmp_path
    ):
        chart_obj = MagicMock()
        mock_resolve.return_value = ((tmp_path / "templates",), (), chart_obj)
        mock_gen.return_value = {"services": {}}
        mgr = MagicMock()
        mgr.validate_docker_availability.return_value = True
        mgr.up.return_value = True
        mock_mgr_cls.return_value = mgr

        runner = CliRunner()
        runner.invoke(
            up,
            ["--chart", "-p", str(tmp_path), "my-chart"],
            obj=MagicMock(data={}),
        )
        chart_obj.cleanup.assert_called_once()

    @patch("riocli.compose.up.DockerComposeManager")
    @patch("riocli.compose.up.generate_compose_file", side_effect=Exception("fail"))
    @patch("riocli.compose.up.resolve_chart_inputs")
    def test_chart_flag_cleanup_called_on_error(
        self, mock_resolve, mock_gen, mock_mgr_cls, tmp_path
    ):
        chart_obj = MagicMock()
        mock_resolve.return_value = ((tmp_path / "templates",), (), chart_obj)
        mgr = MagicMock()
        mock_mgr_cls.return_value = mgr

        runner = CliRunner()
        runner.invoke(
            up,
            ["--chart", "-p", str(tmp_path), "my-chart"],
            obj=MagicMock(data={}),
        )
        chart_obj.cleanup.assert_called_once()


class TestUpCommandLocalConfigtreesFlag:
    def test_requires_configtree_dir(self, tmp_path):
        runner = CliRunner()
        result = runner.invoke(
            up,
            ["--local-configtrees", "-p", str(tmp_path), "manifest.yaml"],
            obj=MagicMock(data={}),
        )
        assert result.exit_code != 0
        assert "--local-configtrees requires --configtree-dir" in result.output

    @patch("riocli.compose.up.write_compose_yaml")
    @patch("riocli.compose.up.DockerComposeManager")
    @patch("riocli.compose.up.generate_compose_file")
    def test_merges_local_configtree_services(
        self, mock_gen, mock_mgr_cls, mock_write, tmp_path
    ):
        configtree_dir = tmp_path / "configtrees"
        configtree_dir.mkdir()
        (configtree_dir / "common.yaml").write_text("{}")
        mock_gen.return_value = {"services": {"svc-new": {"image": "new"}}}
        mgr = MagicMock()
        mgr.validate_docker_availability.return_value = True
        mgr.up.return_value = True
        mock_mgr_cls.return_value = mgr

        runner = CliRunner()
        runner.invoke(
            up,
            [
                "--local-configtrees",
                "--configtree-dir",
                str(configtree_dir),
                "-p",
                str(tmp_path),
                "manifest.yaml",
            ],
            obj=MagicMock(data={}),
            catch_exceptions=False,
        )

        written_doc = mock_write.call_args.kwargs["compose_dict"]
        assert "svc-new" in written_doc["services"]
        assert "v2-apiserver_v2-apiserver" in written_doc["services"]
        assert "v2configtree_bootstrap_v2configtree_bootstrap" in written_doc["services"]
        assert "ioconfig_syncer_ioconfig_syncer" in written_doc["services"]

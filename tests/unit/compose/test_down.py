from unittest.mock import MagicMock, patch

from click.testing import CliRunner

from riocli.compose.down import down


class TestDownCommandChartFlag:
    def test_chart_flag_requires_chart_name(self, tmp_path):
        runner = CliRunner()
        result = runner.invoke(down, ["--chart", "-p", str(tmp_path)])
        assert result.exit_code != 0
        assert "Chart name is required" in result.output

    def test_chart_flag_rejects_multiple_names(self, tmp_path):
        runner = CliRunner()
        result = runner.invoke(
            down, ["--chart", "-p", str(tmp_path), "chart-a", "chart-b"]
        )
        assert result.exit_code != 0
        assert "Only one chart name is allowed" in result.output

    @patch("riocli.compose.down.DockerComposeManager")
    @patch("riocli.compose.down.resolve_chart_inputs")
    def test_chart_flag_cleanup_called_on_success(
        self, mock_resolve, mock_mgr_cls, tmp_path
    ):
        chart_obj = MagicMock()
        mock_resolve.return_value = ((tmp_path / "templates",), (), chart_obj)
        mgr = MagicMock()
        mgr.validate_docker_availability.return_value = True
        mgr.down.return_value = True
        # Simulate compose file already exists so generate is not triggered
        mgr.check_empty_file.return_value = False
        # Make compose_path.exists() return True by creating the file
        compose_file = tmp_path / "docker-compose.yaml"
        compose_file.write_text("services: {}")
        mock_mgr_cls.return_value = mgr

        runner = CliRunner()
        runner.invoke(
            down,
            ["--chart", "-p", str(tmp_path), "my-chart"],
            obj=MagicMock(data={}),
        )
        chart_obj.cleanup.assert_called_once()

    @patch("riocli.compose.down.DockerComposeManager")
    @patch("riocli.compose.down.generate_compose_file", side_effect=Exception("fail"))
    @patch("riocli.compose.down.resolve_chart_inputs")
    def test_chart_flag_cleanup_called_on_error(
        self, mock_resolve, mock_gen, mock_mgr_cls, tmp_path
    ):
        chart_obj = MagicMock()
        mock_resolve.return_value = ((tmp_path / "templates",), (), chart_obj)
        mgr = MagicMock()
        # compose file does not exist → triggers generate_compose_file, which raises
        mock_mgr_cls.return_value = mgr

        runner = CliRunner()
        runner.invoke(
            down,
            ["--chart", "-p", str(tmp_path), "my-chart"],
            obj=MagicMock(data={}),
        )
        chart_obj.cleanup.assert_called_once()

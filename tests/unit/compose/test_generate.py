from pathlib import Path
from unittest.mock import MagicMock, patch

from click.testing import CliRunner

from riocli.compose.generate import generate, resolve_chart_inputs


def make_chart_mock(tmp_path: Path, has_values: bool = True):
    chart = MagicMock()
    chart.name = "my-chart"
    chart.tmp_dir.name = str(tmp_path)
    templates_dir = tmp_path / "my-chart" / "templates"
    templates_dir.mkdir(parents=True)
    if has_values:
        values_file = tmp_path / "my-chart" / "values.yaml"
        values_file.write_text("key: value")
    return chart


class TestResolveChartInputs:
    @patch("riocli.chart.chart.Chart")
    @patch("riocli.chart.util.find_chart")
    def test_returns_templates_dir_and_chart_values_prepended(
        self, mock_find_chart, mock_chart_cls, tmp_path
    ):
        chart = make_chart_mock(tmp_path)
        mock_find_chart.return_value = [{"name": "my-chart", "version": "1.0.0"}]
        mock_chart_cls.return_value = chart

        files, values, chart_obj = resolve_chart_inputs("my-chart", ("user.yaml",))

        assert len(files) == 1
        assert "templates" in str(files[0])
        assert values[0].endswith("values.yaml")  # chart values first
        assert values[-1] == "user.yaml"  # user values last
        assert chart_obj is chart

    @patch("riocli.chart.chart.Chart")
    @patch("riocli.chart.util.find_chart")
    def test_skips_chart_values_when_missing(
        self, mock_find_chart, mock_chart_cls, tmp_path
    ):
        chart = make_chart_mock(tmp_path, has_values=False)
        mock_find_chart.return_value = [{"name": "my-chart", "version": "1.0.0"}]
        mock_chart_cls.return_value = chart

        files, values, chart_obj = resolve_chart_inputs("my-chart", ("user.yaml",))

        assert values == ("user.yaml",)

    @patch("click.secho")
    @patch("riocli.compose.generate.Chart")
    @patch("riocli.compose.generate.find_chart")
    def test_multiple_versions_warns_and_uses_first(
        self, mock_find_chart, mock_chart_cls, mock_secho, tmp_path
    ):
        chart = make_chart_mock(tmp_path)
        mock_find_chart.return_value = [
            {"name": "my-chart", "version": "2.0.0"},
            {"name": "my-chart", "version": "1.0.0"},
        ]
        mock_chart_cls.return_value = chart

        files, values, chart_obj = resolve_chart_inputs("my-chart", ())

        mock_chart_cls.assert_called_once_with(name="my-chart", version="2.0.0")
        warning_messages = [
            call.args[0]
            for call in mock_secho.call_args_list
            if call.args
        ]
        assert any("More than one chart version" in msg for msg in warning_messages)

    @patch("riocli.chart.chart.Chart")
    @patch("riocli.chart.util.find_chart")
    def test_no_user_values_only_chart_values(
        self, mock_find_chart, mock_chart_cls, tmp_path
    ):
        chart = make_chart_mock(tmp_path, has_values=True)
        mock_find_chart.return_value = [{"name": "my-chart", "version": "1.0.0"}]
        mock_chart_cls.return_value = chart

        files, values, chart_obj = resolve_chart_inputs("my-chart", ())

        assert len(values) == 1
        assert values[0].endswith("values.yaml")


class TestGenerateCommandChartFlag:
    def test_chart_flag_requires_chart_name(self, tmp_path):
        runner = CliRunner()
        result = runner.invoke(generate, ["--chart", "-p", str(tmp_path)])
        assert result.exit_code != 0
        assert "Chart name is required" in result.output

    def test_chart_flag_rejects_multiple_names(self, tmp_path):
        runner = CliRunner()
        result = runner.invoke(
            generate, ["--chart", "-p", str(tmp_path), "chart-a", "chart-b"]
        )
        assert result.exit_code != 0
        assert "Only one chart name is allowed" in result.output

    @patch("riocli.compose.generate.generate_compose_file")
    @patch("riocli.compose.generate.resolve_chart_inputs")
    def test_chart_flag_calls_resolve_and_generate(
        self, mock_resolve, mock_gen, tmp_path
    ):
        chart_obj = MagicMock()
        mock_resolve.return_value = (
            (tmp_path / "templates",),
            ("chart_values.yaml",),
            chart_obj,
        )
        mock_gen.return_value = None

        runner = CliRunner()
        runner.invoke(
            generate,
            ["--chart", "-p", str(tmp_path), "my-chart"],
            obj=MagicMock(data={}),
            catch_exceptions=False,
        )

        mock_resolve.assert_called_once_with("my-chart", ())
        mock_gen.assert_called_once()
        chart_obj.cleanup.assert_called_once()

    @patch("riocli.compose.generate.generate_compose_file", side_effect=Exception("boom"))
    @patch("riocli.compose.generate.resolve_chart_inputs")
    def test_chart_flag_cleanup_called_on_error(self, mock_resolve, mock_gen, tmp_path):
        chart_obj = MagicMock()
        mock_resolve.return_value = (
            (tmp_path / "templates",),
            (),
            chart_obj,
        )

        runner = CliRunner()
        runner.invoke(
            generate,
            ["--chart", "-p", str(tmp_path), "my-chart"],
            obj=MagicMock(data={}),
        )

        chart_obj.cleanup.assert_called_once()

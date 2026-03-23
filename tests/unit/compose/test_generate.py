from pathlib import Path
from unittest.mock import MagicMock, patch

from click.testing import CliRunner

from riocli.compose.generate import generate, merge_compose_services, resolve_chart_inputs


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


class TestMergeComposeServices:
    def test_patch_overrides_base_on_name_collision(self):
        base = {"svc-a": {"image": "old"}, "svc-b": {"image": "b"}}
        patch = {"svc-a": {"image": "new"}, "svc-c": {"image": "c"}}
        result = merge_compose_services(base, patch)
        assert result == {
            "svc-a": {"image": "new"},
            "svc-b": {"image": "b"},
            "svc-c": {"image": "c"},
        }

    def test_all_base_services_preserved_when_no_overlap(self):
        base = {"svc-a": {"image": "a"}}
        patch = {"svc-b": {"image": "b"}}
        result = merge_compose_services(base, patch)
        assert result == {"svc-a": {"image": "a"}, "svc-b": {"image": "b"}}

    def test_empty_base_returns_patch_only(self):
        result = merge_compose_services({}, {"svc": {"image": "x"}})
        assert result == {"svc": {"image": "x"}}


class TestResolveChartInputs:
    @patch("riocli.compose.generate.Chart")
    @patch("riocli.compose.generate.find_chart")
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

    @patch("riocli.compose.generate.Chart")
    @patch("riocli.compose.generate.find_chart")
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
            call.args[0] for call in mock_secho.call_args_list if call.args
        ]
        assert any("More than one chart version" in msg for msg in warning_messages)

    @patch("riocli.compose.generate.Chart")
    @patch("riocli.compose.generate.find_chart")
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

    @patch("riocli.compose.generate.write_compose_yaml")
    @patch("riocli.compose.generate.generate_compose_file")
    @patch("riocli.compose.generate.resolve_chart_inputs")
    def test_chart_flag_calls_resolve_and_generate(
        self, mock_resolve, mock_gen, mock_write, tmp_path
    ):
        chart_obj = MagicMock()
        mock_resolve.return_value = (
            (tmp_path / "templates",),
            ("chart_values.yaml",),
            chart_obj,
        )
        mock_gen.return_value = {"services": {}}

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


class TestGenerateCommandChartAndAppendFlag:
    @patch("riocli.compose.generate.write_compose_yaml")
    @patch("riocli.compose.generate.generate_compose_file")
    @patch("riocli.compose.generate.resolve_chart_inputs")
    def test_chart_and_append_merges_chart_services_with_existing(
        self, mock_resolve, mock_gen, mock_write, tmp_path
    ):
        chart_obj = MagicMock()
        mock_resolve.return_value = (
            (tmp_path / "templates",),
            ("chart_values.yaml",),
            chart_obj,
        )
        compose_file = tmp_path / "docker-compose.yaml"
        compose_file.write_text("services:\n  svc-existing:\n    image: existing\n")
        mock_gen.return_value = {"services": {"svc-chart": {"image": "chart"}}}

        runner = CliRunner()
        runner.invoke(
            generate,
            ["--chart", "--append", "-p", str(tmp_path), "my-chart"],
            obj=MagicMock(data={}),
            catch_exceptions=False,
        )

        mock_write.assert_called_once()
        written_doc = mock_write.call_args.kwargs["compose_dict"]
        assert "svc-existing" in written_doc["services"]
        assert "svc-chart" in written_doc["services"]
        chart_obj.cleanup.assert_called_once()


class TestGenerateCommandAppendFlag:
    @patch("riocli.compose.generate.write_compose_yaml")
    @patch("riocli.compose.generate.generate_compose_file")
    def test_append_merges_new_services_with_existing(
        self, mock_gen, mock_write, tmp_path
    ):
        compose_file = tmp_path / "docker-compose.yaml"
        compose_file.write_text("services:\n  svc-base:\n    image: base\n")
        mock_gen.return_value = {"services": {"svc-new": {"image": "new"}}}

        runner = CliRunner()
        runner.invoke(
            generate,
            ["--append", "-p", str(tmp_path), "manifest.yaml"],
            obj=MagicMock(data={}),
            catch_exceptions=False,
        )

        mock_write.assert_called_once()
        written_doc = mock_write.call_args.kwargs["compose_dict"]
        assert "svc-base" in written_doc["services"]
        assert "svc-new" in written_doc["services"]

    @patch("riocli.compose.generate.write_compose_yaml")
    @patch("riocli.compose.generate.generate_compose_file")
    def test_append_new_service_overrides_existing_on_name_collision(
        self, mock_gen, mock_write, tmp_path
    ):
        compose_file = tmp_path / "docker-compose.yaml"
        compose_file.write_text("services:\n  svc-a:\n    image: old\n")
        mock_gen.return_value = {"services": {"svc-a": {"image": "new"}}}

        runner = CliRunner()
        runner.invoke(
            generate,
            ["--append", "-p", str(tmp_path), "manifest.yaml"],
            obj=MagicMock(data={}),
            catch_exceptions=False,
        )

        written_doc = mock_write.call_args.kwargs["compose_dict"]
        assert written_doc["services"]["svc-a"]["image"] == "new"

    @patch("riocli.compose.generate.write_compose_yaml")
    @patch("riocli.compose.generate.generate_compose_file")
    def test_append_with_no_existing_file_creates_new(
        self, mock_gen, mock_write, tmp_path
    ):
        # Output file does NOT exist
        mock_gen.return_value = {"services": {"svc-new": {"image": "new"}}}

        runner = CliRunner()
        runner.invoke(
            generate,
            ["--append", "-p", str(tmp_path), "manifest.yaml"],
            obj=MagicMock(data={}),
            catch_exceptions=False,
        )

        written_doc = mock_write.call_args.kwargs["compose_dict"]
        assert written_doc == {"services": {"svc-new": {"image": "new"}}}

    @patch("riocli.compose.generate.write_compose_yaml")
    @patch("riocli.compose.generate.generate_compose_file")
    def test_without_append_overwrites_existing_file(
        self, mock_gen, mock_write, tmp_path
    ):
        compose_file = tmp_path / "docker-compose.yaml"
        compose_file.write_text("services:\n  svc-base:\n    image: base\n")
        mock_gen.return_value = {"services": {"svc-new": {"image": "new"}}}

        runner = CliRunner()
        runner.invoke(
            generate,
            ["-p", str(tmp_path), "manifest.yaml"],  # no --append
            obj=MagicMock(data={}),
            catch_exceptions=False,
        )

        written_doc = mock_write.call_args.kwargs["compose_dict"]
        assert "svc-base" not in written_doc["services"]
        assert "svc-new" in written_doc["services"]

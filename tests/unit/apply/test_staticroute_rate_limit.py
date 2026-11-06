"""Exercise rio apply's YAML -> CLI model -> SDK -> HTTP request path."""

import json
from importlib import import_module
from unittest.mock import MagicMock

import httpx
import pytest
import yaml
from click.testing import CliRunner
from rapyuta_io_sdk_v2 import Client

from riocli.config import Configuration


@pytest.mark.parametrize("existing", [False, True])
@pytest.mark.parametrize(
    "spec",
    [
        {"sourceIPRange": ["121.2.38.2/32"]},
        {"rateLimit": None},
        {"rateLimit": {"average": 100}},
        {"rateLimit": {"average": 100, "period": "1m", "burst": 20}},
        {"rateLimit": {"average": 100, "period": None, "burst": None}},
        {"rateLimit": {"average": 100, "burst": 0}},
    ],
)
def test_apply_staticroute_payload(tmp_path, monkeypatch, spec, existing):
    manifest = {
        "apiVersion": "api.rapyuta.io/v2",
        "kind": "StaticRoute",
        "metadata": {"name": "limited"},
        "spec": spec,
    }
    path = tmp_path / "route.yaml"
    path.write_text(yaml.safe_dump(manifest))
    requests = []

    def handler(request):
        requests.append(request)
        if existing and request.method == "POST":
            return httpx.Response(409, json={"error": "already exists"})
        return httpx.Response(200, json=manifest)

    client = Client()
    client.c.close()
    client.c = httpx.Client(transport=httpx.MockTransport(handler))
    try:
        config = MagicMock(spec=Configuration)
        config.data = {}
        config.new_v2_client.return_value = client
        apply_module = import_module("riocli.apply")
        result = CliRunner().invoke(
            apply_module.apply, ["--silent", str(path)], obj=config
        )
        assert result.exit_code == 0, result.output
    finally:
        client.c.close()

    assert [r.method for r in requests] == (["POST", "PUT"] if existing else ["POST"])
    for request in requests:
        payload = json.loads(request.content)["spec"]
        if "rateLimit" in spec:
            assert payload["rateLimit"] == spec["rateLimit"]
        else:
            assert "rateLimit" not in payload
            assert payload["sourceIPRange"] == spec["sourceIPRange"]


@pytest.mark.parametrize("format_type", ["json", "yaml"])
def test_inspect_preserves_rate_limit(monkeypatch, format_type):
    from rapyuta_io_sdk_v2 import StaticRoute

    inspect_module = import_module("riocli.static_route.inspect")
    rate_limit = {"average": 100, "period": "1m", "burst": 20}
    client = MagicMock()
    client.get_staticroute.return_value = StaticRoute.model_validate(
        {"metadata": {"name": "limited"}, "spec": {"rateLimit": rate_limit}}
    )
    monkeypatch.setattr(inspect_module, "new_v2_client", lambda: client)
    result = CliRunner().invoke(
        inspect_module.inspect_static_route, ["limited", "--format", format_type]
    )
    assert result.exit_code == 0, result.output
    assert yaml.safe_load(result.output)["spec"]["rateLimit"] == rate_limit

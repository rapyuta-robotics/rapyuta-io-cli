# Copyright 2026 Rapyuta Robotics
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

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest
from click.testing import CliRunner

from riocli.hwil.create import create_device
from riocli.jsonschema.validate import load_schema

VALID = ["12h", "1d", "600s", "10m"]
INVALID = ["invalid", "12", "h", "0h", "-1h", "1.5h", "12H", "1w", "P1D", " 12h", ""]


@pytest.fixture
def ctx_obj():
    obj = MagicMock()
    obj.data = {
        "email_id": "user@example.com",
        "organization_id": "org-guid",
        "project_id": "project-guid",
    }
    return obj


def _run(ctx_obj, expire_after):
    client = MagicMock()
    with patch("riocli.hwil.create.new_hwil_client", return_value=client):
        result = CliRunner().invoke(
            create_device,
            ["test-device", "--expire-after", expire_after],
            obj=ctx_obj,
        )
    return result, client


@pytest.mark.parametrize("value", INVALID)
def test_create_rejects_invalid_expire_after(ctx_obj, value):
    result, client = _run(ctx_obj, value)

    assert result.exit_code == 2
    assert "Invalid value for '--expire-after'" in result.output
    client.create_device.assert_not_called()


@pytest.mark.parametrize("value", VALID)
def test_create_accepts_valid_expire_after(ctx_obj, value):
    result, client = _run(ctx_obj, value)

    assert result.exit_code == 0, result.output
    labels = client.create_device.call_args.args[4]
    assert labels["expiry_after"] == value


def _device_manifest(expire_after):
    return {
        "apiVersion": "apiextensions.rapyuta.io/v1",
        "kind": "Device",
        "metadata": {"name": "test-device"},
        "spec": {
            "python": "python3",
            "virtual": {
                "enabled": True,
                "product": "sootballs",
                "expireAfter": expire_after,
            },
        },
    }


@pytest.mark.parametrize("value", INVALID)
def test_schema_rejects_invalid_expire_after(value):
    errors = list(load_schema("device").iter_errors(_device_manifest(value)))

    assert errors


@pytest.mark.parametrize("value", VALID)
def test_schema_accepts_valid_expire_after(value):
    errors = list(load_schema("device").iter_errors(_device_manifest(value)))

    assert not errors

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

from unittest.mock import MagicMock

import pytest
from munch import Munch, munchify

from jsonschema import ValidationError
from riocli.apply.util import KIND_TO_CLASS
from riocli.constants import ApplyResult, DeleteResult
from riocli.devicepool import util as pool_util
from riocli.devicepool.model import DevicePool
from riocli.exceptions import ResourceNotFound
from riocli.hwilclient.client import Client as HwilClient
from riocli.hwilclient.client import PoolNotFound

TOKEN = "rio-user-token-XYZ"

MANIFEST = {
    "apiVersion": "apiextensions.rapyuta.io/v1",
    "kind": "DevicePool",
    "metadata": {"name": "qa-informer-3k", "labels": {"team": "qa"}},
    "spec": {
        "devices": 600,
        "deploymentsPerDevice": 15,
        "mode": "lite",
        "expireAfter": "6h",
    },
}


def config(env="pr1719"):
    c = MagicMock()
    c.data = {
        "environment": env,
        "project_id": "project-abc",
        "organization_id": "org-xyz",
        "auth_token": TOKEN,
        "email_id": "jane.doe@rapyuta-robotics.com",
    }
    return c


def pool(state, **kw):
    return munchify(
        {
            "id": 41,
            "name": "qa-informer-3k",
            "state": state,
            "reason": "",
            "leftovers": False,
            "environment": "pr1719",
            "project_guid": "project-abc",
            "devices": 600,
            "progress": {"devices_ready": 0, "deployments_ready": 0, "eta_seconds": 0},
            **kw,
        }
    )


def manifest(**spec):
    # the applier instantiates models from munchified manifests (riocli/apply/parse.py)
    m = {**MANIFEST, "spec": {**MANIFEST["spec"], **spec}}
    return DevicePool(munchify(m))


# ---- schema and registration ---------------------------------------------------------------------------------------


def test_devicepool_is_an_apply_kind():
    assert KIND_TO_CLASS["devicepool"] is DevicePool


def test_schema_defaults_and_limits():
    p = manifest()
    assert p.spec.mode == "lite" and p.spec.wait is False
    with pytest.raises(ValidationError):
        manifest(mode="stock")  # stock is not a pool mode (HWIL v2.31)
    with pytest.raises(ValidationError):
        manifest(devices=0)


# ---- request body ---------------------------------------------------------------------------------------------------


def test_body_fills_the_rio_block_from_the_cli_config():
    body = pool_util.pool_body(
        manifest(deployment={"package": "flap", "version": "v1", "namePrefix": "f"}),
        config(),
    )
    assert (
        body["name"] == "qa-informer-3k"
        and body["devices"] == 600
        and body["deployments_per_device"] == 15
    )
    assert body["mode"] == "lite"
    assert body["rio"] == {
        "environment": "pr1719",
        "project_guid": "project-abc",
        "organization_guid": "org-xyz",
        "token": TOKEN,
    }
    assert body["labels"] == {
        "team": "qa",
        "expiry_after": "6h",
        "product": "scale",
        "user": "jane.doe",
    }
    assert body["deployment"] == {"package": "flap", "version": "v1", "name_prefix": "f"}


@pytest.mark.parametrize("env", ["ga", "prod", "staging", None])
def test_body_refuses_environments_other_than_dev_and_pr(env):
    c = config(env)
    if env is None:
        del c.data["environment"]  # a ga login has no environment key
    with pytest.raises(pool_util.PoolEnvironmentError):
        pool_util.pool_body(manifest(), c)


# ---- apply -----------------------------------------------------------------------------------------------------------


def hwil(get_pool=None, create=None):
    h = MagicMock()
    h.get_pool.side_effect = get_pool or PoolNotFound("pool not found")
    h.create_pool.return_value = create or pool("PENDING")
    return h


def test_apply_creates_a_missing_pool():
    h = hwil()
    c = config()
    c.new_hwil_client.return_value = h
    assert (
        manifest().apply(
            client=MagicMock(),
            v2_client=MagicMock(),
            config=c,
            retry_count=1,
            retry_interval=1,
        )
        == ApplyResult.CREATED
    )
    body = h.create_pool.call_args.args[0]
    assert body["rio"]["token"] == TOKEN and body["name"] == "qa-informer-3k"


def test_apply_waits_until_ready(monkeypatch):
    monkeypatch.setattr(pool_util.time, "sleep", lambda s: None)
    h = hwil()
    h.get_pool.side_effect = [PoolNotFound("x"), pool("BOOTSTRAPPING"), pool("READY")]
    c = config()
    c.new_hwil_client.return_value = h
    assert (
        manifest(wait=True).apply(
            client=None, v2_client=None, config=c, retry_count=1, retry_interval=1
        )
        == ApplyResult.CREATED
    )
    assert h.get_pool.call_count == 3


def test_apply_wait_fails_loudly_on_a_failed_pool(monkeypatch):
    monkeypatch.setattr(pool_util.time, "sleep", lambda s: None)
    h = hwil()
    h.get_pool.side_effect = [PoolNotFound("x"), pool("FAILED", reason="token_rejected")]
    c = config()
    c.new_hwil_client.return_value = h
    with pytest.raises(Exception, match="token_rejected"):
        manifest(wait=True).apply(
            client=None, v2_client=None, config=c, retry_count=1, retry_interval=1
        )


def test_apply_reports_a_live_pool_as_existing():
    h = hwil(get_pool=[pool("READY")])
    c = config()
    c.new_hwil_client.return_value = h
    p = manifest()
    assert (
        p.apply(client=None, v2_client=None, config=c, retry_count=1, retry_interval=1)
        == ApplyResult.EXISTS
    )
    h.create_pool.assert_not_called()


def test_apply_says_why_a_changed_pool_is_not_updated():
    h = hwil(get_pool=[pool("READY", devices=300)])
    c = config()
    c.new_hwil_client.return_value = h
    p = manifest()
    assert (
        p.apply(client=None, v2_client=None, config=c, retry_count=1, retry_interval=1)
        == ApplyResult.EXISTS
    )
    assert "cannot be resized" in p.exists_reason


def test_apply_explains_a_name_still_reserved_by_a_deleted_pool():
    """HWIL before v2.32 keeps a deleted pool's name reserved and answers 409: say why, not just already exists"""
    from rapyuta_io.utils import ConflictError

    h = hwil(get_pool=[pool("DELETED")])
    h.create_pool.side_effect = ConflictError("already exists")
    c = config()
    c.new_hwil_client.return_value = h
    with pytest.raises(Exception, match="new name"):
        manifest().apply(
            client=None, v2_client=None, config=c, retry_count=1, retry_interval=1
        )


def test_apply_recreates_a_deleted_pool_where_names_are_reusable():
    h = hwil(get_pool=[pool("DELETED")])
    c = config()
    c.new_hwil_client.return_value = h
    result = manifest().apply(
        client=None, v2_client=None, config=c, retry_count=1, retry_interval=1
    )
    assert result == ApplyResult.CREATED and h.create_pool.called


# ---- delete ----------------------------------------------------------------------------------------------------------


def test_delete_waits_and_prints_the_cleanup_hint(monkeypatch, capsys):
    monkeypatch.setattr(pool_util.time, "sleep", lambda s: None)
    h = hwil(get_pool=[pool("READY"), pool("DELETING"), pool("DELETED", leftovers=True)])
    c = config()
    c.new_hwil_client.return_value = h
    assert (
        manifest(wait=True).delete(
            client=None, v2_client=None, config=c, retry_count=1, retry_interval=1
        )
        == DeleteResult.DELETED
    )
    h.delete_pool.assert_called_once_with(41)
    assert "rio hwil pool cleanup qa-informer-3k" in capsys.readouterr().out


def test_delete_of_a_missing_pool_is_resource_not_found():
    h = hwil()
    c = config()
    c.new_hwil_client.return_value = h
    with pytest.raises(ResourceNotFound):
        manifest().delete(
            client=None, v2_client=None, config=c, retry_count=1, retry_interval=1
        )


# ---- HWIL client -----------------------------------------------------------------------------------------------------


def response(status, body):
    r = MagicMock()
    r.status_code = status
    r.json.return_value = body
    r.text = str(body)
    return r


def test_client_surfaces_hwil_validation_errors(monkeypatch):
    monkeypatch.setattr(
        "riocli.hwilclient.client.requests.post",
        lambda *a, **k: response(
            400, {"rio": {"environment": ["environment must be dev or pr<N>"]}}
        ),
    )
    with pytest.raises(ValueError, match="environment must be dev or pr<N>"):
        HwilClient(auth_token="t").create_pool({"name": "x"})


def test_client_maps_404_to_pool_not_found(monkeypatch):
    monkeypatch.setattr(
        "riocli.hwilclient.client.requests.get",
        lambda *a, **k: response(404, {"detail": "Not found."}),
    )
    with pytest.raises(PoolNotFound):
        HwilClient(auth_token="t").get_pool("nope")


# ---- cleanup ---------------------------------------------------------------------------------------------------------


def dep(name, labels, phase="Succeeded"):
    return Munch(metadata=Munch(name=name, labels=labels), status=Munch(phase=phase))


def test_cleanup_deletes_only_the_pools_labelled_objects(monkeypatch):
    v2 = MagicMock()
    monkeypatch.setattr(
        pool_util,
        "walk_pages",
        lambda fn, **kw: (
            iter(
                [
                    [
                        dep("flap-1", {"pool": "41"}),
                        dep("flap-2", {"pool": "41"}),
                        dep(
                            "flap-3", {"pool": "41"}, "Stopped"
                        ),  # deleted already: never touched
                    ]
                ]
            )
            if kw.get("label_selector") == ["pool=41"]
            else iter([])
        ),
    )
    v1 = MagicMock()
    v1.delete_device.return_value = Munch(status_code=200)
    v1.get_all_devices.return_value = [
        Munch(uuid="u1", name="qa-0001", labels=[Munch(key="pool", value="41")]),
        Munch(uuid="u2", name="other", labels=[Munch(key="pool", value="7")]),
        Munch(uuid="u3", name="nolabel", labels=[]),
    ]
    r = pool_util.cleanup_pool(pool("DELETED", leftovers=True), config(), v2, v1)
    assert sorted(c.args[0] for c in v2.delete_deployment.call_args_list) == [
        "flap-1",
        "flap-2",
    ]
    assert [c.args[0] for c in v1.delete_device.call_args_list] == ["u1"]
    assert r == {
        "deployments": 2,
        "deployments_failed": 0,
        "devices": 1,
        "devices_failed": 0,
        "already_gone": 0,
    }


def test_cleanup_refuses_another_environment_or_project():
    with pytest.raises(pool_util.PoolEnvironmentError):
        pool_util.cleanup_pool(
            pool("DELETED", environment="pr1534"), config(), MagicMock(), MagicMock()
        )
    with pytest.raises(pool_util.PoolEnvironmentError):
        pool_util.cleanup_pool(
            pool("DELETED", project_guid="project-other"),
            config(),
            MagicMock(),
            MagicMock(),
        )


def test_cleanup_refuses_a_pool_that_is_not_deleted():
    """cleanup removes what a finished teardown left behind; on a live pool it would delete working devices"""
    for state in ("READY", "DELETING", "BOOTSTRAPPING"):
        with pytest.raises(pool_util.PoolStateError):
            pool_util.cleanup_pool(pool(state), config(), MagicMock(), MagicMock())


# ---- rio hwil pool ... -----------------------------------------------------------------------------------------------


def test_pool_commands_are_registered():
    from riocli.hwil import hwildevice

    group = hwildevice.commands["pool"]
    assert sorted(group.commands) == ["cleanup", "delete", "inspect", "list"]


def test_list_prints_one_row_per_pool(monkeypatch):
    import importlib

    from click.testing import CliRunner

    pool_cmd = importlib.import_module(
        "riocli.hwil.pool"
    )  # riocli.hwil.pool the attribute is the click group
    h = MagicMock()
    h.list_pools.return_value = [
        pool(
            "READY",
            mode="lite",
            deployments_per_device=15,
            expiry_at="2026-11-01T18:00:00Z",
        )
    ]
    monkeypatch.setattr(pool_cmd, "new_hwil_client", lambda: h)
    out = CliRunner().invoke(pool_cmd.pool, ["list"])
    assert out.exit_code == 0, out.output
    assert "qa-informer-3k" in out.output and "READY" in out.output


def test_cleanup_command_asks_before_deleting(monkeypatch):
    import importlib

    from click.testing import CliRunner

    pool_cmd = importlib.import_module(
        "riocli.hwil.pool"
    )  # riocli.hwil.pool the attribute is the click group
    h = MagicMock()
    h.get_pool.return_value = pool("DELETED", leftovers=True)
    monkeypatch.setattr(pool_cmd, "new_hwil_client", lambda: h)
    called = MagicMock()
    monkeypatch.setattr(pool_cmd, "cleanup_pool", called)
    out = CliRunner().invoke(pool_cmd.pool, ["cleanup", "qa-informer-3k"], input="n\n")
    assert out.exit_code != 0 and not called.called


def test_cleanup_reports_objects_that_were_already_gone(monkeypatch):
    """riocli e2e 2026-11-01: a clean teardown leaves only Stopped deployments; cleanup said "deleted 60" because the
    listing returns Stopped ones and their 404s were counted as deletions"""
    from rapyuta_io_sdk_v2.exceptions import HttpNotFoundError

    v2 = MagicMock()
    v2.delete_deployment.side_effect = HttpNotFoundError("deployment not found")
    monkeypatch.setattr(
        pool_util,
        "walk_pages",
        lambda fn, **kw: iter(
            [[dep("flap-1", {"pool": "41"}), dep("flap-2", {"pool": "41"}, "Stopped")]]
        ),
    )
    v1 = MagicMock()
    v1.get_all_devices.return_value = []
    r = pool_util.cleanup_pool(pool("DELETED"), config(), v2, v1)
    assert [c.args[0] for c in v2.delete_deployment.call_args_list] == [
        "flap-1"
    ]  # Stopped ones are not touched
    assert r == {
        "deployments": 0,
        "deployments_failed": 0,
        "devices": 0,
        "devices_failed": 0,
        "already_gone": 1,
    }


# ---- PR #612 review (Copilot) ----------------------------------------------------------------------------------------


def test_apply_refuses_a_same_named_pool_in_another_target():
    """pool names are global in HWIL: a pool of this name in another environment/project is not this manifest's"""
    h = hwil(get_pool=[pool("READY", environment="pr1534")])
    c = config()
    c.new_hwil_client.return_value = h
    with pytest.raises(pool_util.PoolEnvironmentError, match="pr1534"):
        manifest().apply(
            client=None, v2_client=None, config=c, retry_count=1, retry_interval=1
        )
    h.create_pool.assert_not_called()


def test_delete_refuses_a_pool_in_another_target():
    h = hwil(get_pool=[pool("READY", project_guid="project-other")])
    c = config()
    c.new_hwil_client.return_value = h
    with pytest.raises(pool_util.PoolEnvironmentError, match="project-other"):
        manifest().delete(
            client=None, v2_client=None, config=c, retry_count=1, retry_interval=1
        )
    h.delete_pool.assert_not_called()


def test_dependencies_name_the_custom_package_version():
    assert manifest().list_dependencies() is None
    p = manifest(deployment={"package": "flap", "version": "v1.0.2"})
    assert p.list_dependencies() == ["package:flap:v1.0.2"]


def test_reapply_with_wait_waits_for_an_existing_pool(monkeypatch):
    monkeypatch.setattr(pool_util.time, "sleep", lambda s: None)
    h = hwil(get_pool=[pool("BOOTSTRAPPING"), pool("BOOTSTRAPPING"), pool("READY")])
    c = config()
    c.new_hwil_client.return_value = h
    result = manifest(wait=True).apply(
        client=None, v2_client=None, config=c, retry_count=1, retry_interval=1
    )
    assert result == ApplyResult.EXISTS and h.get_pool.call_count == 3
    h.create_pool.assert_not_called()


def test_reapply_reports_an_existing_failed_pool():
    h = hwil(get_pool=[pool("FAILED", reason="token_rejected")])
    c = config()
    c.new_hwil_client.return_value = h
    with pytest.raises(Exception, match="token_rejected"):
        manifest().apply(
            client=None, v2_client=None, config=c, retry_count=1, retry_interval=1
        )


def test_reapply_refuses_a_pool_being_deleted():
    h = hwil(get_pool=[pool("DELETING")])
    c = config()
    c.new_hwil_client.return_value = h
    with pytest.raises(pool_util.PoolStateError, match="DELETING"):
        manifest().apply(
            client=None, v2_client=None, config=c, retry_count=1, retry_interval=1
        )
    h.create_pool.assert_not_called()


def test_cleanup_reads_the_v1_device_delete_status(monkeypatch):
    """rapyuta_io's delete_device returns the HTTP response instead of raising: 404 is gone, other errors failed"""
    monkeypatch.setattr(pool_util, "walk_pages", lambda fn, **kw: iter([]))
    v1 = MagicMock()
    v1.get_all_devices.return_value = [
        Munch(uuid=u, name=u, labels=[Munch(key="pool", value="41")])
        for u in ("ok", "gone", "bad")
    ]
    v1.delete_device.side_effect = lambda uuid: Munch(
        status_code={"ok": 200, "gone": 404, "bad": 400}[uuid]
    )
    r = pool_util.cleanup_pool(pool("DELETED"), config(), MagicMock(), v1)
    assert r["devices"] == 1 and r["already_gone"] == 1 and r["devices_failed"] == 1


def test_schema_caps_deployments_per_device_like_hwil():
    """HWIL refuses more than POOL_MAX_DEPLOYMENTS_PER_DEVICE (15): fail at validation, before any request"""
    assert manifest(deploymentsPerDevice=15).spec.deploymentsPerDevice == 15
    with pytest.raises(ValidationError):
        manifest(deploymentsPerDevice=16)

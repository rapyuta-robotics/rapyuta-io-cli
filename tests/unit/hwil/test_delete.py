"""rio hwil delete warns that deleting a VM removes every other device of the same project (one resource group)."""

from unittest.mock import MagicMock, patch

from click.testing import CliRunner

from riocli.hwil.delete import delete_device


def test_delete_names_the_other_devices_of_the_project():
    client = MagicMock()
    client.list_devices.return_value = [
        {"id": 1, "name": "a", "labels": {"project": "project-x", "vm": "true"}},
        {"id": 2, "name": "b", "labels": {"project": "project-x", "vm": "true"}},
        {"id": 3, "name": "c", "labels": {"project": "project-y"}},
    ]
    with patch("riocli.hwil.delete.new_hwil_client", return_value=client):
        r = CliRunner().invoke(delete_device, ["a", "--force"])
    assert r.exit_code == 0, r.output
    warning = r.output.split("deleted too:")[1].splitlines()[0].strip()
    assert warning == "b"
    client.delete_device.assert_called_once_with(1)


def test_deleting_a_sysbox_device_warns_about_nothing():
    client = MagicMock()
    client.list_devices.return_value = [
        {"id": 1, "name": "pod", "labels": {"project": "project-x"}},
        {"id": 2, "name": "vm", "labels": {"project": "project-x", "vm": "true"}},
    ]
    with patch("riocli.hwil.delete.new_hwil_client", return_value=client):
        r = CliRunner().invoke(delete_device, ["pod", "--force"])
    assert r.exit_code == 0, r.output
    assert "deleted too" not in r.output


def test_a_refused_delete_is_not_reported_as_success():
    from riocli.hwilclient.client import Client

    resp = MagicMock(ok=False, status_code=403, text='{"detail":"CI-owned device"}')
    with patch("riocli.hwilclient.client.RestClient") as rc:
        rc.return_value.method.return_value.headers.return_value.execute.return_value = (
            resp
        )
        c = Client(token_provider=lambda: "t", hwil_host="https://hwilv3.rapyuta.io")
        try:
            c.delete_device(5)
        except Exception as e:
            assert "403" in str(e) and "CI-owned device" in str(e)
        else:
            raise AssertionError("403 on delete must raise")

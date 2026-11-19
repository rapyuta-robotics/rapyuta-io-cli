"""rio hwil delete warns that deleting a VM removes every other device of the same project (one resource group)."""

from unittest.mock import MagicMock, patch

from click.testing import CliRunner

from riocli.hwil.delete import delete_device


def test_delete_names_the_other_devices_of_the_project():
    client = MagicMock()
    client.list_devices.return_value = [
        {"id": 1, "name": "a", "labels": {"project": "project-x"}},
        {"id": 2, "name": "b", "labels": {"project": "project-x"}},
        {"id": 3, "name": "c", "labels": {"project": "project-y"}},
    ]
    with patch("riocli.hwil.delete.new_hwil_client", return_value=client):
        r = CliRunner().invoke(delete_device, ["a", "--force"])
    assert r.exit_code == 0, r.output
    assert (
        "b" in r.output.split("deleted too:")[1]
        and "c" not in r.output.split("deleted too:")[1]
    )
    client.delete_device.assert_called_once_with(1)

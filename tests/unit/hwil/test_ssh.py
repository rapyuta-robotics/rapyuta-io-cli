"""rio hwil ssh: HWIL VMs are key-only. Upload the user's own public key, then ssh with it; never show a password."""

from unittest.mock import MagicMock, patch

import pytest
from click.testing import CliRunner
from munch import munchify

from riocli.hwil.ssh import find_public_key, ssh


def _home(tmp_path, *names):
    d = tmp_path / ".ssh"
    d.mkdir()
    for n in names:
        (d / n).write_text("ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIExample me@laptop\n")
    return tmp_path


def test_find_public_key_prefers_ed25519(tmp_path, monkeypatch):
    monkeypatch.setenv("HOME", str(_home(tmp_path, "id_rsa.pub", "id_ed25519.pub")))
    assert find_public_key().endswith("/.ssh/id_ed25519.pub")


def test_find_public_key_explains_when_missing(tmp_path, monkeypatch):
    monkeypatch.setenv("HOME", str(tmp_path))
    with pytest.raises(FileNotFoundError, match="ssh-keygen"):
        find_public_key()


def test_ssh_uploads_key_then_runs_ssh_with_it(tmp_path, monkeypatch):
    home = _home(tmp_path, "id_ed25519.pub", "id_ed25519")
    monkeypatch.setenv("HOME", str(home))
    client = MagicMock()
    client.get_device.return_value = munchify(
        {"id": 7, "name": "vm-1", "username": "rr", "ip_address": "20.0.0.1"}
    )
    client.add_ssh_key.return_value = munchify(
        {"fingerprint": "SHA256:abc", "username": "rr"}
    )
    with (
        patch("riocli.hwil.ssh.new_hwil_client", return_value=client),
        patch("riocli.hwil.util.new_hwil_client", return_value=client),
        patch("riocli.hwil.util.find_device_id", return_value=7),
        patch("riocli.hwil.ssh.subprocess.call", return_value=0) as call,
    ):
        result = CliRunner().invoke(ssh, ["vm-1"])
    assert result.exit_code == 0, result.output
    assert client.add_ssh_key.call_args.args == (
        7,
        "ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIExample me@laptop",
    )
    assert call.call_args.args[0] == [
        "ssh",
        "-o",
        "IdentitiesOnly=yes",
        "-i",
        str(home / ".ssh/id_ed25519"),
        "rr@20.0.0.1",
    ]
    assert "password" not in result.output.lower()

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


def test_ssh_uploads_key_then_runs_ssh_with_it(
    tmp_path, monkeypatch
):  # from an office IP
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
        result = CliRunner().invoke(ssh, ["vm-1", "--source-ip", "121.2.38.2"])
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


def _client():
    client = MagicMock()
    client.get_device.return_value = munchify(
        {"id": 7, "name": "vm-1", "username": "rr", "ip_address": "20.0.0.1"}
    )
    client.add_ssh_key.return_value = munchify(
        {"fingerprint": "SHA256:abc", "username": "rr"}
    )
    client.grant_ssh_access.return_value = munchify(
        {"expires_at": "2026-11-19T12:00:00Z"}
    )
    return client


def _run(client, args):
    with (
        patch("riocli.hwil.ssh.new_hwil_client", return_value=client),
        patch("riocli.hwil.util.new_hwil_client", return_value=client),
        patch("riocli.hwil.util.find_device_id", return_value=7),
        patch("riocli.hwil.ssh.subprocess.call", return_value=0),
    ):
        return CliRunner().invoke(ssh, args)


def test_outside_office_opens_jit_access_first(tmp_path, monkeypatch):
    monkeypatch.setenv("HOME", str(_home(tmp_path, "id_ed25519.pub")))
    client = _client()
    with patch("riocli.hwil.ssh.detect_public_ip", return_value="52.10.20.30"):
        r = _run(client, ["vm-1", "--duration", "60"])
    assert r.exit_code == 0, r.output
    client.grant_ssh_access.assert_called_once_with(7, "52.10.20.30", 60)
    assert "2026-11-19T12:00:00Z" in r.output


def test_office_ip_needs_no_jit(tmp_path, monkeypatch):
    monkeypatch.setenv("HOME", str(_home(tmp_path, "id_ed25519.pub")))
    client = _client()
    r = _run(client, ["vm-1", "--source-ip", "121.2.38.2"])
    assert r.exit_code == 0, r.output
    assert not client.grant_ssh_access.called and client.add_ssh_key.called


def test_pinned_host_key_is_used_with_strict_checking(tmp_path, monkeypatch):
    monkeypatch.setenv("HOME", str(_home(tmp_path, "id_ed25519.pub", "id_ed25519")))
    client = _client()
    client.get_device.return_value = munchify(
        {
            "id": 7,
            "name": "vm-1",
            "username": "rr",
            "ip_address": "20.0.0.1",
            "ssh_host_key": "ssh-ed25519 AAAAC3NzaPINNED",
        }
    )
    with (
        patch("riocli.hwil.ssh.new_hwil_client", return_value=client),
        patch("riocli.hwil.util.new_hwil_client", return_value=client),
        patch("riocli.hwil.util.find_device_id", return_value=7),
        patch("riocli.hwil.ssh.subprocess.call", return_value=0) as call,
    ):
        r = CliRunner().invoke(ssh, ["vm-1", "--source-ip", "121.2.38.2"])
    assert r.exit_code == 0, r.output
    cmd = call.call_args.args[0]
    known = str(tmp_path / ".config/rio-cli/hwil_known_hosts")
    assert "HostKeyAlias=vm-1" in cmd and f"UserKnownHostsFile={known}" in cmd
    assert "StrictHostKeyChecking=yes" in cmd and "HostKeyAlgorithms=ssh-ed25519" in cmd
    assert open(known).read() == "vm-1 ssh-ed25519 AAAAC3NzaPINNED\n"


def test_pin_replaces_only_that_devices_entry(tmp_path):
    from riocli.hwil.ssh import pin_host_key

    path = str(tmp_path / "kh")
    pin_host_key("vm-1", "ssh-ed25519 OLD", path)
    pin_host_key("vm-2", "ssh-ed25519 OTHER", path)
    pin_host_key("vm-1", "ssh-ed25519 NEW", path)
    assert sorted(open(path).read().splitlines()) == [
        "vm-1 ssh-ed25519 NEW",
        "vm-2 ssh-ed25519 OTHER",
    ]


def test_pin_refuses_a_non_ed25519_key(tmp_path):
    from riocli.hwil.ssh import pin_host_key

    with pytest.raises(ValueError):
        pin_host_key("vm-1", "ssh-rsa AAAA", str(tmp_path / "kh"))

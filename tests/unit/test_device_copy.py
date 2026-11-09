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

import shlex
from subprocess import CalledProcessError
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import pytest
from click.testing import CliRunner

from riocli.device.tools.scp import scp
from riocli.device.tools.util import copy_from_device, copy_to_device

GUID = "device-guid"
PIPING_503 = (
    "curl: (22) The requested URL returned error: 503\n"
    "upstream connect error or disconnect/reset before headers."
)


def _client(device_output: str | None) -> MagicMock:
    client = MagicMock()
    client.execute_command.side_effect = lambda command, **_: (
        {"jid": "job-1"} if command.run_async else {GUID: device_output}
    )
    client.fetch_cmd_result.return_value = {GUID: device_output}
    return client


def _copy(device_output: str | None, run_async: bool = False, dest="/tmp/a.tar.gz"):
    client = _client(device_output)
    with (
        patch("riocli.device.tools.util.Configuration") as config,
        patch("riocli.device.tools.util.new_client", return_value=client),
        patch("riocli.device.tools.util.run_bash") as run_bash,
    ):
        config.return_value.piping_server = "https://piping.example"
        copy_to_device(GUID, "edgevm1", "tests.tar.gz", dest, run_async=run_async)

    return client.execute_command.call_args.kwargs["command"], run_bash


@pytest.mark.parametrize("run_async", [False, True])
def test_copy_succeeds_on_marker(run_async):
    command, run_bash = _copy("__RIO_COPY_SUCCESS__", run_async=run_async)

    # Both curls must fail on an HTTP error, or the error page is saved as the file.
    assert "curl -sSf -o /tmp/a.tar.gz" in command.cmd
    assert run_bash.call_args.args[0].startswith("curl -sSfT tests.tar.gz ")


@pytest.mark.parametrize("run_async", [False, True])
@pytest.mark.parametrize("output", [PIPING_503, "", None])
def test_copy_fails_without_marker(run_async, output):
    # Device output without the marker (what a 503 yields with curl -f) must fail.
    with pytest.raises(SystemExit) as exc:
        _copy(output, run_async=run_async)

    assert exc.value.code == 1


def test_marker_must_be_a_whole_line():
    # A bash syntax error echoes the offending line, marker included.
    echoed = "bash: -c: line 1: `curl ... && echo '__RIO_COPY_SUCCESS__''"
    with pytest.raises(SystemExit):
        _copy(echoed)


def test_dest_is_shell_quoted():
    command, _ = _copy("__RIO_COPY_SUCCESS__", dest="/tmp/a b(c;d")

    remote_cmd = shlex.split(command.cmd)[2]
    assert shlex.split(remote_cmd)[:4] == ["curl", "-sSf", "-o", "/tmp/a b(c;d"]


def test_scp_command_fails_on_piping_503():
    # scp always runs async, so this is the path the CLI takes.
    client = _client(PIPING_503)
    device = SimpleNamespace(uuid=GUID, name="edgevm1")
    with (
        patch("riocli.device.tools.scp.new_client", return_value=client),
        patch(
            "riocli.device.tools.scp.is_remote_path",
            side_effect=[(None, "a"), (GUID, "/tmp/a")],
        ),
        patch("riocli.device.tools.util.Configuration"),
        patch("riocli.device.tools.util.new_client", return_value=client),
        patch("riocli.device.tools.util.run_bash"),
    ):
        client.get_all_devices.return_value = [device]
        result = CliRunner().invoke(scp, ["a", "edgevm1:/tmp/a"])

    assert result.exit_code == 1
    assert "Files copied successfully" not in result.output


def test_copy_from_device_fails_on_http_error():
    client = MagicMock()
    client.get_fileupload.return_value.status.status = "COMPLETED"
    client.download_fileupload.return_value = {"url": "https://blob.example/x?sig=s"}
    error = CalledProcessError(22, ["curl"])
    with (
        patch("riocli.device.tools.util.new_v2_client", return_value=client),
        patch("riocli.device.tools.util.run_bash", side_effect=error) as run_bash,
        pytest.raises(
            Exception, match=r"Failed to download '/var/log/x' \(curl exit 22\)"
        ),
    ):
        copy_from_device(GUID, "/var/log/x", "x")

    assert run_bash.call_args.args[0].startswith("curl -f -o ")

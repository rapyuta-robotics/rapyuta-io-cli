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

from riocli.device.tools.util import copy_to_device

GUID = "device-guid"
PIPING_503 = (
    "curl: (22) The requested URL returned error: 503\n"
    "upstream connect error or disconnect/reset before headers."
)


def _copy(device_output: str):
    client = MagicMock()
    client.execute_command.return_value = {GUID: device_output}
    with (
        patch("riocli.device.tools.util.Configuration") as config,
        patch("riocli.device.tools.util.new_client", return_value=client),
        patch("riocli.device.tools.util.run_bash") as run_bash,
    ):
        config.return_value.piping_server = "https://piping.example"
        copy_to_device(GUID, "edgevm1", "tests.tar.gz", "/tmp/tests.tar.gz")

    return client.execute_command.call_args.kwargs["command"], run_bash


def test_copy_succeeds_on_marker():
    command, run_bash = _copy("__RIO_COPY_SUCCESS__")

    # Both curls must fail on an HTTP error, or the error page is saved as the file.
    assert "curl -sSf -o /tmp/tests.tar.gz" in command.cmd
    assert run_bash.call_args.args[0].startswith("curl -sSfT tests.tar.gz ")


def test_copy_fails_without_marker():
    # The piping server answered 503: curl -f exits non-zero, so no marker.
    with pytest.raises(SystemExit) as exc:
        _copy(PIPING_503)

    assert exc.value.code == 1


def test_copy_fails_on_empty_output():
    with pytest.raises(SystemExit):
        _copy("")

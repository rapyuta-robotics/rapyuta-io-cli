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

"""Tests for ssh-add wrapper functions."""

from __future__ import annotations

from unittest.mock import patch

import pytest

from riocli.ssh.util import add_to_ssh_agent, remove_from_ssh_agent

from .conftest import _make_subprocess_result


class TestSSHAddWrappers:
    """Tests for add_to_ssh_agent() and remove_from_ssh_agent()."""

    @patch("riocli.ssh.util.subprocess.run")
    def test_add_to_ssh_agent_success(self, mock_run, tmp_path):
        mock_run.return_value = _make_subprocess_result()
        priv = tmp_path / "rio_ed25519"
        priv.write_text("fake key")

        add_to_ssh_agent(priv, lifetime=120)

        mock_run.assert_called_once_with(
            ["ssh-add", "-t", "120", str(priv)],
            capture_output=True,
            text=True,
        )

    @patch("riocli.ssh.util.subprocess.run")
    def test_add_to_ssh_agent_default_lifetime(self, mock_run, tmp_path):
        mock_run.return_value = _make_subprocess_result()
        priv = tmp_path / "rio_ed25519"
        priv.write_text("fake key")

        add_to_ssh_agent(priv)

        mock_run.assert_called_once_with(
            ["ssh-add", "-t", "300", str(priv)],
            capture_output=True,
            text=True,
        )

    @patch("riocli.ssh.util.subprocess.run")
    def test_add_to_ssh_agent_failure(self, mock_run, tmp_path):
        mock_run.return_value = _make_subprocess_result(
            returncode=1,
            stderr="Could not open a connection to your agent",
        )
        priv = tmp_path / "rio_ed25519"
        priv.write_text("fake key")

        with pytest.raises(RuntimeError, match="Failed to add key"):
            add_to_ssh_agent(priv)

    @patch("riocli.ssh.util.subprocess.run")
    def test_add_to_ssh_agent_binary_not_found(self, mock_run, tmp_path):
        """FileNotFoundError from subprocess (ssh-add not on PATH) becomes RuntimeError."""
        mock_run.side_effect = FileNotFoundError("No such file or directory: 'ssh-add'")
        priv = tmp_path / "rio_ed25519"
        priv.write_text("fake key")

        with pytest.raises(RuntimeError, match="ssh-add not found"):
            add_to_ssh_agent(priv)

    @patch("riocli.ssh.util.subprocess.run")
    def test_remove_from_ssh_agent_success(self, mock_run, tmp_path):
        mock_run.return_value = _make_subprocess_result()
        priv = tmp_path / "rio_ed25519"
        priv.write_text("fake key")

        remove_from_ssh_agent(priv)

        mock_run.assert_called_once_with(
            ["ssh-add", "-d", str(priv)],
            capture_output=True,
            text=True,
        )

    @patch("riocli.ssh.util.subprocess.run")
    def test_remove_from_ssh_agent_failure_silenced(self, mock_run, tmp_path):
        """remove_from_ssh_agent silently ignores failures."""
        mock_run.return_value = _make_subprocess_result(
            returncode=1,
            stderr="Could not remove identity",
        )
        priv = tmp_path / "rio_ed25519"
        priv.write_text("fake key")

        # Should NOT raise
        remove_from_ssh_agent(priv)

    @patch("riocli.ssh.util.subprocess.run")
    def test_remove_from_ssh_agent_oserror_silenced(self, mock_run, tmp_path):
        """OSError (e.g. ssh-add not found) should be silently ignored."""
        mock_run.side_effect = OSError("No such file or directory")
        priv = tmp_path / "rio_ed25519"
        priv.write_text("fake key")

        # Should NOT raise
        remove_from_ssh_agent(priv)

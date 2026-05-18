# Copyright 2025 Rapyuta Robotics
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

import io
import sys  # noqa: F401
from unittest.mock import patch

import pytest  # noqa: F401

from riocli.utils.spinner import DummySpinner, with_spinner


class TestDummySpinnerClosedStream:
    """Verify DummySpinner survives closed/broken stdout — reproduces the CI crash."""

    def test_ok_survives_closed_stdout(self):
        """spinner.ok() must not raise when stdout is closed (CI teardown scenario)."""
        spinner = DummySpinner(text="test")
        spinner.text = "some operation"
        closed = io.StringIO()
        closed.close()
        with patch("sys.stdout", closed):
            # Must not raise ValueError
            spinner.ok("OK")

    def test_fail_survives_closed_stdout(self):
        """spinner.fail() must not raise when stdout is closed."""
        spinner = DummySpinner(text="test")
        spinner.text = "some operation"
        closed = io.StringIO()
        closed.close()
        with patch("sys.stdout", closed):
            spinner.fail("FAIL")

    def test_write_survives_closed_stdout(self):
        """spinner.write() must not raise when stdout is closed."""
        spinner = DummySpinner()
        closed = io.StringIO()
        closed.close()
        with patch("sys.stdout", closed):
            spinner.write("some message")

    def test_ok_survives_oserror_on_stdout(self):
        """spinner.ok() must not raise on OSError (broken pipe)."""
        spinner = DummySpinner()
        spinner.text = "work"
        broken = io.StringIO()

        def raise_oserror(*args, **kwargs):
            raise OSError("Broken pipe")

        broken.write = raise_oserror
        with patch("sys.stdout", broken):
            spinner.ok("OK")

    def test_ok_writes_to_stderr(self, capsys):
        """DummySpinner.ok() output goes to stderr, not stdout."""
        spinner = DummySpinner()
        spinner.text = "my task"
        spinner.ok("OK")
        captured = capsys.readouterr()
        assert "OK" in captured.err
        assert "my task" in captured.err
        # Nothing written to stdout
        assert captured.out == ""

    def test_fail_writes_to_stderr(self, capsys):
        """DummySpinner.fail() output goes to stderr, not stdout."""
        spinner = DummySpinner()
        spinner.text = "my task"
        spinner.fail("FAIL")
        captured = capsys.readouterr()
        assert "FAIL" in captured.err
        assert "my task" in captured.err
        assert captured.out == ""

    def test_write_writes_to_stderr(self, capsys):
        """DummySpinner.write() output goes to stderr, not stdout."""
        spinner = DummySpinner()
        spinner.write("hello stderr")
        captured = capsys.readouterr()
        assert "hello stderr" in captured.err
        assert captured.out == ""


class TestDummySpinnerChainedAttrs:
    """Verify spinner.green.ok() / spinner.red.fail() chaining works correctly."""

    def test_chained_ok_survives_closed_stdout(self):
        """spinner.green.ok() (attribute chaining) must not raise on closed stdout."""
        spinner = DummySpinner()
        spinner.text = "chained op"
        closed = io.StringIO()
        closed.close()
        with patch("sys.stdout", closed):
            # spinner.green returns self via __getattr__; .ok() should be safe
            spinner.green.ok("OK")

    def test_chained_fail_survives_closed_stdout(self):
        """spinner.red.fail() must not raise on closed stdout."""
        spinner = DummySpinner()
        spinner.text = "chained op"
        closed = io.StringIO()
        closed.close()
        with patch("sys.stdout", closed):
            spinner.red.fail("FAIL")


class TestDummySpinnerContextManager:
    """Verify DummySpinner works as a context manager (used by with_spinner)."""

    def test_context_manager_enter_returns_self(self):
        spinner = DummySpinner()
        with spinner as s:
            assert s is spinner

    def test_context_manager_exit_returns_false(self):
        spinner = DummySpinner()
        result = spinner.__exit__(None, None, None)
        assert result is False

    def test_hidden_returns_self(self):
        spinner = DummySpinner()
        assert spinner.hidden() is spinner


class TestWithSpinnerDecorator:
    """Verify with_spinner uses DummySpinner in non-TTY environments."""

    def test_uses_dummy_spinner_when_not_tty(self):
        """In CI (non-TTY stdout), DummySpinner should be injected."""
        received = {}

        @with_spinner(text="Testing...")
        def my_func(spinner=None):
            received["spinner"] = spinner

        with patch("sys.stdout") as mock_stdout:
            mock_stdout.isatty.return_value = False
            my_func()

        assert isinstance(received["spinner"], DummySpinner)

    def test_dummy_spinner_ok_in_decorated_function_survives_closed_stdout(self):
        """Full decorator path: ok() call in function body must not crash on closed stdout."""
        closed = io.StringIO()
        closed.close()

        @with_spinner(text="Running...")
        def my_func(spinner=None):
            spinner.text = "done"
            spinner.ok("OK")

        with patch("sys.stdout", closed):
            # isatty() on a closed StringIO raises ValueError; patch isatty separately
            with patch.object(closed, "isatty", return_value=False):
                my_func()  # Must not raise

    def test_dummy_spinner_fail_in_decorated_function_survives_closed_stdout(self):
        """Full decorator path: fail() call must not crash on closed stdout."""
        closed = io.StringIO()
        closed.close()

        @with_spinner(text="Running...")
        def my_func(spinner=None):
            spinner.text = "failed"
            spinner.fail("FAIL")

        with patch("sys.stdout", closed):
            with patch.object(closed, "isatty", return_value=False):
                my_func()  # Must not raise

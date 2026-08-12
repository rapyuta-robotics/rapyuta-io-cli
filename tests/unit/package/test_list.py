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

import munch
import pytest
from click.testing import CliRunner

from riocli.package.list import list_packages


def package(name: str, version: str = "1.0.0") -> munch.Munch:
    return munch.munchify(
        {
            "metadata": {
                "name": name,
                "version": version,
                "guid": f"pkg-{name}-{version}",
                "description": f"{name} description",
            }
        }
    )


# Covers every position the filter word can occupy in a name: at the start,
# in the middle, and absent altogether.
PACKAGES = [
    package("test-pkg-abc"),
    package("my-test-pkg"),
    package("unrelated-pkg"),
]


@pytest.fixture
def runner():
    return CliRunner()


@pytest.fixture
def packages():
    """Patch the client and pagination so the command lists a fixed set of
    packages, leaving the CLI's own client-side filtering under test."""
    with (
        patch("riocli.package.list.new_v2_client", return_value=MagicMock()),
        patch("riocli.package.list.walk_pages", return_value=iter([PACKAGES])),
    ):
        yield


class TestFilterWord:
    def test_name_starting_with_the_filter_word_is_listed(self, runner, packages):
        # str.find() returns 0 for a match at index 0, and `not 0` is True, so
        # this package used to be the one case the filter dropped.
        result = runner.invoke(list_packages, ["--filter", "test-pkg"])

        assert result.exit_code == 0
        assert "test-pkg-abc" in result.output

    def test_name_containing_the_filter_word_is_listed(self, runner, packages):
        result = runner.invoke(list_packages, ["--filter", "test-pkg"])

        assert result.exit_code == 0
        assert "my-test-pkg" in result.output

    def test_name_without_the_filter_word_is_not_listed(self, runner, packages):
        # str.find() returns -1 when absent, and `not -1` is False, so a
        # non-matching package used to be listed anyway.
        result = runner.invoke(list_packages, ["--filter", "test-pkg"])

        assert result.exit_code == 0
        assert "unrelated-pkg" not in result.output

    def test_filter_matching_nothing_lists_no_packages(self, runner, packages):
        result = runner.invoke(list_packages, ["--filter", "no-such-package"])

        assert result.exit_code == 0
        for pkg in PACKAGES:
            assert pkg.metadata.name not in result.output

    def test_no_filter_lists_every_package(self, runner, packages):
        result = runner.invoke(list_packages, [])

        assert result.exit_code == 0
        for pkg in PACKAGES:
            assert pkg.metadata.name in result.output

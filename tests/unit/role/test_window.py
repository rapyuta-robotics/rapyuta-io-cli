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

from datetime import datetime, timedelta, timezone

import click
import pytest

from riocli.role.window import (
    format_time,
    format_utc,
    format_window,
    parse_duration,
    parse_time,
    resolve_window,
    window_status,
)
from tests.unit.role.conftest import NOW

JST = timezone(timedelta(hours=9))


class TestParseTime:
    def test_explicit_offset_is_kept(self):
        parsed = parse_time("2026-10-26T17:00:00+05:30")

        assert parsed.utcoffset() == timedelta(hours=5, minutes=30)
        assert parsed == datetime(2026, 10, 26, 11, 30, tzinfo=timezone.utc)

    def test_z_suffix_is_utc(self):
        assert parse_time("2026-10-26T08:00:00Z") == datetime(
            2026, 10, 26, 8, 0, tzinfo=timezone.utc
        )

    def test_without_offset_uses_local_zone(self):
        parsed = parse_time("2026-10-26T17:00")

        assert parsed.utcoffset() == timedelta(hours=9)
        assert parsed == datetime(2026, 10, 26, 8, 0, tzinfo=timezone.utc)

    @pytest.mark.parametrize("value", ["", "tomorrow", "2026-13-01T00:00:00Z"])
    def test_unparsable_is_usage_error(self, value):
        with pytest.raises(click.UsageError):
            parse_time(value)


class TestParseDuration:
    @pytest.mark.parametrize(
        "value, expected",
        [
            ("8h", timedelta(hours=8)),
            ("90m", timedelta(minutes=90)),
            ("1d", timedelta(days=1)),
            ("2h30m", timedelta(hours=2, minutes=30)),
            ("1d2h3m", timedelta(days=1, hours=2, minutes=3)),
        ],
    )
    def test_valid(self, value, expected):
        assert parse_duration(value) == expected

    @pytest.mark.parametrize("value", ["", "8", "30m2h", "1w", "0m", "h", "-1h"])
    def test_invalid_is_usage_error(self, value):
        with pytest.raises(click.UsageError):
            parse_duration(value)


class TestResolveWindow:
    def test_no_options_is_permanent(self):
        assert resolve_window(None, None, None, NOW) == (None, None)

    def test_duration_counts_from_now(self):
        assert resolve_window(None, None, "8h", NOW) == (None, NOW + timedelta(hours=8))

    def test_duration_counts_from_start(self):
        start, end = resolve_window("2026-10-27T09:00:00+09:00", None, "8h", NOW)

        assert start == datetime(2026, 10, 27, 9, 0, tzinfo=JST)
        assert end == datetime(2026, 10, 27, 17, 0, tzinfo=JST)

    def test_absolute_window(self):
        start, end = resolve_window(
            "2026-10-27T09:00:00+09:00", "2026-10-27T17:00:00+09:00", None, NOW
        )

        assert start == datetime(2026, 10, 27, 0, 0, tzinfo=timezone.utc)
        assert end == datetime(2026, 10, 27, 8, 0, tzinfo=timezone.utc)

    def test_not_after_with_duration_is_usage_error(self):
        with pytest.raises(click.UsageError, match="--not-after.*--for"):
            resolve_window(None, "2026-10-27T17:00:00+09:00", "8h", NOW)

    def test_not_before_alone_is_usage_error(self):
        with pytest.raises(click.UsageError, match="--not-before"):
            resolve_window("2026-10-27T09:00:00+09:00", None, None, NOW)


class TestWindowStatus:
    def test_permanent_is_empty(self):
        assert window_status(None, None, NOW) == ""

    def test_active(self):
        end = NOW + timedelta(hours=2, minutes=10, seconds=59)

        assert window_status(None, end, NOW) == "2h 10m left"

    def test_active_with_start_in_past(self):
        start = NOW - timedelta(hours=1)
        end = NOW + timedelta(minutes=45)

        assert window_status(start, end, NOW) == "45m left"

    def test_not_started(self):
        start = NOW + timedelta(days=1, hours=3)
        end = start + timedelta(hours=8)

        assert window_status(start, end, NOW) == "starts in 1d 3h"

    def test_ended(self):
        assert window_status(None, NOW, NOW) == "ended"

    def test_less_than_a_minute(self):
        assert window_status(None, NOW + timedelta(seconds=30), NOW) == "0m left"


class TestFormat:
    def test_format_time_is_local_with_offset(self):
        assert (
            format_time(datetime(2026, 10, 26, 8, 0, tzinfo=timezone.utc))
            == "2026-10-26T17:00:00+09:00"
        )

    def test_format_utc(self):
        assert (
            format_utc(datetime(2026, 10, 26, 17, 0, tzinfo=JST))
            == "2026-10-26T08:00:00Z"
        )

    def test_format_window_without_start(self):
        end = datetime(2026, 10, 26, 8, 0, tzinfo=timezone.utc)

        assert format_window(None, end) == (
            "now – 2026-10-26T17:00:00+09:00 (local) / now – 2026-10-26T08:00:00Z UTC"
        )

    def test_format_window_with_start(self):
        start = datetime(2026, 10, 26, 0, 0, tzinfo=timezone.utc)
        end = datetime(2026, 10, 26, 8, 0, tzinfo=timezone.utc)

        assert format_window(start, end) == (
            "2026-10-26T09:00:00+09:00 – 2026-10-26T17:00:00+09:00 (local) / "
            "2026-10-26T00:00:00Z – 2026-10-26T08:00:00Z UTC"
        )

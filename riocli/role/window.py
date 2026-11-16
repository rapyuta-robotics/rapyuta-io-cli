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
"""Time windows of role bindings: input parsing, status and display."""

import re
from datetime import datetime, timedelta, timezone

import click
from dateutil.parser import isoparse

from riocli.utils.time import format_duration

_DURATION = re.compile(r"^(?:(\d+)d)?(?:(\d+)h)?(?:(\d+)m)?$")


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


def parse_time(value: str) -> datetime:
    """Parse an ISO 8601 time. A value without an offset is in the local zone.

    dateutil keeps explicit offsets, unlike parsedatetime, so "+09:00" is never
    shifted.
    """
    try:
        parsed = isoparse(value)
    except (ValueError, OverflowError):
        raise click.UsageError(
            f"invalid time '{value}': use ISO 8601, for example 2026-10-26T17:00:00+09:00"
        )

    if parsed.tzinfo is None:
        parsed = parsed.astimezone()

    return parsed


def parse_duration(value: str) -> timedelta:
    """Parse a duration such as 8h, 90m, 1d or 2h30m.

    This is not the grammar of 'rio service-account token create --expiry'
    ('3 days', 'in 2 hours'): that parser drops time zone offsets, which
    --not-before and --not-after must keep.
    """
    match = _DURATION.match(value)
    if not value or match is None:
        raise click.UsageError(
            f"invalid duration '{value}': use days, hours and minutes, for example 8h or 2h30m"
        )

    days, hours, minutes = (int(g or 0) for g in match.groups())
    duration = timedelta(days=days, hours=hours, minutes=minutes)
    if duration <= timedelta(0):
        raise click.UsageError(f"invalid duration '{value}': must be longer than zero")

    return duration


def resolve_window(
    not_before: str | None,
    not_after: str | None,
    duration: str | None,
    now: datetime,
) -> tuple[datetime | None, datetime | None]:
    """Turn --not-before, --not-after and --for into (start, end).

    Returns (None, None) for a permanent binding. --for counts from the start
    when one is given, else from now. Rules the server enforces (end in the
    past, end before start) are left to it.
    """
    if not_after and duration:
        raise click.UsageError("use either --not-after or --for, not both")

    if not_before and not (not_after or duration):
        raise click.UsageError("--not-before needs --not-after or --for")

    start = parse_time(not_before) if not_before else None

    end = None
    if not_after:
        end = parse_time(not_after)
    elif duration:
        end = (start or now) + parse_duration(duration)

    return start, end


def window_status(
    not_before: datetime | None, not_after: datetime | None, now: datetime
) -> str:
    """Return 'starts in …', '… left', 'Expired', or '' for a permanent binding.

    Durations use the same wording as 'rio service-account token list'.
    """
    if not_after is None:
        return ""

    if not_before is not None and now < not_before:
        return f"starts in {format_duration(not_before - now)}"

    if now < not_after:
        return f"{format_duration(not_after - now)} left"

    return "Expired"


def same_time(a: datetime | None, b: datetime | None) -> bool:
    """Whether two optional times are equal to the second; both None counts as equal."""
    if a is None or b is None:
        return a is b

    return a.replace(microsecond=0) == b.replace(microsecond=0)


def format_time(t: datetime) -> str:
    """Local time with its offset; accepted back by --not-after."""
    return t.astimezone().isoformat(timespec="seconds")


def format_utc(t: datetime) -> str:
    return t.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def format_window(not_before: datetime | None, not_after: datetime) -> str:
    local_start = format_time(not_before) if not_before else "now"
    utc_start = format_utc(not_before) if not_before else "now"

    return (
        f"{local_start} – {format_time(not_after)} (local) / "
        f"{utc_start} – {format_utc(not_after)} UTC"
    )

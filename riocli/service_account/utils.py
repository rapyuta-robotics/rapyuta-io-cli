# Copyright 2024 Rapyuta Robotics
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

from datetime import datetime, timedelta, timezone

import click
import parsedatetime as pdt


def parse_human_readable_time_to_iso(time_str: str | None) -> str | None:
    """
    Parses a human-readable time string and converts it to an ISO 8601 formatted string in UTC.

    Args:
        time_str (str | None): Time specification with two possible cases:
            - None for default expiry (90 days)
            - 0 for no expiry.
            - String with relative time (e.g., '3 days', 'in 2 hours') or ISO 8601 timestamp

    Returns:
        str | None: ISO 8601 formatted string in UTC, or None for no expiry case
    """

    if time_str is None:
        return None

    if time_str == "0":
        return "0001-01-01T00:00:00Z"

    time_str = time_str.strip()

    # Handle human-readable time
    cal = pdt.Calendar()
    now = datetime.now(timezone.utc)
    time_struct, parse_status = cal.parse(time_str, now)

    if parse_status == 0:
        raise click.UsageError(
            f"Invalid time format: '{time_str}'. \n"
            f"Please use:\n"
            f"- A relative format (e.g., '3 days', 'in 2 hours')\n"
            f"- An ISO 8601 format (e.g., '2025-12-31T23:59:59+00:00')\n"
            f"- Leave empty for no expiry (infinite duration)"
        )

    dt = datetime(*time_struct[:6], tzinfo=timezone.utc)
    return dt.isoformat()


def convert_utc_to_offset(utc_datetime: datetime, offset_str: str) -> str:
    """
    Convert a UTC datetime object to a datetime string with the given offset.

    Args:
        utc_datetime (datetime): UTC datetime object (timezone-aware or naive as UTC)
        offset_str (str): Offset string in format '+HH:MM' or '-HH:MM'

    Returns:
        str: Datetime string with the given offset applied
    """
    if utc_datetime.tzinfo is None:
        utc_datetime = utc_datetime.replace(tzinfo=timezone.utc)

    # Parse offset string
    sign = 1 if offset_str[0] == "+" else -1
    hours, minutes = map(int, offset_str[1:].split(":"))
    offset = timedelta(hours=hours, minutes=minutes) * sign
    target_tz = timezone(offset)

    # Convert to target timezone
    local_dt = utc_datetime.astimezone(target_tz)
    return local_dt.isoformat()


def calculate_time_remaining(expiry_datetime: datetime) -> str:
    """
    Calculate the relative time remaining until expiry.

    Args:
        expiry_datetime (datetime): The expiry datetime (timezone-aware or naive as UTC)

    Returns:
        str: Human-readable time remaining (e.g., '2 days, 3 hours, 15 minutes' or 'Expired')
    """
    if expiry_datetime.tzinfo is None:
        expiry_datetime = expiry_datetime.replace(tzinfo=timezone.utc)

    now = datetime.now(timezone.utc)

    if expiry_datetime <= now:
        return "Expired"

    time_diff = expiry_datetime - now
    days = time_diff.days
    hours, remainder = divmod(time_diff.seconds, 3600)
    minutes, _ = divmod(remainder, 60)

    parts = []
    if days > 0:
        parts.append(f"{days} day{'s' if days != 1 else ''}")
    if hours > 0:
        parts.append(f"{hours} hour{'s' if hours != 1 else ''}")
    if minutes > 0:
        parts.append(f"{minutes} minute{'s' if minutes != 1 else ''}")

    if not parts:
        return "Less than 1 minute"

    return ", ".join(parts)

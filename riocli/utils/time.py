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
from datetime import timedelta


def format_duration(d: timedelta) -> str:
    """Format a duration as '2 days, 3 hours, 15 minutes' or 'Less than 1 minute'."""
    hours, remainder = divmod(d.seconds, 3600)
    minutes = remainder // 60

    parts = [
        f"{n} {unit}{'s' if n != 1 else ''}"
        for n, unit in ((d.days, "day"), (hours, "hour"), (minutes, "minute"))
        if n > 0
    ]

    return ", ".join(parts) or "Less than 1 minute"

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

from enum import Enum


class Status(str, Enum):
    def __str__(self):
        return str(self.value).lower()

    RUNNING = "Running"
    AVAILABLE = "Available"


class ApplyResult(str, Enum):
    def __str__(self):
        return str(self.value)

    CREATED = "Created"
    UPDATED = "Updated"
    EXISTS = "Exists"

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


class NoProjectSelected(Exception):
    def __str__(self):
        return """No project is selected. Select a project first
        $ rio project select
        """


class NoOrganizationSelected(Exception):
    def __str__(self):
        return """No organization is selected. Select an organization first
        $ rio organization select
        """


class LoggedOut(Exception):
    def __str__(self):
        return """Not logged in. Please login first
        $ rio auth login
        """


class HwilLoggedOut(Exception):
    def __str__(self):
        return """Not logged in to HWIL. Please login first
        $ rio hwil login
        """


class DeviceNotFound(Exception):
    def __init__(self, message="device not found"):
        self.message = message
        super().__init__(self.message)


class ResourceNotFound(Exception):
    def __init__(self, message="resource not found"):
        self.message = message
        super().__init__(self.message)

class OperationNotSupported(Exception):
    def __init__(self, message="operation not supported"):
        self.message = message
        super().__init__(self.message)

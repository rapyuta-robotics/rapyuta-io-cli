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


class RetriesExhausted(Exception):
    def __init__(self, msg=None):
        Exception.__init__(self, msg)


class DeploymentNotRunning(Exception):
    def __init__(self, msg=None):
        Exception.__init__(self, msg)


class ImagePullError(Exception):
    def __init__(self, msg=None):
        Exception.__init__(self, msg)


class HttpAlreadyExistsError(Exception):
    def __init__(self, message="resource already exists"):
        self.message = message
        super().__init__(self.message)


class HttpNotFoundError(Exception):
    def __init__(self, message="resource not found"):
        self.message = message
        super().__init__(self.message)

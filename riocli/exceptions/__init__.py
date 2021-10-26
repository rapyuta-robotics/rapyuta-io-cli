# Copyright 2021 Rapyuta Robotics
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


class LoggedOut(Exception):

    def __str__(self):
        return """Not logged in. Please login first
        $ rio auth login 
        """

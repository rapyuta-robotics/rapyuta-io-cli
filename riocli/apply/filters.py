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

"""
Filters to use in the manifests.
"""

import os


def getenv(default: str, env_var: str) -> str:
    """
    Get the value of an environment variable.

    Usage:
        "foo" : {{ "bar" | getenv('FOO') }}

    Args:
        env_var: The environment variable to get the value of.
        default: The default value to return if the environment variable is not set.

    Returns:
        The value of the environment variable.
    """
    return os.getenv(env_var, default)


FILTERS = {
    'getenv': getenv,
}

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
from click import Context


def get_root_context(ctx: Context) -> Context:
    """
    get_root_context figures out the top-level Context from the given context by walking down the linked-list.

    https://click.palletsprojects.com/en/8.0.x/complex/#contexts
    """
    while True:
        if ctx.parent is None:
            return ctx

        ctx = ctx.parent

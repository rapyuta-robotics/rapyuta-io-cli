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
import click


@click.pass_context
def prompt_callback(ctx: click.Context) -> str:
    organization_name = ctx.obj.data["organization_name"]
    project_name = ctx.obj.data["project_name"]
    return "{}:{} > ".format(organization_name, project_name)

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
from riocli.config.config import Configuration


def new_client(config_inst: Configuration = None, with_project: bool = True):
    """
    new_client is a simple wrapper around the Configuration's new_client method. It can be called
    directly without initializing the Configuration first. It initializes the Configuration if not
    given already and then calls its new_client method.
    """
    if not config_inst:
        config_inst = Configuration()

    return config_inst.new_client(with_project=with_project)


def new_v2_client(config_inst: Configuration = None, with_project: bool = True):
    """
    new_v2_client is a simple wrapper around the Configuration's new_v2_client method. It can be called
    directly without initializing the Configuration first. It initializes the Configuration if not
    given already and then calls its new_client method.
    """
    if not config_inst:
        config_inst = Configuration()

    return config_inst.new_v2_client(with_project=with_project)


def new_hwil_client(config_inst: Configuration = None):
    if not config_inst:
        config_inst = Configuration()

    return config_inst.new_hwil_client()


def get_config_from_context(ctx: click.Context) -> Configuration:
    config_obj = ctx.obj

    if not isinstance(config_obj, Configuration):
        return Configuration()

    return config_obj

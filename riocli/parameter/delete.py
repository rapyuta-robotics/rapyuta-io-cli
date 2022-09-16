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

from email.policy import default
import json
from riocli.parameter.utils import compile_local_configurations
from xmlrpc.client import Boolean
import os
from shutil import copyfile
from tempfile import mkdtemp
import click
import yaml
from click_spinner import spinner

from riocli.config import new_client


@click.command('delete')
@click.option('--tree-names', type=click.STRING, multiple=True, default=None,
              help='Directory names to upload')
def delete_configurations(tree_names:str = None) -> None:
    """
    Upload a set of configurations to IO.

    Compile the IO configurations from the paths provided. Output to a temporary directory. Upload the directory.
    """
    try:
        client = new_client()
        pass
    except IOError as e:
        click.secho(str(e.__traceback__), fg='red')
        click.secho(str(e), fg='red')
        raise SystemExit(1)



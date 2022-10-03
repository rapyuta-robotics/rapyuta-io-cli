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

# -----------------------------------------------------------------------------
#
# Configurations
# Args
#    path,  tree_names,  delete_existing=True|False
# -----------------------------------------------------------------------------

from email.policy import default
import json
from typing import Tuple
from riocli.parameter.utils import compile_local_configurations
from xmlrpc.client import Boolean
import os
from shutil import copyfile
from tempfile import mkdtemp
import click
import yaml
from click_spinner import spinner

from riocli.config import new_client
from rapyuta_io.utils.error import APIError, InternalServerError


@click.command('download')
@click.option('--path', type=click.Path(dir_okay=True, file_okay=False, writable=True, exists=True, resolve_path=True), default=["."],
              help='Root Path for the Parameters to be download')
@click.option('--tree-names', type=click.STRING, multiple=True, default=None,
              help='Tree names to fetch')
@click.option('--delete-existing', is_flag=True, 
              help='Overwrite existing parameter tree')              
def download_configurations(path: click.Path, tree_names:Tuple = None,  delete_existing: Boolean = False) -> None:
    """
    Download the configurations
    """
    if path is None:
        path = mkdtemp() # Temporary directory to hold the configurations

    tree_names = list(tree_names)

    try:
        client = new_client()

        client.download_configurations(str(path), tree_names=tree_names, delete_existing_trees=delete_existing)
    
    except (APIError, InternalServerError) as e:
        click.secho( f"failed API request {str(e)}", fg='red')
        raise SystemExit(1)
    except (IOError, OSError) as e:
        click.secho( f"failed file/directory creation {str(e)}", fg='red')
        raise SystemExit(1)
    
    click.secho("Downloaded IO configurations to '{}'".format(path), fg='green')
    return path



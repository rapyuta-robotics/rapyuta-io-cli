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

from dictdiffer import diff
from riocli.parameter.download import download_configurations
from typing import Tuple
from riocli.parameter.utils import compile_local_configurations, parse_configurations
from xmlrpc.client import Boolean
import os
from shutil import copyfile
from tempfile import mkdtemp
import click
import yaml
from click_spinner import spinner

from riocli.config import new_client
from rapyuta_io.utils.error import APIError, InternalServerError


@click.command('diff')
@click.option('--path', type=click.Path(dir_okay=True, file_okay=False, writable=True, exists=True, resolve_path=True), default=["."],
              help='Root Path for the Parameters to be download')
@click.option('--tree-names', type=click.STRING, multiple=True, default=None,
              help='Tree names to fetch')
@click.option('--delete-existing', is_flag=True, 
              help='Overwrite existing parameter tree')              
def diff_configurations(path: click.Path, tree_names:Tuple = None,  delete_existing: Boolean = False) -> None:
    """
    Download the configurations
    """
    if path is None:
        click.secho( f"Base path missing. cannot diff without a local path to compare with remote tree", fg='red')
        raise SystemExit(1)
        
    try:
        client = new_client()
        with spinner():
            tmppath = mkdtemp() # Temporary directory to hold the configurations
            client.download_configurations(tmppath, tree_names=list(tree_names), delete_existing_trees=delete_existing)
            remote_configuration = parse_configurations(tmppath, tree_names=tree_names)
            local_configuration = parse_configurations(path, tree_names=tree_names)
            result = diff(local_configuration, remote_configuration)
            print("")
            for entry in result:
                action, key_path, value_mutation = entry
                color = 'yellow'
                action_sybom = "~"
                if action== 'add':
                    color = 'green'
                    action_sybom = "+"
                if action == "remove":
                    color = 'red'
                    action_sybom = "-"
                click.secho(f"{action_sybom}{action} {'.'.join(key_path)}  {value_mutation}", fg=color)
                


    except (APIError, InternalServerError) as e:
        click.secho( f"failed API request {str(e)}", fg='red')
        raise SystemExit(1)
    except (IOError, OSError) as e:
        click.secho( f"failed file/directory creation {str(e)}", fg='red')
        raise SystemExit(1)
    



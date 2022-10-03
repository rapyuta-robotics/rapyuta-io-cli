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


@click.command('upload')
@click.option('--paths', type=click.Path(), default=["."], multiple=True,
              help='Path for the Parameters Directory file')
@click.option('--tree-names', type=click.STRING, multiple=True, default=None,
              help='Directory names to upload')
@click.option('--delete-existing', is_flag=True, 
              help='Overwrite existing parameter tree')              
def upload_configurations(paths: click.Path, tree_names:str = None,  delete_existing: Boolean = False) -> None:
    """
    Upload a set of configurations to IO.

    Compile the IO configurations from the paths provided. Output to a temporary directory. Upload the directory.
    """
    try:
        client = new_client()
        uploaded_configuration = None
    
        with spinner():
            paths = list(paths)
            print(tree_names)
            
            configurations = compile_local_configurations(paths, tree_names=tree_names)
            d_tmp = mkdtemp() # Temporary directory to hold the merged configurations
            rev_paths = list(reversed(paths)) # path list in reverse order
            print(configurations.items())
            for rel_file_path, configuration in configurations.items():
                file_path = os.path.join(d_tmp, rel_file_path)
                file_name, file_extension = os.path.splitext(file_path) # f is a file name with extension
                print(".")
                try:
                    os.makedirs(os.path.dirname(file_path))
                except OSError:
                    pass

                if file_extension == '.yaml':
                    with open(file_path, 'w') as fp:
                        fp.write(yaml.safe_dump(configuration, indent=4))
                        click.secho("Wrote file '{}'".format(file_path))
                else:
                    for src_path in rev_paths:
                        src = os.path.abspath(os.path.join(src_path, rel_file_path))
                        try:
                            copyfile(src, file_path)
                        except IOError as e:
                        # file not found in this directory, try the next
                            click.secho(str(e), fg='red')
                            raise SystemExit(1)
                        else:
                            # copied the file, break out of the loop
                            click.secho("Copied file '{}' to '{}'".format(src, file_path))
                            break
            
            uploaded_configuration = client.upload_configurations(d_tmp, delete_existing_trees=delete_existing)
        
        if upload_configurations:
            click.secho('Parameter uploaded successfully!', fg='green')
            return upload_configurations
        else:
            click.secho(str(e), fg='red')
            raise SystemExit(1)

    except IOError as e:
        click.secho(str(e.__traceback__), fg='red')
        click.secho(str(e), fg='red')
        raise SystemExit(1)



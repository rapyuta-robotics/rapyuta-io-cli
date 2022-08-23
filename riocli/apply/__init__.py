# Copyright 2022 Rapyuta Robotics
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
import glob
import os

import click
from click_help_colors import HelpColorsCommand

from riocli.apply.parse import Applier
from riocli.apply.explain import explain
from riocli.build.model import Build
from riocli.deployment.model import Deployment
from riocli.device.model import Device
from riocli.disk.model import Disk
from riocli.network.model import Network
from riocli.package.model import Package
from riocli.project.model import Project
from riocli.secret.model import Secret
from riocli.static_route.model import StaticRoute
from riocli.utils import run_bash

KIND_TO_CLASS = {
    'Project': Project,
    'Secret': Secret,
    'Build': Build,
    'Device': Device,
    'Network': Network,
    'StaticRoute': StaticRoute,
    'Package': Package,
    'Disk': Disk,
    'Deployment': Deployment,
}

def parse_varidac_pathargs(pathItem):
    glob_files = []
    abs_path = os.path.abspath(pathItem)
    #make it absolte
    # does the path exist. 
    #     is it a dir?  scan recursively
    #     not a dir but has  special charaters in it?  [*?^!]
    #        assume its a valid glob, use it to glob recursively
    #      if all else fails
    #        consider it a file path directly. 
    if os.path.exists(abs_path):
        if os.path.isdir(abs_path):
            glob_files = glob.glob(abs_path + "/**/*", recursive=True)
        else:
            if "*" in abs_path or '?' in abs_path or '^' in abs_path or '.' in abs_path or '!' in abs_path:
                glob_files = glob.glob(abs_path, recursive=True)
            else:
                glob_files = [pathItem]
    return glob_files

@click.command(
    'apply',
    cls=HelpColorsCommand,
    help_headers_color='yellow',
    help_options_color='green',
)
@click.option('--dryrun', '-d', is_flag=True, default=False, help='dry run the yaml files without applying any change')
@click.option('--values', '-v')
@click.option('--secrets', '-s')
@click.argument('files', nargs=-1)
def apply(values: str, secrets: str, files: list[str], dryrun: bool = False, ) -> None:
    """
    Apply resource manifests
    """
    glob_files = []
    abs_values = values
    abs_secret = secrets

    for pathItem in files:
        path_glob = parse_varidac_pathargs(pathItem)
        glob_files.extend(path_glob)

    if values and values != "":
        abs_values = os.path.abspath(values)
        if abs_values in glob_files:
            glob_files.remove(abs_values)
    
    if secrets and secrets != "":
        abs_secrets = os.path.abspath(secrets)
        if abs_secrets in glob_files:
            glob_files.remove(abs_secrets)
        
    

    if len(glob_files) == 0:
        click.secho('no files specified', fg='red')
        exit(1)
    
    click.secho("----- Files Processed ----", fg="yellow")
    for file in glob_files:
        click.secho(file, fg="yellow")
    
    
    rc = Applier(glob_files, abs_values, abs_secret)
    rc.parse_dependencies()

    rc.apply(dryrun=dryrun)


@click.command(
    'delete',
    cls=HelpColorsCommand,
    help_headers_color='yellow',
    help_options_color='green',
)
@click.option('--values')
@click.argument('files')
@click.option('--dryrun', '-d', is_flag=True, default=False, help='dry run the yaml files without applying any change')
def delete(values: str, files: str, dryrun: bool = False) -> None:
    """
    Apply resource manifests
    """
    abs_path = os.path.abspath(files)
    glob_files = []
    if os.path.exists(abs_path):
        if os.path.isdir(abs_path):
            glob_files = glob.glob(abs_path + "/**/*", recursive=True)
        else:
            glob_files = [files]

    if len(glob_files) == 0:
        click.secho('no files specified', fg='red')
        exit(1)

    rc = Applier(glob_files, values)
    rc.parse_dependencies(check_missing=False)
    rc.delete(dryrun=dryrun)

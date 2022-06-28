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
from genericpath import isdir
import graphlib
import json
import typing
import os
import glob 

import click
from pyparsing import line
import yaml
from click_help_colors import HelpColorsCommand
from rapyuta_io import Client

from riocli.apply.parse import Applier
from riocli.build.model import Build
from riocli.deployment.model import Deployment
from riocli.device.model import Device
from riocli.disk.model import Disk
from riocli.network.model import Network
from riocli.package.model import Package
from riocli.project.model import Project
from riocli.secret.model import Secret
from riocli.static_route.model import StaticRoute

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

PKG_ROOT = os.path.dirname(os.path.abspath(__file__))
@click.command(
    'apply',
    hidden=True,
    cls=HelpColorsCommand,
    help_headers_color='yellow',
    help_options_color='green',
)
@click.argument('files')
def apply(files: str) -> None:
    """
    Apply resource manifests
    """
    abs_path = os.path.abspath(files)
    glob_files = []
    if(os.path.exists(abs_path)):
        if(os.path.isdir(abs_path)):
            glob_files = glob.glob( abs_path+"/**/*", recursive=True)
        else:
            glob_files = [files]
    
    if len(glob_files) == 0:
        click.secho('no files specified', fg='red')
        exit(1)

    rc = Applier(glob_files)
    rc.parse_dependencies()
    missing_resources = []        
    for key, item in rc.resolved_objects.items():
        if 'src' in item and item['src'] == 'missing':
            missing_resources.append(key)

    if(missing_resources):
        click.secho("missing resources found in yaml. " + \
                        "Plese ensure the following are either available in your yaml" + \
                        "or created on the server. {}".format(set(missing_resources))
                    , fg="red")
        exit(1)

    rc.apply()


def apply_manifest(client: Client, manifest: str) -> None:
    cls = get_model(manifest)
    ist = cls.from_dict(client, manifest)
    if manifest['kind'].lower() == "deployment":
        ist.apply(client)


def get_model(data: dict) -> typing.Any:
    kind = data.get('kind', None)
    if not kind:
        raise Exception('kind is missing')

    cls = KIND_TO_CLASS.get(kind, None)
    if not cls:
        raise Exception('invalid kind {}'.format(kind))

    return cls


#TODO very ghetto explain command
@click.command(
    'explain',
    hidden=True,
    cls=HelpColorsCommand,
    help_headers_color='yellow',
    help_options_color='green',
)
@click.argument('resource')
@click.argument('template_root', default= os.path.abspath(os.path.join(PKG_ROOT, '../../examples/manifests')))
def explain(resource: str, template_root: str) -> None:
    glob_files = glob.glob( template_root+"/**/*", recursive=True)
    for file in glob_files:
        if resource in os.path.basename(file):
            with open(file) as f:
                lines = ["---\n"]
                lines.extend(f.readlines())
                lines.extend(["---\n"])
                click.secho("".join(lines))
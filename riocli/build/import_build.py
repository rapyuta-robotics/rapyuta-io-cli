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
import os

import click
from click_help_colors import HelpColorsGroup
from click_spinner import spinner
from rapyuta_io import Build, StrategyType, DeviceArch, SimulationOptions

from riocli.config import new_client
from riocli.utils import run_bash
from riocli.utils.selector import show_selection


@click.group(
    'import',
    invoke_without_command=False,
    cls=HelpColorsGroup,
    help_headers_color='yellow',
    help_options_color='green',
)
def import_build():
    """
    Imports the build from the Shell context automagically
    """
    pass


@import_build.command('docker')
@click.option('--arch', help='Architecture for the Build',
              type=click.Choice(['amd64', 'arm32v7', 'arm64v8']), default='amd64')
@click.option('--ros/--no-ros', is_flag=True, help='Flag to enable ROS support', default=False)
@click.option('--sim/--no-sim', is_flag=True, help='Flag to enable Simulation support', default=False)
@click.option('--ros-distro', help='ROS Distribution to use for the Build',
              type=click.Choice(['kinetic', 'melodic'], case_sensitive=True), default='melodic')
@click.option('--wait', type=bool, help='Wait for the Build to complete', default=False)
def import_docker_build(arch: str, ros: bool, ros_distro: str, sim: bool, wait: bool) -> None:
    """
    Imports the build from the current repository based on Dockerfiles
    """
    try:
        build = _gather_information()
        build.buildInfo.architecture = arch
        simulation = SimulationOptions(sim)
        build.buildInfo.simulationOptions = simulation
        build.buildInfo.isROS = ros
        if ros:
            build.buildInfo.rosDistro = ros_distro
        client = new_client()
        with spinner():
            build = client.create_build(build)
            if wait:
                build.poll_build_till_ready()
        click.secho('Created build successfully!', fg='green')
    except Exception as e:
        click.secho(str(e), fg='red')
        exit(1)


def _gather_information() -> Build:
    directory = os.path.basename(run_bash('pwd'))
    repository = run_bash('git remote get-url --all origin')
    repository = _sanitize_repository(repository)
    branch = run_bash('git symbolic-ref HEAD').replace('refs/heads/', '')
    name = '{}___{}'.format(directory, branch.replace('/', '-'))

    dockerfiles = run_bash("find . -name *Dockerfile*").split("\n")
    if len(dockerfiles) == 0 or dockerfiles[0] == '':
        raise Exception('No Dockerfile found')
    elif len(dockerfiles) == 1:
        choice = dockerfiles[0]
    else:
        choice = show_selection(dockerfiles, header='Which Dockerfile do you want to use')

    return Build(buildName=name, strategyType=StrategyType.DOCKER, repository=repository, architecture=DeviceArch.AMD64,
                 dockerFilePath=choice)


def _sanitize_repository(repository: str) -> str:
    if 'github.com' in repository:
        return repository.replace("git@github.com:", "git://github.com/")

    # TODO: Add handling for more providers here!
    return repository

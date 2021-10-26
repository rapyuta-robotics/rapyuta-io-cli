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
import click
from click_spinner import spinner
from rapyuta_io import Build, SimulationOptions

from riocli.config import new_client


@click.command('create')
@click.option('--strategy', type=click.Choice(['Source', 'Docker']), default='Docker',
              help='Strategy for building the Source')
@click.option('--branch', default='', help='Git Repository branch')
@click.option('--context', help='Context directory relative to the Git Repository root', default='')
@click.option('--arch', help='Architecture for the Build',
              type=click.Choice(['amd64', 'arm32v7', 'arm64v8']), default='amd64')
@click.option('--ros/--no-ros', is_flag=True, help='Flag to enable ROS support', default=False)
@click.option('--sim/--no-sim', is_flag=True, help='Flag to enable Simulation support', default=False)
@click.option('--ros-distro', help='ROS Distribution to use for the Build',
              type=click.Choice(['kinetic', 'melodic', 'noetic'], case_sensitive=True), default='melodic')
@click.option('--dockerfile', help='Path of Dockerfile, relative to the Context directory', default=None)
@click.option('--secret', help='Secret for the private git repository', default='')
@click.option('--docker-push-secret', help='Docker secret for pushing the image to an external registry.',
              default='')
@click.option('--docker-push-repository', help='External docker repository where Build will push the image.',
              default='')
@click.option('--trigger-name', type=str, help='Trigger name of the build', default='')
@click.option('--wait', type=bool, help='Wait for the Build to complete', default=False)
@click.argument('build-name', type=str)
@click.argument('repository', type=str)
def create_build(build_name: str, repository: str, strategy: str, branch: str, context: str, arch: str, ros: bool,
                 sim: bool, secret: str, ros_distro: str, trigger_name: str, dockerfile: str, docker_push_secret: str,
                 docker_push_repository: str, wait: bool) -> None:
    """
    Create a new build on the Platform
    """
    try:
        simulation = SimulationOptions(sim)
        build = Build(buildName=build_name, strategyType=strategy, repository=repository, architecture=arch, isRos=ros,
                      contextDir=context, simulationOptions=simulation, branch=branch, rosDistro=ros_distro,
                      secret=secret, triggerName=trigger_name, dockerPushSecret=docker_push_secret,
                      dockerPushRepository=docker_push_repository)
        if strategy == 'Dockerfile':
            build.buildInfo.dockerFilePath = dockerfile
        client = new_client()
        with spinner():
            build = client.create_build(build)
            if wait:
                build.poll_build_till_ready()
        click.secho('Created build successfully!', fg='green')
    except Exception as e:
        click.secho(str(e), fg='red')
        exit(1)

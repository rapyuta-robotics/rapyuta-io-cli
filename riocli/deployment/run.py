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


@click.command('run', hidden=True)
@click.argument('docker-image', type=str)
def run_deployment(docker_image: str) -> None:
    # TODO(ankit): Implement `kubectl run` like command to instantly create a Deployment.
    # Possibly implement --interactive --tty to SSH into the session
    pass

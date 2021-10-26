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

from rapyuta_io import Build
from riocli.build.util import name_to_guid
from riocli.config import new_client
from riocli.utils import inspect_with_format


@click.command('inspect')
@click.option('--format', '-f', 'format_type', default='yaml',
              type=click.Choice(['json', 'yaml'], case_sensitive=False))
@click.argument('build-name', required=True)
@name_to_guid
def inspect_build(format_type: str, build_guid: str, build_name: str) -> None:
    """
    Inspect the build resource
    """
    try:
        client = new_client()
        build = client.get_build(build_guid, include_build_requests=True)
        data = make_build_inspectable(build)
        inspect_with_format(data, format_type)
    except Exception as e:
        click.secho(str(e), fg='red')
        exit(1)


def make_build_inspectable(build: Build) -> dict:
    build_requests = make_build_requests_inspectable(build)
    build_info = make_build_info_inspectable(build)
    return {
        'created_at': build.CreatedAt,
        'updated_at': build.UpdatedAt,
        'deleted_at': build.DeletedAt,
        'guid': build.guid,
        'build_generation': build.buildGeneration,
        'build_name': build.buildName,
        'build_info': build_info,
        'status': build.status,
        'owner_project': build.ownerProject,
        'creator': build.creator,
        'docker_pull_info': build.dockerPullInfo,
        'build_requests': build_requests,
        'secret': build.secret,
        'docker_pull_secret': build.dockerPullSecret,
        'docker_push_secret': build.dockerPushSecret,
        'docker_push_repository': build.dockerPushRepository,
    }


def make_build_info_inspectable(build: Build) -> dict:
    build_info = build.buildInfo
    return {
        'repository': build_info.repository,
        'strategy_type': build_info.strategyType,
        'architecture': build_info.architecture,
        'is_ros': build_info.isRos,
        'ros_distro': build_info.rosDistro,
        'simulation_options': {
            'simulation': build_info.simulationOptions.simulation
        },
        'build_options': build_info.buildOptions,
        'branch': build_info.branch,
        'docker_file_path': build_info.dockerFilePath,
        'context_dir': build_info.contextDir,
    }


def make_build_requests_inspectable(build: Build) -> list:
    build_request_data = []
    for build_request in build.buildRequests:
        build_request_data.append({
            'created_at': build_request['CreatedAt'],
            'updated_at': build_request['UpdatedAt'],
            'deleted_at': build_request['DeletedAt'],
            'request_id': build_request['requestId'],
            'is_complete': build_request['isComplete'],
            'error_string': build_request['errorString'],
            'owner_project': build_request['ownerProject'],
            'creator': build_request['creator'],
            'trigger_name': build_request['triggerName'],
            'build_generation': build_request['buildGeneration'],
            'git_metadata': make_git_metadata_inspectable(build_request['gitMetadata']),
            'executable_image_info': make_executable_image_info_inspectable(build_request['executableImageInfo']),
        })
    return build_request_data


def make_git_metadata_inspectable(git_metadata: dict) -> dict:
    guid = list(git_metadata.keys())[0]
    guid_details = git_metadata[guid]
    guid_value = {
        'author': {
            'email': guid_details['author']['email'],
            'name': guid_details['author']['name'],
        },
        'branch': guid_details['branch'],
        'commit': guid_details['commit'],
        'committer': {
            'email': guid_details['committer']['email'],
            'name': guid_details['committer']['name'],
        },
        'message': guid_details['message'],
        'repository_url': guid_details['repositoryUrl']
    }
    return {
        guid: guid_value
    }


def make_executable_image_info_inspectable(exec_img_info: dict) -> dict:
    image_info_list = []
    for img_info in exec_img_info['imageInfo']:
        image_info_list.append({
            'artifact_id': img_info['artifactID'],
            'image_name': img_info['imageName'],
        })
    return {
        'image_info': image_info_list
    }

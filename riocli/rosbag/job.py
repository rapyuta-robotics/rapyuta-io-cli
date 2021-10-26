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
import typing

import click
from click_help_colors import HelpColorsGroup
from click_spinner import spinner
from rapyuta_io.clients.rosbag import ROSBagOptions, ROSBagJob, ROSBagCompression, ROSBagJobStatus

from riocli.config import new_client
from riocli.deployment.util import  name_to_guid as deployment_name_to_guid


@click.group(
    'job',
    invoke_without_command=False,
    cls=HelpColorsGroup,
    help_headers_color='yellow',
    help_options_color='green',
)
def rosbag_job() -> None:
    """
    Record the topics for any ROS component
    """
    pass


@rosbag_job.command('create')
@click.option('--name', help='Name of the rosbag job')
@click.option('--deployment-id', help='Deployment id ')
@click.option('--component-instance-id', help='Component instance id ')
@click.option('--all-topics/--not-all-topics', help='Record all topics?', default=False)
@click.option('--topics', help='List of topics whose content is to be recorded ', multiple=True)
@click.option('--topic-include-regex', help='Include topics matching the given regular expression ', multiple=True)
@click.option('--topic-exclude-regex', help='Exclude topics matching the given regular expression ')
@click.option('--max-message-count', help='Only record NUM messages on each topic ', default=0)
@click.option('--node', help='Record all topics subscribed to by a specific node ')
@click.option('--compression', help='Compression ?', type=click.Choice(['LZ4', 'BZ2'], case_sensitive=True),
              default=None)
@click.option('--max-splits', help='Split bag at most MAX_SPLITS times ', default=0)
@click.option('--max-split-size', help='Record a bag of maximum size', default=0)
@click.option('--chunk-size', help='Record to chunks of size KB before writing to disk', default=0)
def job_create(name: str, deployment_id: str, component_instance_id: str, all_topics: bool, topics: typing.List[str],
               topic_include_regex: str, topic_exclude_regex: str, max_message_count: int, node: str,
               compression: str, max_splits: int, max_split_size: int, chunk_size: int) -> None:
    """
    Create a ROSbag job
    """
    if compression:
        compression = ROSBagCompression(compression)
    rosbag_options = ROSBagOptions(all_topics=all_topics, topics=list(topics),
                                   topic_include_regex=list(topic_include_regex),
                                   topic_exclude_regex=topic_exclude_regex, max_message_count=max_message_count,
                                   node=node, max_splits=max_splits, max_split_size=max_split_size,
                                   chunk_size=chunk_size, compression=compression)
    rosbag_job = ROSBagJob(name=name, deployment_id=deployment_id, component_instance_id=component_instance_id,
                           rosbag_options=rosbag_options)
    try:
        client = new_client()
        with spinner():
            client.create_rosbag_job(rosbag_job)
        click.secho('Rosbag Job created successfully', fg='green')
    except Exception as e:
        click.secho(str(e), fg='red')
        exit(1)


@rosbag_job.command('stop')
@click.argument('deployment-name')
@click.option('--component-instance-ids', help='Filter by component instance ids ', multiple=True)
@click.option('--guids', help='Filter by job guids', multiple=True)
@deployment_name_to_guid
def job_stop(deployment_guid: str, deployment_name: str, component_instance_ids: typing.List[str],
             guids: typing.List[str]) -> None:
    """
    Stop ROSbag jobs
    """
    try:
        client = new_client()
        with spinner():
            client.stop_rosbag_jobs(deployment_id=deployment_guid, component_instance_ids=list(component_instance_ids),
                                    guids=list(guids))
        click.secho('Rosbag Job stopped successfully', fg='green')
    except Exception as e:
        click.secho(str(e), fg='red')
        exit(1)


@rosbag_job.command('list')
@click.argument('deployment-name')
@click.option('--component-instance-ids', help='Filter by component instance ids ', multiple=True)
@click.option('--guids', help='Filter by job guids ', multiple=True)
@click.option('--statuses', help='Filter by rosbag job statuses ', multiple=True, default=['Starting', 'Running'],
              type=click.Choice(['Starting', 'Running', 'Error', 'Stopping', 'Stopped'], case_sensitive=True))
@deployment_name_to_guid
def job_list(deployment_guid: str, deployment_name: str,
             component_instance_ids: typing.List[str], guids: typing.List[str], statuses: typing.List[str]) -> None:
    """
    List the Rosbag jobs for the given Deployment
    """
    status_list = []
    try:
        client = new_client()
        for status in list(statuses):
            status_list.append(ROSBagJobStatus(status))
        rosbag_jobs = client.list_rosbag_jobs(deployment_id=deployment_guid,
                                              component_instance_ids=list(component_instance_ids), guids=list(guids),
                                              statuses=status_list)
        _display_rosbag_job_list(rosbag_jobs, show_header=True)
    except Exception as e:
        click.secho(str(e), fg='red')
        exit(1)


def _display_rosbag_job_list(jobs: typing.List[ROSBagJob], show_header: bool = True) -> None:
    if show_header:
        header = '{:<35} {:<25} {:<15} {:20} {:40}'.format(
            'GUID',
            'Name',
            'Status',
            'Component Type',
            'Device ID',
        )
        click.secho(header, fg='yellow')
    for job in jobs:
        click.secho('{:<35} {:<25} {:<15} {:20} {:40}'.format(
            job.guid,
            job.name,
            job.status,
            job.component_type.name,
            'None' if job.device_id is None else job.device_id,
        ))







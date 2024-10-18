# Copyright 2024 Rapyuta Robotics
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
import pyrfc3339
from click_help_colors import HelpColorsGroup
from click_spinner import spinner
from rapyuta_io.clients.rosbag import (
    ROSBagOptions,
    ROSBagJob,
    ROSBagCompression,
    ROSBagJobStatus,
    ROSBagUploadTypes,
    ROSBagOnDemandUploadOptions,
    ROSBagTimeRange,
)

from riocli.config import new_client

# from riocli.deployment.util import name_to_guid as deployment_name_to_guid
from riocli.rosbag.util import ROSBagJobNotFound
from riocli.utils import inspect_with_format
from riocli.utils import tabulate_data


@click.group(
    "job",
    invoke_without_command=False,
    cls=HelpColorsGroup,
    help_headers_color="yellow",
    help_options_color="green",
)
def rosbag_job() -> None:
    """
    Record the topics for any ROS component
    """
    pass


@rosbag_job.command("create")
@click.option("--name", help="Name of the rosbag job")
@click.option("--deployment-id", help="Deployment id ")
@click.option("--component-instance-id", help="Component instance id ")
@click.option("--all-topics/--not-all-topics", help="Record all topics?", default=False)
@click.option(
    "--topics", help="List of topics whose content is to be recorded ", multiple=True
)
@click.option(
    "--topic-include-regex",
    help="Include topics matching the given regular expression ",
    multiple=True,
)
@click.option(
    "--topic-exclude-regex",
    help="Exclude topics matching the given regular expression ",
)
@click.option(
    "--max-message-count", help="Only record NUM messages on each topic ", default=0
)
@click.option("--node", help="Record all topics subscribed to by a specific node ")
@click.option(
    "--compression",
    help="Compression ?",
    type=click.Choice(["LZ4", "BZ2"], case_sensitive=True),
    default=None,
)
@click.option("--max-splits", help="Split bag at most MAX_SPLITS times ", default=0)
@click.option("--max-split-size", help="Record a bag of maximum size", default=0)
@click.option(
    "--chunk-size", help="Record to chunks of size KB before writing to disk", default=0
)
def job_create(
    name: str,
    deployment_id: str,
    component_instance_id: str,
    all_topics: bool,
    topics: typing.List[str],
    topic_include_regex: str,
    topic_exclude_regex: str,
    max_message_count: int,
    node: str,
    compression: str,
    max_splits: int,
    max_split_size: int,
    chunk_size: int,
) -> None:
    """
    Create a ROSbag job
    """
    if compression:
        compression = ROSBagCompression(compression)
    rosbag_options = ROSBagOptions(
        all_topics=all_topics,
        topics=list(topics),
        topic_include_regex=list(topic_include_regex),
        topic_exclude_regex=topic_exclude_regex,
        max_message_count=max_message_count,
        node=node,
        max_splits=max_splits,
        max_split_size=max_split_size,
        chunk_size=chunk_size,
        compression=compression,
    )
    rosbag_job = ROSBagJob(
        name=name,
        deployment_id=deployment_id,
        component_instance_id=component_instance_id,
        rosbag_options=rosbag_options,
    )
    try:
        client = new_client()
        with spinner():
            client.create_rosbag_job(rosbag_job)
        click.secho("Rosbag Job created successfully", fg="green")
    except Exception as e:
        click.secho(str(e), fg="red")
        raise SystemExit(1)


@rosbag_job.command("inspect")
@click.option(
    "--format",
    "-f",
    "format_type",
    type=click.Choice(["json", "yaml"], case_sensitive=False),
    default="yaml",
)
@click.argument("job-guid", type=str)
def job_inspect(job_guid: str, format_type: str) -> None:
    """
    Inspect a ROSbag job
    """
    try:
        client = new_client()
        job = client.get_rosbag_job(job_guid)
        job = make_rosbag_job_inspectable(job)
        inspect_with_format(job, format_type)
    except Exception as e:
        click.secho(str(e), fg="red")
        raise SystemExit(1)


@rosbag_job.command("stop")
@click.argument("deployment-name")
@click.option(
    "--component-instance-ids", help="Filter by component instance ids ", multiple=True
)
@click.option("--guids", help="Filter by job guids", multiple=True)
# @deployment_name_to_guid
def job_stop(
    deployment_guid: str,
    deployment_name: str,
    component_instance_ids: typing.List[str],
    guids: typing.List[str],
) -> None:
    """
    Stop ROSbag jobs
    """
    try:
        client = new_client()
        with spinner():
            client.stop_rosbag_jobs(
                deployment_id=deployment_guid,
                component_instance_ids=list(component_instance_ids),
                guids=list(guids),
            )
        click.secho("Rosbag Job stopped successfully", fg="green")
    except Exception as e:
        click.secho(str(e), fg="red")
        raise SystemExit(1)


@rosbag_job.command("list")
@click.argument("deployment-name")
@click.option(
    "--component-instance-ids", help="Filter by component instance ids ", multiple=True
)
@click.option("--guids", help="Filter by job guids ", multiple=True)
@click.option(
    "--statuses",
    help="Filter by rosbag job statuses ",
    multiple=True,
    default=["Starting", "Running", "Stopped", "Stopping", "Error"],
    type=click.Choice(
        ["Starting", "Running", "Error", "Stopping", "Stopped"], case_sensitive=True
    ),
)
# @deployment_name_to_guid
def job_list(
    deployment_guid: str,
    deployment_name: str,
    component_instance_ids: typing.List[str],
    guids: typing.List[str],
    statuses: typing.List[str],
) -> None:
    """
    List the Rosbag jobs for the given Deployment
    """
    status_list = []
    try:
        client = new_client()
        for status in list(statuses):
            status_list.append(ROSBagJobStatus(status))
        rosbag_jobs = client.list_rosbag_jobs(
            deployment_id=deployment_guid,
            component_instance_ids=list(component_instance_ids),
            guids=list(guids),
            statuses=status_list,
        )
        _display_rosbag_job_list(rosbag_jobs, show_header=True)
    except Exception as e:
        click.secho(str(e), fg="red")
        raise SystemExit(1)


@rosbag_job.command("trigger")
@click.argument("deployment-name")
@click.argument("job-guid")
@click.option(
    "--upload-from",
    help="Rosbags recorded after or at this time are uploaded. Specify time in RFC 3339 "
    "format (1985-04-12T23:20:50.52Z)",
    required=True,
)
@click.option(
    "--upload-to",
    help="Rosbags recorded before or at this time are uploaded. Specify time in RFC 3339 "
    "format (1985-04-12T23:20:50.52Z)",
    required=True,
)
# @deployment_name_to_guid
def job_trigger_upload(
    deployment_guid: str,
    deployment_name: str,
    job_guid: str,
    upload_from: str,
    upload_to: str,
) -> None:
    """
    Trigger Rosbag Upload

    Here are some examples of RFC3339 date/time format that can be given to '--upload-from' &
    '--upload-to' options

    1. 2022-10-21T23:20:50.52Z

       This represents 20 minutes and 50.52 seconds after the 23rd hour of
       October 21st, 2022 in UTC.

    2. 2022-10-21T23:20:50.52+05:30

       This represents 20 minutes and 50.52 seconds after the 23rd hour of
       October 21st, 2022 with an offset of +05:30 from UTC (Indian Standard Time).

       Note that this is equivalent to 2022-10-21T17:50:50.52Z in UTC.

    3. 2022-10-21T23:20:50.52+09:00

       This represents 20 minutes and 50.52 seconds after the 23rd hour of
       October 21st, 2022 with an offset of +09:00 from UTC (Japan Standard Time).

       Note that this is equivalent to 2022-10-21T14:20:50.52Z in UTC.


    4. 2022-10-21T23:20:50.52-07:00

       This represents 20 minutes and 50.52 seconds after the 23rd hour of
       October 21st, 2022 with an offset of -07:00 from UTC (Pacific Daylight Time).

       Note that this is equivalent to 2022-10-22T06:20:50.52Z in UTC.

    Ref: https://www.rfc-editor.org/rfc/rfc3339#section-5.8
    """
    try:
        client = new_client()
        with spinner():
            rosbag_jobs = client.list_rosbag_jobs(
                deployment_id=deployment_guid, guids=[job_guid]
            )
            if len(rosbag_jobs) == 0:
                raise ROSBagJobNotFound()

            if (
                rosbag_jobs[0].upload_options
                and rosbag_jobs[0].upload_options.upload_type
                != ROSBagUploadTypes.ON_DEMAND
            ):
                click.secho(
                    "Warning: this job does not have OnDemand upload type so triggering will not have any effect but,"
                    " it will take into effect when job's upload type is changed to OnDemand",
                    fg="yellow",
                )

            time_range = ROSBagTimeRange(
                from_time=int(pyrfc3339.parse(upload_from).timestamp()),
                to_time=int(pyrfc3339.parse(upload_to).timestamp()),
            )
            on_demand_options = ROSBagOnDemandUploadOptions(time_range)

            rosbag_jobs[0].patch(on_demand_options=on_demand_options)

        click.secho("Rosbag upload triggered successfully", fg="green")
    except Exception as e:
        click.secho(str(e), fg="red")
        raise SystemExit(1)


@rosbag_job.command("update")
@click.argument("deployment-name")
@click.argument("job-guid")
@click.option(
    "--upload-mode",
    help="Change upload mode",
    type=click.Choice([t for t in ROSBagUploadTypes]),
    required=True,
)
# @deployment_name_to_guid
def update_job(
    deployment_guid: str, deployment_name: str, job_guid: str, upload_mode: str
) -> None:
    """
    Update the Rosbag Job
    """
    try:
        client = new_client()
        with spinner():
            rosbag_jobs = client.list_rosbag_jobs(
                deployment_id=deployment_guid, guids=[job_guid]
            )
            if len(rosbag_jobs) == 0:
                raise ROSBagJobNotFound()

            rosbag_jobs[0].patch(upload_type=upload_mode)

        click.secho("Rosbag Job updated successfully", fg="green")
    except Exception as e:
        click.secho(str(e), fg="red")
        raise SystemExit(1)


def _display_rosbag_job_list(
    jobs: typing.List[ROSBagJob], show_header: bool = True
) -> None:
    headers = []
    if show_header:
        headers = ("GUID", "Name", "Status", "Component Type", "Device ID")

    data = []
    for job in jobs:
        data.append(
            [
                job.guid,
                job.name,
                job.status,
                job.component_type.name,
                "None" if job.device_id is None else job.device_id,
            ]
        )

    tabulate_data(data, headers)


def make_rosbag_job_inspectable(job: ROSBagJob) -> typing.Dict:
    return {
        "name": job.name,
        "status": job.status,
        "project": job.project,
        "device_id": job.device_id,
        "package_id": job.package_id,
        "component_id": job.component_id,
        "deployment_id": job.deployment_id,
        "component_type": job.component_type,
        "rosbag_options": job.rosbag_options,
        "upload_options": job.upload_options,
        "override_options": job.override_options,
        "component_instance_id": job.component_instance_id,
    }

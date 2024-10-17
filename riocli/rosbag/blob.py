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
from click_help_colors import HelpColorsGroup
from click_spinner import spinner
from rapyuta_io.clients.rosbag import ROSBagBlobStatus, ROSBagBlob
from rapyuta_io.utils import ResourceNotFoundError

from riocli.config import new_client
from riocli.utils import tabulate_data


@click.group(
    "blob",
    invoke_without_command=False,
    cls=HelpColorsGroup,
    help_headers_color="yellow",
    help_options_color="green",
)
def rosbag_blob() -> None:
    """
    ROSBag file actions
    """
    pass


@rosbag_blob.command("delete")
@click.argument("guid")
def blob_delete(guid: str) -> None:
    """
    Delete a ROSbag blob
    """
    try:
        client = new_client()
        with spinner():
            client.delete_rosbag_blob(guid)
        click.secho("Rosbag Blob deleted successfully", fg="green")
    except ResourceNotFoundError as e:
        click.secho(str(e), fg="red")
        raise SystemExit(1)


@rosbag_blob.command("download")
@click.argument("guid")
@click.option("--filename", help="Name of the file")
@click.option("--download-dir", help="Directory to download the file into")
def blob_download(guid: str, filename: str, download_dir: str) -> None:
    """
    Download a ROSbag blob
    """
    try:
        client = new_client()
        with spinner():
            client.download_rosbag_blob(
                guid=guid, filename=filename, download_dir=download_dir
            )
        click.secho("Rosbag Blob downloaded successfully", fg="green")
    except ResourceNotFoundError as e:
        click.secho(str(e), fg="red")
        raise SystemExit(1)


@rosbag_blob.command("list")
@click.option("--guids", help="Filter by blob guids ", multiple=True)
@click.option("--deployment-ids", help="Filter by deployment ids ", multiple=True)
@click.option(
    "--component-instance-ids", help="Filter by component instance ids ", multiple=True
)
@click.option("--job-ids", help="Filter by job ids ", multiple=True)
@click.option("--device-ids", help="Filter by device ids ", multiple=True)
@click.option(
    "--statuses",
    help="Filter by rosbag blob statuses ",
    type=click.Choice(
        ["Starting", "Uploading", "Uploaded", "Error"], case_sensitive=True
    ),
    multiple=True,
    default=["Uploaded", "Uploading", "Starting"],
)
def blob_list(
    guids: typing.List[str],
    deployment_ids: typing.List[str],
    component_instance_ids: typing.List[str],
    job_ids: typing.List[str],
    device_ids: typing.List[str],
    statuses: typing.List[str],
) -> None:
    """
    List the Rosbag blobs in the selected project
    """
    status_list = []
    for status in list(statuses):
        status_list.append(ROSBagBlobStatus(status))
    try:
        client = new_client()
        rosbag_blobs = client.list_rosbag_blobs(
            guids=list(guids),
            deployment_ids=list(deployment_ids),
            component_instance_ids=list(component_instance_ids),
            job_ids=list(job_ids),
            device_ids=list(device_ids),
            statuses=status_list,
        )
        _display_rosbag_blob_list(rosbag_blobs, show_header=True)
    except Exception as e:
        click.secho(str(e), fg="red")
        raise SystemExit(1)


def _display_rosbag_blob_list(
    blobs: typing.List[ROSBagBlob], show_header: bool = True
) -> None:
    headers = []
    if show_header:
        headers = (
            "GUID",
            "Job ID",
            "Blob Ref ID",
            "Status",
            "Component Type",
            "Device ID",
        )

    data = []
    for blob in blobs:
        data.append(
            [
                blob.guid,
                blob.job_id,
                blob.blob_ref_id,
                blob.status,
                blob.component_type.name,
                "None" if blob.device_id is None else blob.device_id,
            ]
        )

    tabulate_data(data, headers)

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
from datetime import datetime, timedelta

import click
from click_help_colors import HelpColorsGroup
from click_spinner import spinner
from rapyuta_io.clients import LogsUploadRequest, LogUploads, SharedURL

from riocli.config import new_client
from riocli.device.util import name_to_guid, name_to_request_id


@click.group(
    'uploads',
    invoke_without_command=False,
    cls=HelpColorsGroup,
    help_headers_color='yellow',
    help_options_color='green',
)
def device_uploads() -> None:
    """
    Uploaded files from the Device
    """
    pass


@device_uploads.command('list')
@click.argument('device-name', type=str)
@name_to_guid
def list_uploads(device_name: str, device_guid: str) -> None:
    try:
        client = new_client()
        device = client.get_device(device_id=device_guid)
        uploads = device.list_uploaded_files_for_device()
        _display_upload_list(uploads=uploads, show_header=True)
    except Exception as e:
        click.secho(str(e), fg='red')
        exit(1)


@device_uploads.command('create')
@click.option('--max-upload-rate', type=int, default=1*1024*1024,
              help='Network bandwidth limit to be used for upload (Bytes per second)')
@click.option('--override', is_flag=True, default=False, help='Flag to override destination file')
@click.option('--purge', is_flag=True, default=False, help='Flag to enable purging the file, after it is uploaded')
@click.argument('device-name', type=str)
@click.argument('upload-name', type=str)
@click.argument('file-path', type=str)
@name_to_guid
def create_upload(
        device_name: str,
        device_guid: str,
        upload_name: str,
        file_path: str,
        max_upload_rate: int,
        override: bool,
        purge: bool,
) -> None:
    try:
        client = new_client()
        with spinner():
            device = client.get_device(device_id=device_guid)
            upload_request = LogsUploadRequest(device_path=file_path, file_name=upload_name,
                                               max_upload_rate=max_upload_rate, override=override,
                                               purge_after=purge)
            device.upload_log_file(upload_request)
        click.secho('File upload requested successfully!', fg='green')
    except Exception as e:
        click.secho(str(e), fg='red')
        exit(1)


@device_uploads.command('status')
@click.argument('device-name', type=str)
@click.argument('file-name', type=str)
@name_to_guid
@name_to_request_id
def upload_status(device_name: str, device_guid: str, file_name: str, request_id: str):
    try:
        client = new_client()
        device = client.get_device(device_id=device_guid)
        status = device.get_log_upload_status(request_uuid=request_id)
        click.secho(status.status)
    except Exception as e:
        click.secho(str(e), fg='red')
        exit(1)


@device_uploads.command('delete')
@click.argument('device-name', type=str)
@click.argument('file-name', type=str)
@name_to_guid
@name_to_request_id
def delete_upload(device_name: str, device_guid: str, file_name: str, request_id: str):
    try:
        client = new_client()
        with spinner():
            device = client.get_device(device_id=device_guid)
            device.delete_uploaded_log_file(request_uuid=request_id)
        click.secho('Deleted upload successfully!', fg='green')
    except Exception as e:
        click.secho(str(e), fg='red')
        exit(1)


@device_uploads.command('download')
@click.argument('device-name', type=str)
@click.argument('file-name', type=str)
@name_to_guid
@name_to_request_id
def download_log(device_name: str, device_guid: str, file_name: str, request_id: str):
    try:
        client = new_client()
        with spinner():
            device = client.get_device(device_id=device_guid)
            url = device.download_log_file(request_uuid=request_id)
        click.secho(url)
    except Exception as e:
        click.secho(str(e), fg='red')
        exit(1)


@device_uploads.command('cancel')
@click.argument('device-name', type=str)
@click.argument('file-name', type=str)
@name_to_guid
@name_to_request_id
def cancel_upload(device_name: str, device_guid: str, file_name: str, request_id: str):
    try:
        client = new_client()
        with spinner():
            device = client.get_device(device_id=device_guid)
            device.cancel_log_file_upload(request_uuid=request_id)
        click.secho('Cancelled upload successfully!', fg='green')
    except Exception as e:
        click.secho(str(e), fg='red')
        exit(1)


@device_uploads.command('share')
@click.option('--expiry', help='Flag to set the expiry date for the Shared URL [default: 7 days]', default=7)
@click.argument('device-name', type=str)
@click.argument('file-name', type=str)
@name_to_guid
@name_to_request_id
def shared_url(device_name: str, device_guid: str, file_name: str, request_id: str, expiry: int) -> None:
    try:
        client = new_client()
        with spinner():
            device = client.get_device(device_id=device_guid)
            expiry_time = datetime.now() + timedelta(days=7)
            public_url = device.create_shared_url(SharedURL(request_id, expiry_time=expiry_time))
        click.secho(public_url.url, fg='green')
    except Exception as e:
        click.secho(str(e), fg='red')
        exit(1)


def _display_upload_list(uploads: LogUploads, show_header: bool = True) -> None:
    if show_header:
        click.secho('{:34} {:20} {:16} {:<12} {:64}'.
                    format('Upload ID', 'Name', 'Status', 'Total Size', 'Error'),
                    fg='yellow')

    for upload in uploads:
        click.secho('{:34} {:20} {:16} {:<12} {:64}'.format(upload.request_uuid, upload.filename, upload.status,
                                                           upload.total_size, upload.error_message))


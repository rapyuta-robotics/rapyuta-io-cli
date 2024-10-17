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
from datetime import datetime, timedelta

import click
from click_help_colors import HelpColorsCommand, HelpColorsGroup
from rapyuta_io.clients import LogUploads, LogsUploadRequest, SharedURL

from riocli.config import new_client
from riocli.constants import Colors, Symbols
from riocli.device.util import name_to_guid, name_to_request_id
from riocli.utils import tabulate_data
from riocli.utils.spinner import with_spinner


@click.group(
    "uploads",
    invoke_without_command=False,
    cls=HelpColorsGroup,
    help_headers_color=Colors.YELLOW,
    help_options_color=Colors.RED,
)
def device_uploads() -> None:
    """Manage file uploads from a device.

    Provides a convenient way to upload from a device to the cloud
    and later download, share and perform operations on the uploaded files.
    """
    pass


@device_uploads.command(
    "list",
    cls=HelpColorsCommand,
    help_headers_color=Colors.YELLOW,
    help_options_color=Colors.GREEN,
)
@click.argument("device-name", type=str)
@name_to_guid
def list_uploads(device_name: str, device_guid: str) -> None:
    """List all files uploaded from a device.

    Lists all the files uploaded from a device along
    with their size and status.
    """
    try:
        client = new_client()
        device = client.get_device(device_id=device_guid)
        uploads = device.list_uploaded_files_for_device()
        _display_upload_list(uploads=uploads, show_header=True)
    except Exception as e:
        click.secho(str(e), fg=Colors.RED)
        raise SystemExit(1) from e


@device_uploads.command(
    "create",
    cls=HelpColorsCommand,
    help_headers_color=Colors.YELLOW,
    help_options_color=Colors.GREEN,
)
@click.option(
    "--max-upload-rate",
    type=int,
    default=1 * 1024 * 1024,
    help="Network bandwidth limit to be used for upload (Bytes per second)",
)
@click.option(
    "--override", is_flag=True, default=False, help="Flag to override destination file"
)
@click.option(
    "--purge",
    is_flag=True,
    default=False,
    help="Flag to enable purging the file, after it is uploaded",
)
@click.argument("device-name", type=str)
@click.argument("upload-name", type=str)
@click.argument("file-path", type=str)
@name_to_guid
@with_spinner(text="Uploading...")
def create_upload(
    device_name: str,
    device_guid: str,
    upload_name: str,
    file_path: str,
    max_upload_rate: int,
    override: bool,
    purge: bool,
    spinner=None,
) -> None:
    """Upload a file from a device to the cloud.

    You can set the maximum upload rate for the upload operation
    --max-upload-rate flag. The default rate is 1MB/s.

    If there already exists a file upload with the same name, you
    can override it using the --override flag. The default is set
    to false.

    Setting the --purge flag will delete the file from the device
    once it is uploaded. The default is set to false. This option
    is useful when you want to free up space on the device after
    uploading the file.

    Usage Examples:

      Upload a file from a device with a max upload rate of 2MB/s

      $ rio device uploads create DEVICE_NAME FILE_NAME FILE_PATH --max-upload-rate 2097152

      Upload a file from the device and delete it after it uploads

      $ rio device uploads create DEVICE_NAME FILE_NAME FILE_PATH --purge

      Upload a file from the device and override the existing file on the cloud

        $ rio device uploads create DEVICE_NAME FILE_NAME FILE_PATH --override
    """
    try:
        client = new_client()
        device = client.get_device(device_id=device_guid)
        upload_request = LogsUploadRequest(
            device_path=file_path,
            file_name=upload_name,
            max_upload_rate=max_upload_rate,
            override=override,
            purge_after=purge,
        )
        device.upload_log_file(upload_request)
        spinner.text = click.style("File upload requested successfully.", fg=Colors.GREEN)
        spinner.green.ok(Symbols.SUCCESS)
    except Exception as e:
        spinner.text = click.style(
            "Failed to request upload: {}".format(e), fg=Colors.RED
        )
        spinner.red.fail(Symbols.ERROR)
        raise SystemExit(1) from e


@device_uploads.command(
    "status",
    cls=HelpColorsCommand,
    help_headers_color=Colors.YELLOW,
    help_options_color=Colors.GREEN,
)
@click.argument("device-name", type=str)
@click.argument("file-name", type=str)
@name_to_guid
@name_to_request_id
def upload_status(
    device_name: str,
    device_guid: str,
    file_name: str,
    request_id: str,
) -> None:
    """Check the status of a file upload."""
    try:
        client = new_client()
        device = client.get_device(device_id=device_guid)
        status = device.get_log_upload_status(request_uuid=request_id)
        click.secho(status.status)
    except Exception as e:
        click.secho(str(e), fg=Colors.RED)
        raise SystemExit(1) from e


@device_uploads.command(
    "delete",
    cls=HelpColorsCommand,
    help_headers_color=Colors.YELLOW,
    help_options_color=Colors.GREEN,
)
@click.argument("device-name", type=str)
@click.argument("file-name", type=str)
@name_to_guid
@name_to_request_id
@with_spinner(text="Deleting upload...")
def delete_upload(
    device_name: str, device_guid: str, file_name: str, request_id: str, spinner=None
) -> None:
    """Delete an uploaded file."""
    try:
        client = new_client()
        device = client.get_device(device_id=device_guid)
        device.delete_uploaded_log_file(request_uuid=request_id)
        spinner.text = click.style("Deleted upload successfully.", fg=Colors.GREEN)
        spinner.green.ok(Symbols.SUCCESS)
    except Exception as e:
        spinner.text = click.style("Failed to delete upload: {}".format(e), fg=Colors.RED)
        spinner.red.fail(Symbols.ERROR)
        raise SystemExit(1) from e


@device_uploads.command(
    "download",
    cls=HelpColorsCommand,
    help_headers_color=Colors.YELLOW,
    help_options_color=Colors.GREEN,
)
@click.argument("device-name", type=str)
@click.argument("file-name", type=str)
@name_to_guid
@name_to_request_id
@with_spinner(text="Downloading file...")
def download_log(
    device_name: str, device_guid: str, file_name: str, request_id: str, spinner=None
) -> None:
    """Download a file from the device."""
    try:
        client = new_client()
        device = client.get_device(device_id=device_guid)
        url = device.download_log_file(request_uuid=request_id)
        spinner.text = click.style(url, fg=Colors.BLUE)
        spinner.green.ok(Symbols.SUCCESS)
    except Exception as e:
        spinner.text = click.style(str(e), fg=Colors.RED)
        spinner.red.fail(Symbols.ERROR)
        raise SystemExit(1) from e


@device_uploads.command(
    "cancel",
    cls=HelpColorsCommand,
    help_headers_color=Colors.YELLOW,
    help_options_color=Colors.GREEN,
)
@click.argument("device-name", type=str)
@click.argument("file-name", type=str)
@name_to_guid
@name_to_request_id
@with_spinner(text="Cancelling upload...")
def cancel_upload(
    device_name: str, device_guid: str, file_name: str, request_id: str, spinner=None
) -> None:
    """Cancel an ongoing upload operation."""
    try:
        client = new_client()
        device = client.get_device(device_id=device_guid)
        device.cancel_log_file_upload(request_uuid=request_id)
        spinner.text = click.style("Cancelled upload.", fg=Colors.GREEN)
        spinner.green.ok(Symbols.SUCCESS)
    except Exception as e:
        spinner.text = click.style(str(e), fg=Colors.RED)
        spinner.red.fail(Symbols.ERROR)
        raise SystemExit(1) from e


@device_uploads.command(
    "share",
    cls=HelpColorsCommand,
    help_headers_color=Colors.YELLOW,
    help_options_color=Colors.GREEN,
)
@click.option(
    "--expiry",
    help="Flag to set the expiry date for the Shared URL [default: 7 days]",
    default=7,
)
@click.argument("device-name", type=str)
@click.argument("file-name", type=str)
@name_to_guid
@name_to_request_id
@with_spinner(text="Creating shared URL...")
def shared_url(
    device_name: str,
    device_guid: str,
    file_name: str,
    request_id: str,
    expiry: int,
    spinner=None,
) -> None:
    """Share a URL for an uploaded file.

    The command creates a shared public URL for the file
    uploaded from the device. The URl can be used to download
    the file later from any location.

    Optionally, you can set an expiry on the URL using the
    --expiry flag. The default expiry is 7 days.

    Usage Examples:

      Share a URL for an uploaded file with 10 day expiry

      $ rio device uploads share DEVICE_NAME FILE_NAME --expiry 10
    """
    try:
        client = new_client()
        device = client.get_device(device_id=device_guid)
        expiry_time = datetime.now() + timedelta(days=expiry)
        public_url = device.create_shared_url(
            SharedURL(request_id, expiry_time=expiry_time)
        )
        spinner.text = click.style(public_url.url, fg=Colors.GREEN)
        spinner.green.ok(Symbols.SUCCESS)
    except Exception as e:
        spinner.text = click.style(
            "Failed to create shared URL: {}".format(e), fg=Colors.RED
        )
        spinner.red.fail(Symbols.ERROR)
        raise SystemExit(1) from e


def _display_upload_list(uploads: LogUploads, show_header: bool = True) -> None:
    headers = []
    if show_header:
        headers = ("Upload ID", "Name", "Status", "Total Size")

    data = [[u.request_uuid, u.filename, u.status, u.total_size] for u in uploads]

    tabulate_data(data, headers)

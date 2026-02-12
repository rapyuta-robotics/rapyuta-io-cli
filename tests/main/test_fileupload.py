"""
File Upload Tests for rapyuta.io CLI

This module tests file upload operations for devices including:
- Creating file upload requests
- Checking upload status
- Listing file uploads
- Downloading uploaded files
- Creating shared URLs for uploads
- Deleting file uploads
- Cancelling ongoing uploads
"""

import time

import pytest

from riocli.bootstrap import cli


@pytest.mark.integration
@pytest.mark.slow
class TestFileUpload:
    """Test class for file upload operations"""

    def test_01_create_success_file_upload(self, cli_runner, test_device_setup):
        """Test create file upload request for a device"""
        result = cli_runner.invoke(
            cli,
            [
                "device",
                "uploads",
                "create",
                test_device_setup["device_name"],
                "test-file-1",
                test_device_setup["small_file"],
            ],
        )

        assert result.exit_code == 0, result.output
        assert "File upload requested successfully" in result.output

        # wait for it to become completed before next test
        max_retries = 18
        interval = 5
        for _ in range(max_retries):
            result = cli_runner.invoke(
                cli,
                [
                    "device",
                    "uploads",
                    "status",
                    test_device_setup["device_name"],
                    "test-file-1",
                ],
            )

            if result.exit_code == 0:
                status = result.output.strip()
                if status == "COMPLETED":
                    break

            time.sleep(interval)

    def test_02_create_file_upload_with_wrong_file_path(
        self, cli_runner, test_device_setup
    ):
        """Test create file upload request for a device with non-existent file path"""
        result = cli_runner.invoke(
            cli,
            [
                "device",
                "uploads",
                "create",
                test_device_setup["device_name"],
                "test-file-1-failed",
                "non_existent_file_path",
            ],
        )

        assert result.exit_code == 0, result.output
        assert "File upload requested successfully" in result.output

        max_retries = 18
        interval = 5
        for _ in range(max_retries):
            result = cli_runner.invoke(
                cli,
                [
                    "device",
                    "uploads",
                    "status",
                    test_device_setup["device_name"],
                    "test-file-1-failed",
                ],
            )

            if result.exit_code == 0:
                status = result.output.strip()
                if status == "FAILED":
                    break

            time.sleep(interval)

    def test_03_create_file_upload_with_custom_max_upload_rate(
        self, cli_runner, test_device_setup
    ):
        """Test that file upload can be created with a custom max upload rate"""
        result = cli_runner.invoke(
            cli,
            [
                "device",
                "uploads",
                "create",
                test_device_setup["device_name"],
                "large-file-1",
                test_device_setup["large_file"],
                "--max-upload-rate",
                "2097152",
            ],
        )

        assert result.exit_code == 0, result.output
        assert "File upload requested successfully" in result.output

    def test_04_create_file_upload_with_override_flag(
        self, cli_runner, test_device_setup
    ):
        """Test that file upload can be created with override flag"""
        result = cli_runner.invoke(
            cli,
            [
                "device",
                "uploads",
                "create",
                test_device_setup["device_name"],
                "test-file-1",
                test_device_setup["small_file"],
                "--override",
            ],
        )
        assert result.exit_code == 0, result.output
        assert "File upload requested successfully" in result.output

    def test_05_create_file_upload_with_purge_after_flag(
        self, cli_runner, test_device_setup
    ):
        """Test that file upload can be created with purge after flag"""
        result = cli_runner.invoke(
            cli,
            [
                "device",
                "uploads",
                "create",
                test_device_setup["device_name"],
                "test-file-purge-after",
                test_device_setup["small_file"],
                "--purge",
            ],
        )
        assert result.exit_code == 0, result.output
        assert "File upload requested successfully" in result.output

        # wait for file status to be complete
        max_retries = 18
        interval = 5
        for _ in range(max_retries):
            result = cli_runner.invoke(
                cli,
                [
                    "device",
                    "uploads",
                    "status",
                    test_device_setup["device_name"],
                    "test-file-purge-after",
                ],
            )

            if result.exit_code == 0:
                status = result.output.strip()
                if status == "COMPLETED":
                    break

            time.sleep(interval)

        # validate file got deleted after upload completion
        result = cli_runner.invoke(
            cli,
            [
                "device",
                "execute",
                test_device_setup["device_name"],
                "ls /tmp",
            ],
        )
        assert result.exit_code == 0, result.output
        assert test_device_setup["small_file"].split("/")[-1] not in result.output

    def test_06_list_file_uploads(self, cli_runner, test_device_setup):
        """Test list file uploads from a device"""
        device_name = test_device_setup["device_name"]

        result = cli_runner.invoke(cli, ["device", "uploads", "list", device_name])

        assert result.exit_code == 0, result.output
        assert "test-file-1" in result.output
        assert "large-file-1" in result.output
        assert "test-file-purge-after" in result.output
        assert "test-file-1-failed" in result.output

    def test_07_check_file_upload_status(self, cli_runner, test_device_setup):
        """Test that super user can check the status of a file upload"""
        device_name = test_device_setup["device_name"]

        result = cli_runner.invoke(
            cli,
            [
                "device",
                "uploads",
                "status",
                device_name,
                "test-file-1",
            ],
        )

        assert result.exit_code == 0
        assert "COMPLETED" in result.output

    def test_08_download_file_upload(self, cli_runner, test_device_setup):
        """Test get download URL for an uploaded file"""
        result = cli_runner.invoke(
            cli,
            [
                "device",
                "uploads",
                "download",
                test_device_setup["device_name"],
                "test-file-1",
            ],
        )

        assert result.exit_code == 0
        assert "https://iostorageaccountstag" in result.output

    def test_09_cancel_file_upload(self, cli_runner, test_device_setup):
        """Test that file upload can be cancelled"""
        result = cli_runner.invoke(
            cli,
            [
                "device",
                "uploads",
                "create",
                test_device_setup["device_name"],
                "test-file-cancel",
                test_device_setup["large_file"],
            ],
        )

        assert result.exit_code == 0, result.output
        assert "File upload requested successfully" in result.output

        result = cli_runner.invoke(
            cli,
            [
                "device",
                "uploads",
                "cancel",
                test_device_setup["device_name"],
                "test-file-cancel",
            ],
        )

        assert result.exit_code == 0, result.output
        assert "Cancelled upload" in result.output

        # wait for status to become cancelled
        max_retries = 18
        interval = 5
        for _ in range(max_retries):
            result = cli_runner.invoke(
                cli,
                [
                    "device",
                    "uploads",
                    "status",
                    test_device_setup["device_name"],
                    "test-file-cancel",
                ],
            )

            if result.exit_code == 0:
                status = result.output.strip()
                if status == "CANCELLED":
                    break

            time.sleep(interval)

    def test_10_delete_cancelled_file_upload(self, cli_runner, test_device_setup):
        """Test that cancelled file upload can be deleted"""
        result = cli_runner.invoke(
            cli,
            [
                "device",
                "uploads",
                "delete",
                test_device_setup["device_name"],
                "test-file-cancel",
            ],
        )

        assert result.exit_code == 0, result.output
        assert "Deleted upload successfully" in result.output

        # Verify file is not in list anymore
        result = cli_runner.invoke(
            cli,
            [
                "device",
                "uploads",
                "list",
                test_device_setup["device_name"],
            ],
        )

        assert result.exit_code == 0, result.output
        assert "test-file-cancel" not in result.output

    def test_11_delete_completed_file_upload(self, cli_runner, test_device_setup):
        """Test that completed file upload can be deleted"""
        result = cli_runner.invoke(
            cli,
            [
                "device",
                "uploads",
                "delete",
                test_device_setup["device_name"],
                "test-file-purge-after",
            ],
        )

        assert result.exit_code == 0, result.output
        assert "Deleted upload successfully" in result.output

        # Verify file is not in list anymore
        result = cli_runner.invoke(
            cli,
            [
                "device",
                "uploads",
                "list",
                test_device_setup["device_name"],
            ],
        )

        assert result.exit_code == 0, result.output
        assert "test-file-purge-after" not in result.output

    def test_12_delete_failed_file_upload(self, cli_runner, test_device_setup):
        """Test that failed file upload can be deleted"""
        result = cli_runner.invoke(
            cli,
            [
                "device",
                "uploads",
                "delete",
                test_device_setup["device_name"],
                "test-file-1-failed",
            ],
        )

        assert result.exit_code == 0, result.output
        assert "Deleted upload successfully" in result.output

        result = cli_runner.invoke(
            cli,
            [
                "device",
                "uploads",
                "list",
                test_device_setup["device_name"],
            ],
        )

        assert result.exit_code == 0, result.output
        assert "test-file-1-failed" not in result.output

    def test_13_create_shared_url(self, cli_runner, test_device_setup):
        """Test create a shared URL for an uploaded file"""
        device_name = test_device_setup["device_name"]

        result = cli_runner.invoke(
            cli,
            [
                "device",
                "uploads",
                "share",
                device_name,
                "test-file-1",
            ],
        )

        assert result.exit_code == 0
        assert "/v2/devices/fileuploads/sharedurls/sharedurl-" in result.output

    def test_14_create_shared_url_with_custom_expiry(self, cli_runner, test_device_setup):
        """Test create a shared URL for an uploaded file with custom expiry time"""
        # Note: since there is no list shared url so cannot validate the expiry time,
        # but we can at least check that the shared url got created successfully.
        result = cli_runner.invoke(
            cli,
            [
                "device",
                "uploads",
                "share",
                test_device_setup["device_name"],
                "test-file-1",
                "--expiry",
                "2",
            ],
        )

        assert result.exit_code == 0
        assert "/v2/devices/fileuploads/sharedurls/sharedurl-" in result.output

    def test_15_create_upload_with_nonexistent_device(
        self, cli_runner, test_device_setup
    ):
        """Test create file upload with non-existent device name"""
        result = cli_runner.invoke(
            cli,
            [
                "device",
                "uploads",
                "create",
                "nonexistent-device-name",
                "test-file",
                test_device_setup["small_file"],
            ],
        )

        assert result.exit_code == 1
        assert "device not found" in result.output.lower()

    def test_16_create_upload_with_invalid_max_upload_rate(
        self, cli_runner, test_device_setup
    ):
        """Test create file upload with unaccepted value of max upload rate"""
        result = cli_runner.invoke(
            cli,
            [
                "device",
                "uploads",
                "create",
                test_device_setup["device_name"],
                "test-file",
                test_device_setup["small_file"],
                "--max-upload-rate",
                "invalid_value",
            ],
        )

        assert result.exit_code != 0

    def test_17_create_upload_with_same_name_without_override(
        self, cli_runner, test_device_setup
    ):
        """Test create file upload with same name without override flag"""
        result = cli_runner.invoke(
            cli,
            [
                "device",
                "uploads",
                "create",
                test_device_setup["device_name"],
                "test-file-1",
                test_device_setup["small_file"],
            ],
        )

        assert result.exit_code == 1
        assert (
            "Failed to request upload: file already exists with name: test-file-1"
            in result.output
        )

    def test_18_override_ongoing_upload(
        self, cli_runner, test_device_setup, device_file_factory
    ):
        """Test create same name file upload with override for an ongoing file upload"""
        test_file = device_file_factory(
            test_device_setup["device_name"], "test-override-ongoing.txt", 50000
        )

        result = cli_runner.invoke(
            cli,
            [
                "device",
                "uploads",
                "create",
                test_device_setup["device_name"],
                "test-ongoing-override",
                test_file,
            ],
        )

        assert result.exit_code == 0, result.output

        result = cli_runner.invoke(
            cli,
            [
                "device",
                "uploads",
                "create",
                test_device_setup["device_name"],
                "test-ongoing-override",
                test_file,
                "--override",
            ],
        )

        assert result.exit_code == 1
        assert (
            "Failed to request upload: upload is in progress, cannot override, you must cancel it first"
            in result.output
        )

    def test_19_cancel_completed_upload(self, cli_runner, test_device_setup):
        """Test cancel a completed file upload"""
        result = cli_runner.invoke(
            cli,
            [
                "device",
                "uploads",
                "cancel",
                test_device_setup["device_name"],
                "test-file-1",
            ],
        )

        assert result.exit_code == 1
        assert "upload should be in progress" in result.output

    def test_20_cancel_nonexistent_upload(self, cli_runner, test_device_setup):
        """Test cancel a non-existent file upload"""
        result = cli_runner.invoke(
            cli,
            [
                "device",
                "uploads",
                "cancel",
                test_device_setup["device_name"],
                "nonexistent-file-upload",
            ],
        )

        assert result.exit_code == 1
        assert "file not found" in result.output.lower()

    def test_21_download_in_progress_upload(
        self, cli_runner, test_device_setup, device_file_factory
    ):
        """Test download an in progress file upload"""
        test_file = device_file_factory(
            test_device_setup["device_name"], "test-download-progress.txt", 100000
        )

        result = cli_runner.invoke(
            cli,
            [
                "device",
                "uploads",
                "create",
                test_device_setup["device_name"],
                "test-download-progress",
                test_file,
            ],
        )

        assert result.exit_code == 0, result.output

        result = cli_runner.invoke(
            cli,
            [
                "device",
                "uploads",
                "download",
                test_device_setup["device_name"],
                "test-download-progress",
            ],
        )

        assert result.exit_code == 1
        assert "file upload not in completed state" in result.output

    def test_22_download_nonexistent_upload(self, cli_runner, test_device_setup):
        """Test download a non-existent file upload"""
        result = cli_runner.invoke(
            cli,
            [
                "device",
                "uploads",
                "download",
                test_device_setup["device_name"],
                "nonexistent-file-upload",
            ],
        )

        assert result.exit_code == 1
        assert "file not found" in result.output.lower()

    def test_23_delete_ongoing_upload(
        self, cli_runner, test_device_setup, device_file_factory
    ):
        """Test delete an ongoing file upload"""
        test_file = device_file_factory(
            test_device_setup["device_name"], "test-delete-ongoing.txt", 100000
        )

        result = cli_runner.invoke(
            cli,
            [
                "device",
                "uploads",
                "create",
                test_device_setup["device_name"],
                "test-delete-ongoing",
                test_file,
            ],
        )

        assert result.exit_code == 0, result.output

        result = cli_runner.invoke(
            cli,
            [
                "device",
                "uploads",
                "status",
                test_device_setup["device_name"],
                "test-delete-ongoing",
            ],
        )

        assert result.exit_code == 0
        status = result.output.strip()
        assert status in ["PENDING", "IN_PROGRESS"]

        result = cli_runner.invoke(
            cli,
            [
                "device",
                "uploads",
                "delete",
                test_device_setup["device_name"],
                "test-delete-ongoing",
            ],
        )

        assert result.exit_code == 1
        assert (
            "Failed to delete upload: upload in progress can not be deleted, please cancel first"
            in result.output
        )

    def test_24_create_shared_url_for_nonexistent_file(
        self, cli_runner, test_device_setup
    ):
        """Test create shared url for a non-existent file"""
        result = cli_runner.invoke(
            cli,
            [
                "device",
                "uploads",
                "share",
                test_device_setup["device_name"],
                "nonexistent-file-upload",
            ],
        )

        assert result.exit_code == 1
        assert "file not found" in result.output.lower()

    def test_25_create_shared_url_with_invalid_expiry(
        self, cli_runner, test_device_setup
    ):
        """Test create shared url with an unacceptable custom expiry value"""
        result = cli_runner.invoke(
            cli,
            [
                "device",
                "uploads",
                "share",
                test_device_setup["device_name"],
                "test-file-1",
                "--expiry",
                "invalid_expiry",
            ],
        )

        assert result.exit_code != 0

"""
Integration Tests for rapyuta.io CLI - Parameter Operations

This module tests parameter upload, download, list, delete, and diff
operations using pytest and Click testing framework.

The parameter feature allows users to upload directory structures as
configuration parameter trees on rapyuta.io. These tests verify end-to-end
functionality of parameter commands using real CLI invocations.

Test execution order:
1. Upload tests (upload parameter trees from fixture directories)
2. List tests (verify uploaded trees are visible)
3. Download tests (download trees and verify content)
4. Diff tests (compare local vs cloud parameter trees)
5. Recreate/overwrite tests (upload with --recreate flag)
6. Selective upload tests (upload specific trees using --tree-names)
7. Delete tests (remove parameter trees)
8. Negative tests (invalid paths, missing trees, invalid names)
9. Cleanup (ensure all test trees are removed)

Test fixtures:
    tests/fixtures/parameter_trees/
        test-tree-1/
            metadata.yaml
            config/
                params.yaml
                env.txt
        test-tree-2/
            metadata.yaml
            settings/
                db.yaml
            data/
                sample.txt

    tests/fixtures/parameter_trees_updated/
        test-tree-1/
            config/
                params.yaml  (modified content)
                env.txt      (modified content)
"""

import filecmp
import os
import shutil
from pathlib import Path
from tempfile import mkdtemp

import pytest

from riocli.bootstrap import cli


def assert_dirs_equal(dir_a: str, dir_b: str) -> None:
    """Recursively assert that two directory trees are identical.

    Checks:
    - No files/dirs present only in *dir_a* (missing from download).
    - No files/dirs present only in *dir_b* (unexpected extras in download).
    - No files that differ between the two sides.
    - Recurses into every common subdirectory.

    Args:
        dir_a: The reference (original/expected) directory.
        dir_b: The directory being verified (e.g. downloaded copy).

    Raises:
        AssertionError: On any discrepancy between the two trees.
    """
    cmp = filecmp.dircmp(dir_a, dir_b)

    assert len(cmp.left_only) == 0, (
        f"Items missing from '{dir_b}' (present in '{dir_a}'): {cmp.left_only}"
    )
    assert len(cmp.right_only) == 0, (
        f"Unexpected extra items in '{dir_b}' (not in '{dir_a}'): {cmp.right_only}"
    )
    assert len(cmp.diff_files) == 0, (
        f"Files differ between '{dir_a}' and '{dir_b}': {cmp.diff_files}"
    )

    if cmp.common_files:
        _match, mismatch, _errors = filecmp.cmpfiles(
            dir_a, dir_b, cmp.common_files, shallow=False
        )
        assert len(mismatch) == 0, (
            f"File content mismatch between '{dir_a}' and '{dir_b}': {mismatch}"
        )

    for sub in cmp.common_dirs:
        assert_dirs_equal(
            os.path.join(dir_a, sub),
            os.path.join(dir_b, sub),
        )


@pytest.mark.integration
@pytest.mark.slow
class TestParameterOperations:
    """
    Integration tests for parameter upload, download, list, delete, and diff.

    These tests run against the real rapyuta.io platform and require
    a valid test configuration with authentication credentials.
    """

    @pytest.fixture(autouse=True)
    def setup_paths(self):
        """Setup paths to test fixture directories."""
        fixtures_dir = Path(__file__).parent.parent / "fixtures"
        self.parameter_trees_dir = fixtures_dir / "parameter_trees"
        self.parameter_trees_updated_dir = fixtures_dir / "parameter_trees_updated"

        # Individual tree names matching the fixture directories
        self.tree_name_1 = "test-tree-1"
        self.tree_name_2 = "test-tree-2"

    # =================
    # UPLOAD TESTS
    # =================

    def test_01_upload_all_parameter_trees(self, logged_in_user_from_config):
        """Test uploading all parameter trees from the fixture directory."""
        runner, _user = logged_in_user_from_config

        # First delete both trees to start clean
        runner.invoke(cli, ["parameter", "delete", self.tree_name_1, "--force"])
        runner.invoke(cli, ["parameter", "delete", self.tree_name_2, "--force"])

        result = runner.invoke(
            cli,
            [
                "parameter",
                "upload",
                str(self.parameter_trees_dir),
                "--force",
            ],
        )

        assert result.exit_code == 0, (
            f"Parameter upload should succeed. "
            f"Exit code: {result.exit_code}, Output: {result.output}"
        )
        assert "Configuration parameters uploaded successfully" in result.output

    def test_02_upload_single_tree_by_name(self, logged_in_user_from_config):
        """Test uploading a single parameter tree by specifying --tree-names."""
        runner, _user = logged_in_user_from_config

        # First delete both trees to start clean
        runner.invoke(cli, ["parameter", "delete", self.tree_name_1, "--force"])
        runner.invoke(cli, ["parameter", "delete", self.tree_name_2, "--force"])

        # Upload only test-tree-1
        result = runner.invoke(
            cli,
            [
                "parameter",
                "upload",
                str(self.parameter_trees_dir),
                "--tree-names",
                self.tree_name_1,
                "--force",
            ],
        )

        assert result.exit_code == 0, (
            f"Parameter upload with --tree-names should succeed. "
            f"Exit code: {result.exit_code}, Output: {result.output}"
        )
        assert "Configuration parameters uploaded successfully" in result.output

    def test_03_upload_multiple_trees_by_name(self, logged_in_user_from_config):
        """Test uploading multiple parameter trees by specifying --tree-names multiple times."""
        runner, _user = logged_in_user_from_config

        # First delete both trees to start clean
        runner.invoke(cli, ["parameter", "delete", self.tree_name_1, "--force"])
        runner.invoke(cli, ["parameter", "delete", self.tree_name_2, "--force"])

        result = runner.invoke(
            cli,
            [
                "parameter",
                "upload",
                str(self.parameter_trees_dir),
                "--tree-names",
                self.tree_name_1,
                "--tree-names",
                self.tree_name_2,
                "--force",
            ],
        )

        assert result.exit_code == 0, (
            f"Parameter upload with multiple --tree-names should succeed. "
            f"Exit code: {result.exit_code}, Output: {result.output}"
        )
        assert "Configuration parameters uploaded successfully" in result.output

    def test_04_upload_with_recreate_flag(self, logged_in_user_from_config):
        """Test uploading parameter trees with --recreate flag to overwrite existing."""
        runner, _user = logged_in_user_from_config

        # Upload updated version of test-tree-1 with --recreate
        result = runner.invoke(
            cli,
            [
                "parameter",
                "upload",
                str(self.parameter_trees_updated_dir),
                "--tree-names",
                self.tree_name_1,
                "--recreate",
                "--force",
            ],
        )

        assert result.exit_code == 0, (
            f"Parameter upload with --recreate should succeed. "
            f"Exit code: {result.exit_code}, Output: {result.output}"
        )
        assert "Configuration parameters uploaded successfully" in result.output

    # =================
    # LIST TESTS
    # =================

    def test_05_list_parameter_trees(self, logged_in_user_from_config):
        """Test listing all parameter trees in the current project."""
        runner, _user = logged_in_user_from_config

        # First ensure trees are uploaded
        runner.invoke(
            cli,
            [
                "parameter",
                "upload",
                str(self.parameter_trees_dir),
                "--force",
            ],
        )

        result = runner.invoke(cli, ["parameter", "list"])

        assert result.exit_code == 0, (
            f"Parameter list should succeed. "
            f"Exit code: {result.exit_code}, Output: {result.output}"
        )

        # Both trees should be visible in the list output
        assert self.tree_name_1 in result.output, (
            f"Tree '{self.tree_name_1}' should be visible in list output. "
            f"Output: {result.output}"
        )
        assert self.tree_name_2 in result.output, (
            f"Tree '{self.tree_name_2}' should be visible in list output. "
            f"Output: {result.output}"
        )

    def test_06_list_shows_uploaded_tree_after_single_upload(
        self, logged_in_user_from_config
    ):
        """Test that a newly uploaded tree appears in list output."""
        runner, _user = logged_in_user_from_config

        # Clean up first
        runner.invoke(cli, ["parameter", "delete", self.tree_name_1, "--force"])
        runner.invoke(cli, ["parameter", "delete", self.tree_name_2, "--force"])

        # Upload only test-tree-1
        runner.invoke(
            cli,
            [
                "parameter",
                "upload",
                str(self.parameter_trees_dir),
                "--tree-names",
                self.tree_name_1,
                "--force",
            ],
        )

        result = runner.invoke(cli, ["parameter", "list"])
        assert result.exit_code == 0

        assert self.tree_name_1 in result.output, (
            f"Tree '{self.tree_name_1}' should appear after upload. "
            f"Output: {result.output}"
        )

    # =================
    # DOWNLOAD TESTS
    # =================

    def test_07_download_all_parameter_trees(self, logged_in_user_from_config):
        """Test downloading all parameter trees to a temporary directory."""
        runner, _user = logged_in_user_from_config

        # Ensure both trees are uploaded
        runner.invoke(
            cli,
            [
                "parameter",
                "upload",
                str(self.parameter_trees_dir),
                "--recreate",
                "--force",
            ],
        )

        download_dir = mkdtemp(prefix="rio-param-test-")
        try:
            result = runner.invoke(
                cli,
                [
                    "parameter",
                    "download",
                    download_dir,
                ],
            )

            assert result.exit_code == 0, (
                f"Parameter download should succeed. "
                f"Exit code: {result.exit_code}, Output: {result.output}"
            )
            assert "Configurations downloaded successfully" in result.output

            # Recursively verify both downloaded trees match the fixture source,
            # including all subdirectories (e.g. config/params.yaml, settings/db.yaml).
            for tree_name in (self.tree_name_1, self.tree_name_2):
                assert_dirs_equal(
                    os.path.join(str(self.parameter_trees_dir), tree_name),
                    os.path.join(download_dir, tree_name),
                )
        finally:
            shutil.rmtree(download_dir, ignore_errors=True)

    def test_08_download_specific_tree_by_name(self, logged_in_user_from_config):
        """Test downloading specific parameter trees by name."""
        runner, _user = logged_in_user_from_config

        download_dir = mkdtemp(prefix="rio-param-test-")
        try:
            result = runner.invoke(
                cli,
                [
                    "parameter",
                    "download",
                    "--tree-names",
                    self.tree_name_1,
                    download_dir,
                ],
            )

            assert result.exit_code == 0, (
                f"Parameter download with --tree-names should succeed. "
                f"Exit code: {result.exit_code}, Output: {result.output}"
            )
            assert "Configurations downloaded successfully" in result.output

            # Recursively verify the requested tree matches the fixture source,
            # including all subdirectories (e.g. config/params.yaml, config/env.txt).
            assert_dirs_equal(
                os.path.join(str(self.parameter_trees_dir), self.tree_name_1),
                os.path.join(download_dir, self.tree_name_1),
            )

            # Verify that the other tree was NOT downloaded.
            assert not os.path.exists(os.path.join(download_dir, self.tree_name_2)), (
                f"Tree '{self.tree_name_2}' should not have been downloaded "
                f"when only '{self.tree_name_1}' was requested."
            )
        finally:
            shutil.rmtree(download_dir, ignore_errors=True)

    def test_09_download_verifies_file_content(self, logged_in_user_from_config):
        """Test that downloaded files match the originally uploaded content."""
        runner, _user = logged_in_user_from_config

        # Upload the original trees with --recreate to ensure clean state
        runner.invoke(
            cli,
            [
                "parameter",
                "upload",
                str(self.parameter_trees_dir),
                "--recreate",
                "--force",
            ],
        )

        download_dir = mkdtemp(prefix="rio-param-test-")
        try:
            result = runner.invoke(
                cli,
                [
                    "parameter",
                    "download",
                    "--tree-names",
                    self.tree_name_1,
                    download_dir,
                ],
            )
            assert result.exit_code == 0

            original_tree = os.path.join(str(self.parameter_trees_dir), self.tree_name_1)
            downloaded_tree = os.path.join(download_dir, self.tree_name_1)

            assert_dirs_equal(original_tree, downloaded_tree)
        finally:
            shutil.rmtree(download_dir, ignore_errors=True)

    def test_10_download_to_temp_dir_when_no_path(self, logged_in_user_from_config):
        """Test downloading without specifying a path uses a temp directory."""
        runner, _user = logged_in_user_from_config

        result = runner.invoke(
            cli,
            [
                "parameter",
                "download",
                "--tree-names",
                self.tree_name_1,
            ],
        )

        assert result.exit_code == 0, (
            f"Parameter download without path should succeed. "
            f"Exit code: {result.exit_code}, Output: {result.output}"
        )
        assert "Configurations downloaded successfully" in result.output
        assert "Downloading at" in result.output

        cli_temp_dir = None
        for line in result.output.splitlines():
            if "Downloading at" in line:
                # Take everything after the last occurrence of "Downloading at "
                cli_temp_dir = line.split("Downloading at", 1)[-1].strip()
                break

        if cli_temp_dir:
            shutil.rmtree(cli_temp_dir, ignore_errors=True)

    # =================
    # DIFF TESTS
    # =================

    def test_11_diff_identical_trees(self, logged_in_user_from_config):
        """Test diff when local and cloud trees are identical (no output expected)."""
        runner, _user = logged_in_user_from_config

        # Upload the original trees to ensure cloud matches local
        runner.invoke(
            cli,
            [
                "parameter",
                "upload",
                str(self.parameter_trees_dir),
                "--recreate",
                "--force",
            ],
        )

        result = runner.invoke(
            cli,
            [
                "parameter",
                "diff",
                "--tree-names",
                self.tree_name_1,
                str(self.parameter_trees_dir),
            ],
        )

        assert result.exit_code == 0, (
            f"Parameter diff should succeed for identical trees. "
            f"Exit code: {result.exit_code}, Output: {result.output}"
        )

        # For identical trees, there should be no diff markers (--- or +++)
        assert "---" not in result.output, (
            f"Identical trees should produce no diff. Output: {result.output}"
        )

    def test_12_diff_modified_trees(self, logged_in_user_from_config):
        """Test diff when local trees differ from cloud trees."""
        runner, _user = logged_in_user_from_config

        # Upload the original trees first
        runner.invoke(
            cli,
            [
                "parameter",
                "upload",
                str(self.parameter_trees_dir),
                "--tree-names",
                self.tree_name_1,
                "--recreate",
                "--force",
            ],
        )

        # Now diff the updated version against what's in the cloud
        result = runner.invoke(
            cli,
            [
                "parameter",
                "diff",
                "--tree-names",
                self.tree_name_1,
                str(self.parameter_trees_updated_dir),
            ],
        )

        assert result.exit_code == 0, (
            f"Parameter diff should succeed for modified trees. "
            f"Exit code: {result.exit_code}, Output: {result.output}"
        )

        # There should be diff output since files differ
        assert (
            "---" in result.output
            or "+++" in result.output
            or "deleted" in result.output
            or "new" in result.output
        ), f"Modified trees should produce diff output. Output: {result.output}"

    # =================
    # DELETE TESTS
    # =================

    def test_13_delete_single_parameter_tree(self, logged_in_user_from_config):
        """Test deleting a single parameter tree."""
        runner, _user = logged_in_user_from_config

        # Ensure trees are uploaded
        runner.invoke(
            cli,
            [
                "parameter",
                "upload",
                str(self.parameter_trees_dir),
                "--force",
            ],
        )

        result = runner.invoke(
            cli,
            ["parameter", "delete", self.tree_name_2, "--force"],
        )

        assert result.exit_code == 0, (
            f"Parameter delete should succeed. "
            f"Exit code: {result.exit_code}, Output: {result.output}"
        )
        assert "Configuration deleted successfully" in result.output

        # Verify tree is no longer listed
        result = runner.invoke(cli, ["parameter", "list"])
        assert result.exit_code == 0
        assert self.tree_name_2 not in result.output, (
            f"Deleted tree '{self.tree_name_2}' should not appear in list. "
            f"Output: {result.output}"
        )

    def test_14_delete_and_verify_other_tree_remains(self, logged_in_user_from_config):
        """Test that deleting one tree does not affect other trees."""
        runner, _user = logged_in_user_from_config

        # Re-upload both trees
        runner.invoke(
            cli,
            [
                "parameter",
                "upload",
                str(self.parameter_trees_dir),
                "--recreate",
                "--force",
            ],
        )

        # Delete only test-tree-1
        result = runner.invoke(
            cli,
            ["parameter", "delete", self.tree_name_1, "--force"],
        )
        assert result.exit_code == 0

        # Verify test-tree-2 still exists
        result = runner.invoke(cli, ["parameter", "list"])
        assert result.exit_code == 0
        assert self.tree_name_1 not in result.output, (
            f"Deleted tree '{self.tree_name_1}' should not appear in list."
        )
        assert self.tree_name_2 in result.output, (
            f"Tree '{self.tree_name_2}' should still exist after deleting another tree."
        )

    # =================
    # NEGATIVE / EDGE CASE TESTS
    # =================

    def test_15_upload_nonexistent_path(self, logged_in_user_from_config, tmp_path):
        """Test uploading from a non-existent path fails gracefully."""
        runner, _user = logged_in_user_from_config

        # Construct a path that is guaranteed not to exist: a child of the
        # pytest-managed tmp_path that was never created.
        nonexistent_path = tmp_path / "nonexistent-param-dir"

        result = runner.invoke(
            cli,
            [
                "parameter",
                "upload",
                str(nonexistent_path),
                "--force",
            ],
        )

        assert result.exit_code != 0, (
            f"Upload from non-existent path should fail. "
            f"Exit code: {result.exit_code}, Output: {result.output}"
        )

    def test_16_upload_empty_directory(self, logged_in_user_from_config):
        """Test uploading an empty directory shows info message."""
        runner, _user = logged_in_user_from_config

        empty_dir = mkdtemp(prefix="rio-param-empty-")
        try:
            result = runner.invoke(
                cli,
                [
                    "parameter",
                    "upload",
                    empty_dir,
                    "--force",
                ],
            )

            assert result.exit_code == 0, (
                f"Upload of empty directory should exit cleanly. "
                f"Exit code: {result.exit_code}, Output: {result.output}"
            )
            assert "No configuration trees to upload" in result.output
        finally:
            shutil.rmtree(empty_dir, ignore_errors=True)

    def test_17_upload_with_invalid_tree_name_filter(self, logged_in_user_from_config):
        """Test uploading with a --tree-names that doesn't match any directory."""
        runner, _user = logged_in_user_from_config

        result = runner.invoke(
            cli,
            [
                "parameter",
                "upload",
                str(self.parameter_trees_dir),
                "--tree-names",
                "nonexistent-tree",
                "--force",
            ],
        )

        assert result.exit_code != 0, (
            f"Upload with non-matching tree name should fail. "
            f"Exit code: {result.exit_code}, Output: {result.output}"
        )

    def test_18_delete_nonexistent_tree(self, logged_in_user_from_config):
        """Test deleting a non-existent tree succeeds (backend delete is idempotent)."""
        runner, _user = logged_in_user_from_config

        result = runner.invoke(
            cli,
            ["parameter", "delete", "nonexistent-tree-xyz", "--force"],
        )

        # The backend returns 200 for deleting a tree that does not exist,
        # so the CLI exits 0 and reports success — that is the correct behaviour.
        assert result.exit_code == 0, (
            f"Delete of non-existent tree should succeed (idempotent). "
            f"Exit code: {result.exit_code}, Output: {result.output}"
        )
        assert "Configuration deleted successfully" in result.output, (
            f"Expected success message. Output: {result.output}"
        )

    def test_19_upload_directory_with_only_files_no_subdirs(
        self, logged_in_user_from_config
    ):
        """Test uploading a directory with only files (no subdirectories) shows info."""
        runner, _user = logged_in_user_from_config

        flat_dir = mkdtemp(prefix="rio-param-flat-")
        try:
            # Create a directory with only files (no subdirectories)
            with open(os.path.join(flat_dir, "file.txt"), "w") as f:
                f.write("some content")

            result = runner.invoke(
                cli,
                [
                    "parameter",
                    "upload",
                    flat_dir,
                    "--force",
                ],
            )

            assert result.exit_code == 0, (
                f"Upload with only files should exit cleanly. "
                f"Exit code: {result.exit_code}, Output: {result.output}"
            )
            assert "No configuration trees to upload" in result.output
        finally:
            shutil.rmtree(flat_dir, ignore_errors=True)

    # =================
    # RE-UPLOAD / IDEMPOTENCY TESTS
    # =================

    def test_20_reupload_same_trees_without_recreate(self, logged_in_user_from_config):
        """Test re-uploading the same trees without --recreate flag."""
        runner, _user = logged_in_user_from_config

        # First upload
        runner.invoke(
            cli,
            [
                "parameter",
                "upload",
                str(self.parameter_trees_dir),
                "--recreate",
                "--force",
            ],
        )

        # Second upload without --recreate
        result = runner.invoke(
            cli,
            [
                "parameter",
                "upload",
                str(self.parameter_trees_dir),
                "--force",
            ],
        )

        # The behavior may vary — it may succeed or warn. We just check it doesn't crash unexpectedly.
        # Some platforms allow re-upload, others require --recreate.
        assert result.exit_code == 0 or result.exit_code == 1, (
            f"Re-upload without --recreate should either succeed or fail gracefully. "
            f"Exit code: {result.exit_code}, Output: {result.output}"
        )

    def test_21_upload_recreate_and_verify_updated_content(
        self, logged_in_user_from_config
    ):
        """Test that --recreate replaces the tree with updated content."""
        runner, _user = logged_in_user_from_config

        # Upload original trees
        runner.invoke(
            cli,
            [
                "parameter",
                "upload",
                str(self.parameter_trees_dir),
                "--tree-names",
                self.tree_name_1,
                "--recreate",
                "--force",
            ],
        )

        # Upload updated version with --recreate
        runner.invoke(
            cli,
            [
                "parameter",
                "upload",
                str(self.parameter_trees_updated_dir),
                "--tree-names",
                self.tree_name_1,
                "--recreate",
                "--force",
            ],
        )

        # Download and verify the content matches the updated version
        download_dir = mkdtemp(prefix="rio-param-verify-")
        try:
            result = runner.invoke(
                cli,
                [
                    "parameter",
                    "download",
                    "--tree-names",
                    self.tree_name_1,
                    download_dir,
                ],
            )
            assert result.exit_code == 0

            # Recursively compare downloaded content with updated version,
            # including all subdirectories (e.g. config/params.yaml, config/env.txt).
            updated_tree = os.path.join(
                str(self.parameter_trees_updated_dir), self.tree_name_1
            )
            downloaded_tree = os.path.join(download_dir, self.tree_name_1)

            assert_dirs_equal(updated_tree, downloaded_tree)
        finally:
            shutil.rmtree(download_dir, ignore_errors=True)

    # =================
    # CLEANUP TESTS
    # =================

    def test_22_cleanup_all_test_trees(self, logged_in_user_from_config):
        """Cleanup: delete all test parameter trees created during testing."""
        runner, _user = logged_in_user_from_config

        for tree_name in [self.tree_name_1, self.tree_name_2]:
            result = runner.invoke(
                cli,
                ["parameter", "delete", tree_name, "--force"],
            )
            # Allow deletion to fail if tree was already deleted in a prior test
            if result.exit_code == 0:
                assert "Configuration deleted successfully" in result.output

        # Verify no test trees remain
        result = runner.invoke(cli, ["parameter", "list"])
        assert result.exit_code == 0
        assert self.tree_name_1 not in result.output, (
            f"Tree '{self.tree_name_1}' should be cleaned up."
        )
        assert self.tree_name_2 not in result.output, (
            f"Tree '{self.tree_name_2}' should be cleaned up."
        )

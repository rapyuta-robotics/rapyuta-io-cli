from __future__ import annotations

import os
import stat
import subprocess
from dataclasses import asdict
from types import SimpleNamespace

from munch import Munch, munchify

from riocli.compose.defaults import DEFAULT_VOLUME_MOUNTS
from riocli.compose.generate import clean_dict
from riocli.compose.populate import (
    _build_fixup_cmd,
    build_volume_mounts,
    get_volumes_requiring_fixup,
    populate,
    populate_command,
    populate_depends_on,
    populate_entrypoint,
    populate_healthcheck,
)


def _make_deployment(volumes: list[dict]) -> Munch:
    return munchify({"spec": {"volumes": volumes}})


class TestPopulateEntrypoint:
    # populate_entrypoint() only feeds `rio compose generate`'s local Docker
    # Compose output. Real device deployments (`rio apply`) never read an
    # `entrypoint` field -- it has no effect there, only in this pipeline.

    def test_missing_entrypoint_returns_none(self):
        assert populate_entrypoint(munchify({"command": "foo"})) is None

    def test_none_entrypoint_returns_none(self):
        assert populate_entrypoint(munchify({"entrypoint": None})) is None

    def test_explicit_empty_string_entrypoint_is_honored(self):
        # An explicit "" clears the image's ENTRYPOINT entirely in Compose --
        # distinct from not declaring the field at all -- so it must not be
        # treated as "missing".
        exe = munchify({"entrypoint": ""})
        assert populate_entrypoint(exe) == ""

    def test_string_entrypoint_is_returned_as_is(self):
        exe = munchify({"entrypoint": "./owm_bootstrap.sh"})
        assert populate_entrypoint(exe) == "./owm_bootstrap.sh"

    def test_list_entrypoint_is_returned_as_is(self):
        exe = munchify({"entrypoint": ["/usr/local/bin/apiserver"]})
        assert populate_entrypoint(exe) == ["/usr/local/bin/apiserver"]

    def test_dollar_vars_are_escaped(self):
        exe = munchify({"entrypoint": "./run.sh $FOO"})
        assert populate_entrypoint(exe) == "./run.sh $$FOO"

    def test_entrypoint_and_command_coexist(self):
        # entrypoint replaces the image's ENTRYPOINT; command still supplies
        # the args passed to it -- both populate independently.
        exe = munchify({"entrypoint": "./owm_bootstrap.sh", "command": "--foo bar"})
        assert populate_entrypoint(exe) == "./owm_bootstrap.sh"
        assert populate_command(exe) == "--foo bar"


class TestGetVolumesRequiringFixup:
    def test_deduplicates_same_host_and_container(self):
        dep = _make_deployment(
            [
                {
                    "subPath": "/host/path",
                    "mountPath": "/container/path",
                    "uid": 1000,
                    "gid": 1000,
                    "perm": 755,
                },
                {
                    "subPath": "/host/path",
                    "mountPath": "/container/path",
                    "uid": 1000,
                    "gid": 1000,
                    "perm": 755,
                },
            ]
        )
        result = get_volumes_requiring_fixup({"dep": dep})
        assert len(result) == 1
        assert result[0]["host"] == "/host/path"
        assert result[0]["container"] == "/container/path"

    def test_deduplicates_across_deployments(self):
        vol = {
            "subPath": "/host/path",
            "mountPath": "/container/path",
            "uid": 1000,
            "gid": 1000,
            "perm": 755,
        }
        dep1 = _make_deployment([vol])
        dep2 = _make_deployment([vol])
        result = get_volumes_requiring_fixup({"dep1": dep1, "dep2": dep2})
        assert len(result) == 1

    def test_distinct_mounts_are_all_returned(self):
        dep = _make_deployment(
            [
                {
                    "subPath": "/host/a",
                    "mountPath": "/container/a",
                    "uid": 1000,
                    "gid": 1000,
                    "perm": 755,
                },
                {
                    "subPath": "/host/b",
                    "mountPath": "/container/b",
                    "uid": 1000,
                    "gid": 1000,
                    "perm": 755,
                },
            ]
        )
        result = get_volumes_requiring_fixup({"dep": dep})
        assert len(result) == 2

    def test_skips_volumes_without_uid_gid_perm(self):
        dep = _make_deployment(
            [
                {"subPath": "/host/path", "mountPath": "/container/path"},
            ]
        )
        result = get_volumes_requiring_fixup({"dep": dep})
        assert result == []

    def test_same_host_different_container_both_kept(self):
        dep = _make_deployment(
            [
                {
                    "subPath": "/host/path",
                    "mountPath": "/container/a",
                    "uid": 1000,
                    "gid": 1000,
                    "perm": 755,
                },
                {
                    "subPath": "/host/path",
                    "mountPath": "/container/b",
                    "uid": 1000,
                    "gid": 1000,
                    "perm": 755,
                },
            ]
        )
        result = get_volumes_requiring_fixup({"dep": dep})
        assert len(result) == 2


class TestBuildFixupCmdStructure:
    """Verify the shell command string generated by _build_fixup_cmd."""

    def _branches(self, cmd: str) -> tuple[str, str]:
        """Split cmd into (file_branch, dir_branch) strings."""
        # format: "if [ -f ... ]; then FILE; else DIR; fi"
        after_then = cmd.split("; then ", 1)[1]
        file_branch, dir_branch_fi = after_then.split("; else ", 1)
        dir_branch = dir_branch_fi.removesuffix("; fi")
        return file_branch, dir_branch

    def test_structure_is_if_else_fi(self):
        cmd = _build_fixup_cmd(
            {"container": "/data/logs", "uid": None, "gid": None, "perm": 755}
        )
        assert cmd.startswith("if [ -f /data/logs ]")
        assert "; then " in cmd
        assert "; else " in cmd
        assert cmd.endswith("; fi")

    def test_perm_only_dir_branch_has_mkdir_and_chmod(self):
        cmd = _build_fixup_cmd(
            {"container": "/data/logs", "uid": None, "gid": None, "perm": 755}
        )
        _, dir_branch = self._branches(cmd)
        assert "mkdir -p /data/logs" in dir_branch
        assert "chmod 755 /data/logs" in dir_branch
        assert "chown" not in dir_branch

    def test_perm_only_file_branch_has_only_chmod(self):
        cmd = _build_fixup_cmd(
            {"container": "/data/logs", "uid": None, "gid": None, "perm": 755}
        )
        file_branch, _ = self._branches(cmd)
        assert "chmod 755 /data/logs" in file_branch
        assert "mkdir" not in file_branch
        assert "chown" not in file_branch

    def test_no_uid_gid_perm_file_branch_is_noop(self):
        cmd = _build_fixup_cmd(
            {"container": "/data/logs", "uid": None, "gid": None, "perm": None}
        )
        file_branch, _ = self._branches(cmd)
        assert file_branch == ":"

    def test_uid_and_gid_dir_branch_has_recursive_chown(self):
        cmd = _build_fixup_cmd(
            {"container": "/data/logs", "uid": 1000, "gid": 2000, "perm": None}
        )
        _, dir_branch = self._branches(cmd)
        assert "chown -R 1000:2000 /data/logs" in dir_branch

    def test_uid_and_gid_file_branch_has_non_recursive_chown(self):
        cmd = _build_fixup_cmd(
            {"container": "/data/logs", "uid": 1000, "gid": 2000, "perm": None}
        )
        file_branch, _ = self._branches(cmd)
        assert "chown 1000:2000 /data/logs" in file_branch
        assert "-R" not in file_branch

    def test_uid_only_no_gid(self):
        cmd = _build_fixup_cmd(
            {"container": "/data/logs", "uid": 1000, "gid": None, "perm": None}
        )
        file_branch, dir_branch = self._branches(cmd)
        assert "chown 1000: /data/logs" in file_branch
        assert "chown -R 1000: /data/logs" in dir_branch

    def test_gid_only_no_uid(self):
        cmd = _build_fixup_cmd(
            {"container": "/data/logs", "uid": None, "gid": 2000, "perm": None}
        )
        file_branch, dir_branch = self._branches(cmd)
        assert "chown :2000 /data/logs" in file_branch
        assert "chown -R :2000 /data/logs" in dir_branch

    def test_uid_gid_perm_all_present(self):
        cmd = _build_fixup_cmd(
            {"container": "/data/logs", "uid": 1000, "gid": 2000, "perm": 755}
        )
        file_branch, dir_branch = self._branches(cmd)
        assert "mkdir -p /data/logs" in dir_branch
        assert "chown -R 1000:2000 /data/logs" in dir_branch
        assert "chmod 755 /data/logs" in dir_branch
        assert "chown 1000:2000 /data/logs" in file_branch
        assert "chmod 755 /data/logs" in file_branch
        assert "mkdir" not in file_branch

    def test_path_with_spaces_is_quoted(self):
        cmd = _build_fixup_cmd(
            {"container": "/data/my path", "uid": None, "gid": None, "perm": 755}
        )
        # shlex.quote adds single quotes when the path contains spaces
        assert "'/data/my path'" in cmd

    def test_path_with_special_chars_is_quoted(self):
        cmd = _build_fixup_cmd(
            {"container": "/data/$secret", "uid": None, "gid": None, "perm": 755}
        )
        assert "'/data/$secret'" in cmd


class TestBuildFixupCmdShellExecution:
    """Run the generated shell commands via sh and verify filesystem effects."""

    def _sh(self, cmd: str) -> subprocess.CompletedProcess:
        return subprocess.run(["sh", "-c", cmd], capture_output=True, text=True)

    def test_creates_nonexistent_directory(self, tmp_path):
        target = tmp_path / "new_dir"
        cmd = _build_fixup_cmd(
            {"container": str(target), "uid": None, "gid": None, "perm": 755}
        )
        result = self._sh(cmd)
        assert result.returncode == 0, result.stderr
        assert target.is_dir()

    def test_sets_permissions_on_new_directory(self, tmp_path):
        target = tmp_path / "perm_dir"
        cmd = _build_fixup_cmd(
            {"container": str(target), "uid": None, "gid": None, "perm": 700}
        )
        self._sh(cmd)
        assert stat.S_IMODE(target.stat().st_mode) == 0o700

    def test_sets_permissions_on_existing_directory(self, tmp_path):
        target = tmp_path / "existing"
        target.mkdir(mode=0o777)
        cmd = _build_fixup_cmd(
            {"container": str(target), "uid": None, "gid": None, "perm": 750}
        )
        self._sh(cmd)
        assert stat.S_IMODE(target.stat().st_mode) == 0o750

    def test_creates_nested_directories(self, tmp_path):
        target = tmp_path / "a" / "b" / "c"
        cmd = _build_fixup_cmd(
            {"container": str(target), "uid": None, "gid": None, "perm": 755}
        )
        result = self._sh(cmd)
        assert result.returncode == 0, result.stderr
        assert target.is_dir()

    def test_file_branch_does_not_convert_file_to_directory(self, tmp_path):
        target = tmp_path / "config.yaml"
        target.write_text("key: value")
        cmd = _build_fixup_cmd(
            {"container": str(target), "uid": None, "gid": None, "perm": 644}
        )
        result = self._sh(cmd)
        assert result.returncode == 0, result.stderr
        assert target.is_file()

    def test_file_branch_sets_permissions_on_existing_file(self, tmp_path):
        target = tmp_path / "config.yaml"
        target.write_text("key: value")
        cmd = _build_fixup_cmd(
            {"container": str(target), "uid": None, "gid": None, "perm": 600}
        )
        self._sh(cmd)
        assert stat.S_IMODE(target.stat().st_mode) == 0o600

    def test_chown_with_current_user_on_new_directory(self, tmp_path):
        target = tmp_path / "owned"
        uid, gid = os.getuid(), os.getgid()
        cmd = _build_fixup_cmd(
            {"container": str(target), "uid": uid, "gid": gid, "perm": 755}
        )
        result = self._sh(cmd)
        assert result.returncode == 0, result.stderr
        assert target.stat().st_uid == uid
        assert target.stat().st_gid == gid

    def test_chown_with_current_user_on_existing_file(self, tmp_path):
        target = tmp_path / "owned.conf"
        target.write_text("content")
        uid, gid = os.getuid(), os.getgid()
        cmd = _build_fixup_cmd(
            {"container": str(target), "uid": uid, "gid": gid, "perm": 644}
        )
        result = self._sh(cmd)
        assert result.returncode == 0, result.stderr
        assert target.is_file()
        assert target.stat().st_uid == uid

    def test_multiple_entries_chained_with_and(self, tmp_path):
        dir1 = tmp_path / "dir1"
        dir2 = tmp_path / "dir2"
        entries = [
            {"container": str(dir1), "uid": None, "gid": None, "perm": 755},
            {"container": str(dir2), "uid": None, "gid": None, "perm": 700},
        ]
        full_cmd = " && ".join(_build_fixup_cmd(e) for e in entries)
        result = self._sh(full_cmd)
        assert result.returncode == 0, result.stderr
        assert dir1.is_dir()
        assert dir2.is_dir()
        assert stat.S_IMODE(dir1.stat().st_mode) == 0o755
        assert stat.S_IMODE(dir2.stat().st_mode) == 0o700

    def test_path_with_spaces(self, tmp_path):
        target = tmp_path / "my dir"
        cmd = _build_fixup_cmd(
            {"container": str(target), "uid": None, "gid": None, "perm": 755}
        )
        result = self._sh(cmd)
        assert result.returncode == 0, result.stderr
        assert target.is_dir()


class TestBuildVolumeMounts:
    """Cover both device bind mounts and cloud disk-backed named volumes."""

    def test_defaults_always_present(self):
        dep = _make_deployment([])
        named: set[str] = set()
        mounts = build_volume_mounts(dep, named)
        assert mounts == DEFAULT_VOLUME_MOUNTS
        assert named == set()

    def test_device_bind_mount_unchanged(self):
        dep = _make_deployment([{"subPath": "/host/data", "mountPath": "/data"}])
        named: set[str] = set()
        mounts = build_volume_mounts(dep, named)
        assert "/host/data:/data" in mounts
        assert named == set()

    def test_device_bind_mount_applies_permission_mode(self):
        dep = _make_deployment(
            [{"subPath": "/host/data", "mountPath": "/data", "perm": 755}]
        )
        mounts = build_volume_mounts(dep, set())
        assert "/host/data:/data:rw" in mounts

    def test_disk_volume_becomes_named_volume(self):
        dep = _make_deployment(
            [
                {
                    "mountPath": "/data",
                    "subPath": "data",
                    "depends": {"kind": "disk", "nameOrGUID": "neo4j-disk"},
                }
            ]
        )
        named: set[str] = set()
        mounts = build_volume_mounts(dep, named)
        # Named volume keyed by disk name, NOT the relative subPath.
        assert "neo4j-disk:/data" in mounts
        assert "data:/data" not in mounts
        assert named == {"neo4j-disk"}

    def test_disk_volume_without_name_is_skipped(self):
        dep = _make_deployment([{"mountPath": "/data", "depends": {"kind": "disk"}}])
        named: set[str] = set()
        mounts = build_volume_mounts(dep, named)
        assert mounts == DEFAULT_VOLUME_MOUNTS
        assert named == set()

    def test_volume_without_mountpath_is_skipped(self):
        dep = _make_deployment([{"subPath": "/host/data"}])
        mounts = build_volume_mounts(dep, set())
        assert mounts == DEFAULT_VOLUME_MOUNTS

    def test_disk_kind_capitalized_becomes_named_volume(self):
        # SDK DiskDepends defaults to "Disk"; the capitalized spelling must match too.
        dep = _make_deployment(
            [
                {
                    "mountPath": "/data",
                    "depends": {"kind": "Disk", "nameOrGUID": "my-disk"},
                }
            ]
        )
        named: set[str] = set()
        mounts = build_volume_mounts(dep, named)
        assert "my-disk:/data" in mounts
        assert "data:/data" not in mounts
        assert named == {"my-disk"}

    def test_disk_kind_omitted_becomes_named_volume(self):
        # An omitted kind defaults to a disk depends in the SDK model.
        dep = _make_deployment(
            [{"mountPath": "/data", "depends": {"nameOrGUID": "my-disk"}}]
        )
        named: set[str] = set()
        mounts = build_volume_mounts(dep, named)
        assert "my-disk:/data" in mounts
        assert named == {"my-disk"}

    def test_cloud_runtime_omits_default_mounts(self):
        dep = munchify(
            {
                "spec": {
                    "runtime": "cloud",
                    "volumes": [
                        {
                            "mountPath": "/data",
                            "depends": {"kind": "disk", "nameOrGUID": "my-disk"},
                        }
                    ],
                }
            }
        )
        mounts = build_volume_mounts(dep, set())
        # Only the disk mount — none of the device host paths.
        assert mounts == ["my-disk:/data"]

    def test_device_runtime_keeps_default_mounts(self):
        dep = munchify({"spec": {"runtime": "device", "volumes": []}})
        assert build_volume_mounts(dep, set()) == DEFAULT_VOLUME_MOUNTS

    def test_subpath_on_disk_mount_warns_but_mounts_whole_volume(self):
        class _RecordingSpinner:
            def __init__(self):
                self.writes: list[str] = []

            def write(self, text):
                self.writes.append(text)

        dep = _make_deployment(
            [
                {
                    "mountPath": "/data",
                    "subPath": "sub",
                    "depends": {"kind": "disk", "nameOrGUID": "my-disk"},
                }
            ]
        )
        spinner = _RecordingSpinner()
        mounts = build_volume_mounts(dep, set(), spinner=spinner)
        assert "my-disk:/data" in mounts
        assert any("subPath" in w and "sub" in w for w in spinner.writes)


class TestPopulateHealthcheck:
    def test_no_probe_returns_none(self):
        assert populate_healthcheck(munchify({})) is None

    def test_no_exec_command_returns_none(self):
        exe = munchify({"livenessProbe": {"exec": {}}})
        assert populate_healthcheck(exe) is None

    def test_exec_probe(self):
        exe = munchify(
            {
                "livenessProbe": {
                    "exec": {"command": ["health", "check"]},
                    "timeoutSeconds": 5,
                    "periodSeconds": 15,
                    "failureThreshold": 2,
                }
            }
        )
        hc = populate_healthcheck(exe)
        assert hc.test == "health check"
        assert hc.timeout == "5s"
        assert hc.interval == "15s"
        assert hc.retries == 2
        assert hc.start_period is None

    def test_exec_probe_sets_start_period_from_initial_delay(self):
        exe = munchify(
            {
                "livenessProbe": {
                    "exec": {"command": ["true"]},
                    "initialDelaySeconds": 20,
                }
            }
        )
        hc = populate_healthcheck(exe)
        assert hc.start_period == "20s"

    def test_httpget_probe_is_ignored(self):
        # httpGet probes are not translated: images often lack curl/wget, so an
        # in-container HTTP healthcheck would report a false 'unhealthy'.
        exe = munchify(
            {
                "livenessProbe": {
                    "httpGet": {"path": "/healthz", "port": 2100},
                    "initialDelaySeconds": 30,
                }
            }
        )
        assert populate_healthcheck(exe) is None


class TestPopulateDependsOn:
    def _fixture(self, dep_exe: dict):
        deployment = munchify(
            {
                "spec": {
                    "depends": [{"kind": "deployment", "nameOrGUID": "dep-b"}],
                }
            }
        )
        deployments = munchify(
            {
                "deployment:dep-b": {
                    "metadata": {"depends": {"nameOrGUID": "pkg-b", "version": "1"}},
                }
            }
        )
        packages = munchify(
            {
                "package:pkg-b": {
                    "metadata": {"version": "1"},
                    "spec": {"executables": [dep_exe]},
                }
            }
        )
        return deployment, deployments, packages

    def test_dependency_without_probe_uses_service_started(self):
        deployment, deployments, packages = self._fixture({"name": "exe-b"})
        result = populate_depends_on(deployment, deployments, packages)
        assert result["dep-b_exe-b"].condition == "service_started"

    def test_dependency_with_httpget_probe_uses_service_started(self):
        # httpGet probes emit no healthcheck, so ordering falls back to service_started.
        exe = {
            "name": "exe-b",
            "livenessProbe": {"httpGet": {"path": "/healthz", "port": 2100}},
        }
        deployment, deployments, packages = self._fixture(exe)
        result = populate_depends_on(deployment, deployments, packages)
        assert result["dep-b_exe-b"].condition == "service_started"

    def test_dependency_with_exec_probe_uses_service_healthy(self):
        exe = {
            "name": "exe-b",
            "livenessProbe": {"exec": {"command": ["true"]}},
        }
        deployment, deployments, packages = self._fixture(exe)
        result = populate_depends_on(deployment, deployments, packages)
        assert result["dep-b_exe-b"].condition == "service_healthy"


class TestPopulateNamedVolumes:
    """End-to-end populate(): disk mounts surface as top-level volumes and survive
    the asdict() + clean_dict() serialization path used by `generate`."""

    def _cloud_fixture(self):
        deployment = munchify(
            {
                "metadata": {
                    "name": "svc",
                    "depends": {"nameOrGUID": "svc-pkg", "version": "1"},
                },
                "spec": {
                    "runtime": "cloud",
                    "volumes": [
                        {
                            "execName": "app",
                            "mountPath": "/data",
                            "subPath": "data",
                            "depends": {"kind": "disk", "nameOrGUID": "svc-disk"},
                        }
                    ],
                },
            }
        )
        package = munchify(
            {
                "metadata": {"name": "svc-pkg", "version": "1"},
                "spec": {
                    "runtime": "cloud",
                    "executables": [
                        {"name": "app", "type": "docker", "docker": {"image": "img:1"}}
                    ],
                },
            }
        )
        ctx = SimpleNamespace(obj=SimpleNamespace(data={}))
        return ctx, {"deployment:svc": deployment}, {"package:svc-pkg": package}

    def test_disk_mount_declared_as_top_level_volume(self):
        ctx, deployments, packages = self._cloud_fixture()
        compose = populate(ctx, deployments, packages)
        assert compose.volumes == {"svc-disk": {"driver": "local"}}

        cleaned = clean_dict(asdict(compose))
        # The non-empty driver map survives clean_dict (an empty {} would be stripped).
        assert cleaned["volumes"] == {"svc-disk": {"driver": "local"}}
        assert "svc-disk:/data" in cleaned["services"]["svc_app"]["volumes"]

    def test_no_top_level_volumes_without_disk_mounts(self):
        ctx, deployments, packages = self._cloud_fixture()
        deployments["deployment:svc"].spec.volumes = []
        compose = populate(ctx, deployments, packages)
        assert compose.volumes is None
        # clean_dict drops the None volumes key entirely.
        assert "volumes" not in clean_dict(asdict(compose))

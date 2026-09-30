from __future__ import annotations

from unittest.mock import MagicMock

from rapyuta_io_sdk_v2 import Restore

from riocli.constants import DeleteResult
from riocli.database.restore.util import _source_summary, display_restore_list


def _restore(source: dict, status: dict | None = None) -> Restore:
    return Restore.model_validate(
        {
            "apiVersion": "api.rapyuta.io/v2",
            "kind": "Restore",
            "metadata": {"name": "orders-restore", "guid": "restore-aaaaaaaaaaaaaaaa"},
            "spec": {"database": "orders-db", "source": source},
            "status": status,
        }
    )


def test_source_summary_backup_names_the_archive():
    # The archive is what the restore actually reads, so it is what is shown —
    # not the backup name, which is provenance and may be absent.
    r = _restore(
        {
            "type": "backup",
            "fileUpload": "orders_20260101T020000.tar.gz",
            "backupName": "orders-nightly",
        }
    )
    assert _source_summary(r.spec.source) == "backup: orders_20260101T020000.tar.gz"


def test_source_summary_backup_by_guid():
    r = _restore({"type": "backup", "fileUpload": "fileupload-abc123"})
    assert _source_summary(r.spec.source) == "backup: fileupload-abc123"


def test_source_summary_data_directory():
    # A migration's source is a path on the device, not a platform resource.
    r = _restore(
        {
            "type": "dataDirectory",
            "oldDataDirectory": "/opt/rapyuta/volumes/orders-db/17",
            "sourceVersion": "17",
        }
    )
    assert (
        _source_summary(r.spec.source)
        == "dataDirectory: /opt/rapyuta/volumes/orders-db/17"
    )


def test_step_is_shown_alongside_the_phase(capsys):
    # A restore sits in Running for minutes, so the phase alone cannot tell
    # progress from a stall.
    r = _restore(
        {"type": "backup", "fileUpload": "fileupload-abc123"},
        {"phase": "Running", "step": "Transferring"},
    )

    display_restore_list([r])
    out = capsys.readouterr().out

    assert "Running" in out
    assert "Transferring" in out


def test_missing_status_does_not_break_the_table(capsys):
    display_restore_list([_restore({"type": "backup", "fileUpload": "fileupload-x"})])
    assert "Unknown" in capsys.readouterr().out


def _restore_resource():
    from riocli.database.restore.model import Restore as RestoreResource

    return RestoreResource(
        {
            "apiVersion": "api.rapyuta.io/v2",
            "kind": "Restore",
            "metadata": {"name": "orders-restore"},
            "spec": {
                "database": "orders-db",
                "source": {"type": "backup", "fileUpload": "fileupload-abc"},
            },
        }
    )


def test_delete_reports_a_restore_as_retained():
    # The API has no restore delete, so the audit record stays; raising instead
    # would abort `rio delete -f` for every other resource in the bundle.
    v2 = MagicMock()
    result = _restore_resource().delete(
        client=MagicMock(),
        v2_client=v2,
        config=MagicMock(),
        retry_count=0,
        retry_interval=0,
    )

    assert result == DeleteResult.RETAINED
    assert v2.method_calls == []


def test_delete_manifest_prints_retained_for_a_restore_and_deleted_otherwise():
    from riocli.apply.parse import Applier
    from riocli.secret.model import Secret

    applier = Applier.__new__(Applier)
    applier.config = MagicMock()
    applier.objects = {"restore:orders-restore": _restore_resource()}

    applier.objects["secret:db-creds"] = Secret(
        {
            "apiVersion": "api.rapyuta.io/v2",
            "kind": "Secret",
            "metadata": {"name": "db-creds"},
            "spec": {"type": "Opaque", "data": {"USER": "appuser"}},
        }
    )

    lines = {}
    for key in applier.objects:
        spinner = MagicMock()
        applier._delete_manifest(key, v2_client=MagicMock(), spinner=spinner)
        lines[key] = spinner.write.call_args.args[0]

    assert "Retained" in lines["restore:orders-restore"]
    assert "Deleted" not in lines["restore:orders-restore"]
    assert "Deleted" in lines["secret:db-creds"]

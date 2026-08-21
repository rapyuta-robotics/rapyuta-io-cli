from __future__ import annotations

from rapyuta_io_sdk_v2 import Restore

from riocli.restore.util import _source_summary, display_restore_list


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
        {"phase": "Running", "step": "loading orders"},
    )

    display_restore_list([r])
    out = capsys.readouterr().out

    assert "Running" in out
    assert "loading orders" in out


def test_missing_status_does_not_break_the_table(capsys):
    display_restore_list([_restore({"type": "backup", "fileUpload": "fileupload-x"})])
    assert "Unknown" in capsys.readouterr().out

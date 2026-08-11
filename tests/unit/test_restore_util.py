from rapyuta_io_sdk_v2 import Restore

from riocli.restore.util import _source_summary


def _restore(source: dict) -> Restore:
    return Restore.model_validate(
        {
            "apiVersion": "api.rapyuta.io/v2",
            "kind": "Restore",
            "metadata": {"name": "orders-restore", "guid": "restore-aaaaaaaaaaaaaaaa"},
            "spec": {"database": "orders-db", "source": source},
        }
    )


def test_source_summary_backup_latest_run():
    # No run pinned: the restore takes the backup's latest.
    r = _restore({"type": "backup", "backupName": "orders-nightly"})
    assert _source_summary(r.spec.source) == "backup: orders-nightly"


def test_source_summary_backup_pinned_run():
    # A pinned run is what distinguishes two restores of the same backup, so it
    # belongs in the summary.
    r = _restore(
        {
            "type": "backup",
            "backupName": "orders-nightly",
            "backupRunID": "20260101T020000",
        }
    )
    assert _source_summary(r.spec.source) == "backup: orders-nightly (20260101T020000)"


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

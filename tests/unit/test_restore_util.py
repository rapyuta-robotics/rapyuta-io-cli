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

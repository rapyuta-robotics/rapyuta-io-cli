from rapyuta_io_sdk_v2 import Database

from riocli.database.util import _standby_summary


def _database(standby_devices: int = 0, running: int = 0) -> Database:
    postgres = {
        "version": "17",
        "primary": {"deviceName": "edge-node-01", "port": 5432},
    }
    status = {"phase": "Running", "postgres": {}}

    if standby_devices:
        postgres["standby"] = {
            "primaryInterface": "eth0",
            "devices": [
                {"deviceName": f"edge-node-{i + 2:02d}", "port": 5432}
                for i in range(standby_devices)
            ],
        }
        status["postgres"]["standby"] = [
            {
                "deviceName": f"edge-node-{i + 2:02d}",
                "port": 5432,
                "phase": "running" if i < running else "crashloop",
            }
            for i in range(standby_devices)
        ]

    return Database.model_validate(
        {
            "apiVersion": "api.rapyuta.io/v2",
            "kind": "Database",
            "metadata": {"name": "orders-db", "guid": "db-aaaaaaaaaaaaaaaaaaaa"},
            "spec": {"type": "postgres", "postgres": postgres},
            "status": status,
        }
    )


def test_standby_summary_without_standby():
    assert _standby_summary(_database()) == "-"


def test_standby_summary_all_running():
    assert _standby_summary(_database(standby_devices=2, running=2)) == "2/2"


def test_standby_summary_partially_running():
    assert _standby_summary(_database(standby_devices=2, running=1)) == "1/2"


def test_standby_summary_without_reported_status():
    db = _database(standby_devices=1, running=1)
    db.status = None
    assert _standby_summary(db) == "0/1"

from munch import Munch
from rapyuta_io_sdk_v2 import Client as v2Client
from rapyuta_io_sdk_v2 import DatabaseCreate as DatabaseModel
from typing_extensions import override

from riocli.model import Model


class Database(Model):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.update(*args, **kwargs)
        self._obj = DatabaseModel.model_validate(self)

    @override
    def create_object(
        self, v2_client: v2Client, retry_count: int, retry_interval: int, *args, **kwargs
    ) -> DatabaseModel:
        return v2_client.create_database(body=self._obj)  # pyright:ignore[reportArgumentType]

    @override
    def update_object(self, *args, **kwargs) -> Munch | None:
        raise NotImplementedError

    @override
    def delete_object(self, v2_client: v2Client, *args, **kwargs) -> None:
        _ = v2_client.delete_database(self._obj.metadata.name)

    @override
    def list_dependencies(self) -> list[str] | None:
        return None

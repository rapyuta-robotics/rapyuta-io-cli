# Copyright 2025 Rapyuta Robotics
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


from munch import Munch
from rapyuta_io_sdk_v2 import Client
from rapyuta_io_sdk_v2 import Role as RoleModel
from rapyuta_io_sdk_v2 import RoleBinding as RoleBindingModel
from rapyuta_io_sdk_v2.exceptions import HttpAlreadyExistsError, HttpNotFoundError
from typing_extensions import override

from riocli.constants import ApplyResult
from riocli.model import Model
from riocli.role.select import find_bindings
from riocli.role.window import format_time, same_time, utcnow

_CREATE = "create"
_EXISTS = "exists"
_REPLACE = "replace"


class Role(Model):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.update(*args, **kwargs)
        self._obj = RoleModel.model_validate(self)

    @override
    def create_object(self, v2_client: Client, *args, **kwargs) -> Munch | None:
        return v2_client.create_role(self._obj)  # pyright:ignore[reportArgumentType]

    @override
    def update_object(self, v2_client: Client, *args, **kwargs) -> Munch | None:
        return v2_client.update_role(self._obj)  # pyright:ignore[reportArgumentType]

    @override
    def delete_object(self, v2_client: Client, *args, **kwargs) -> None:
        _ = v2_client.delete_role(self._obj.metadata.name)

    @override
    def list_dependencies(self) -> list[str] | None:
        return None


class RoleBinding(Model):
    """A RoleBinding manifest is the desired state of one binding.

    A permanent binding exists or not. A time-bound binding is identified by
    its start: applying a manifest replaces the time-bound binding with the
    same start (both empty counts as equal) or creates one, so changing the
    end in the manifest extends or shortens the window.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.update(*args, **kwargs)
        self._obj = RoleBindingModel.model_validate(self)

    @override
    def apply(self, *args, **kwargs) -> ApplyResult:
        # A window that has ended can't be created again, so a manifest kept
        # in git is skipped instead of failing every apply after its end.
        end = self._obj.spec.not_after
        if end is not None and end <= utcnow():
            return ApplyResult.EXPIRED

        return super().apply(*args, **kwargs)

    @override
    def create_object(self, v2_client: Client, *args, **kwargs) -> Munch | None:
        action, _ = self._plan(v2_client)
        if action != _CREATE:
            # Model.apply continues with update_object.
            raise HttpAlreadyExistsError("role binding already exists")

        try:
            return v2_client.update_role_binding(self._bulk())  # pyright:ignore[reportReturnType]
        except HttpAlreadyExistsError as e:
            # Model.apply retries through update_object; keep the server's
            # reason in case the conflict is with a binding of the other kind.
            self._create_conflict = e
            raise

    @override
    def update_object(self, v2_client: Client, *args, **kwargs) -> Munch | None:
        action, current = self._plan(v2_client)
        if action == _EXISTS:
            # Model.apply reports this as "already exists".
            raise NotImplementedError

        conflict = getattr(self, "_create_conflict", None)
        if action == _CREATE and conflict is not None:
            # Still nothing to replace, so the create's 409 wasn't a race with
            # the same binding; sending it again would get the same 409.
            raise conflict

        old = [current] if action == _REPLACE else []
        return v2_client.update_role_binding(self._bulk(old))  # pyright:ignore[reportReturnType]

    @override
    def delete_object(self, v2_client: Client, *args, **kwargs) -> None:
        spec = self._obj.spec
        for b in self._find(v2_client):
            if same_time(b.spec.not_before, spec.not_before) and same_time(
                b.spec.not_after, spec.not_after
            ):
                _ = v2_client.update_role_binding({"oldBindings": [b], "newBindings": []})
                return

        raise HttpNotFoundError("role binding not found")

    @override
    def list_dependencies(self) -> list[str] | None:
        return self._obj.list_dependencies()

    def _bulk(self, old: list | None = None) -> dict:
        return {"newBindings": [self._obj], "oldBindings": old or []}

    def _find(self, v2_client: Client) -> list[RoleBindingModel]:
        spec = self._obj.spec
        return find_bindings(
            v2_client,
            spec.role_ref.name,
            (spec.subject.kind, spec.subject.name),
            (spec.domain.kind, spec.domain.name),
        )

    def _plan(self, v2_client: Client) -> tuple[str, RoleBindingModel | None]:
        spec = self._obj.spec
        candidates = self._find(v2_client)

        if spec.not_after is None:
            if any(b.spec.not_after is None for b in candidates):
                return _EXISTS, None
            return _CREATE, None

        same_start = [
            b
            for b in candidates
            if b.spec.not_after is not None
            and same_time(b.spec.not_before, spec.not_before)
        ]
        if any(same_time(b.spec.not_after, spec.not_after) for b in same_start):
            return _EXISTS, None

        if len(same_start) > 1:
            start = format_time(spec.not_before) if spec.not_before else "creation"
            ends = ", ".join(format_time(b.spec.not_after) for b in same_start)
            raise Exception(
                f"{len(same_start)} time-bound bindings of {spec.role_ref.name} for "
                f"{spec.subject.kind}:{spec.subject.name} in "
                f"{spec.domain.kind}:{spec.domain.name} start at {start} "
                f"(ends: {ends}); nothing was changed. Remove the extra ones with "
                "'rio role unbind --not-after' and apply again"
            )

        if same_start:
            return _REPLACE, same_start[0]

        return _CREATE, None

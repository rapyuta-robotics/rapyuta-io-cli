# Copyright 2024 Rapyuta Robotics
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
import typing
from threading import Lock

from riocli.utils import Singleton


class SimpleCache(object, metaclass=Singleton):
    def __init__(self):
        super().__init__()
        self._cache = {}
        self._lock = Lock()

    def __enter__(self):
        self._lock.acquire()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._lock.release()

    def get(self, key: typing.Text) -> typing.Any:
        return self._cache.get(key)

    def set(self, key: typing.Text, value: typing.Any) -> None:
        self._cache[key] = value


_cache = SimpleCache()


def get_cache():
    return _cache

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
import json
import os

from munch import Munch, munchify


class StateFile(object):
    _MARKERS = [".git", ".project"]
    _STATE_FILE = ".rio"

    def __init__(self, dir_name: str = os.getcwd()):
        self._dir_name = dir_name
        self.state = self._load_state_file()

    def save(self) -> None:
        file_path = self._search_state_file()
        data = json.dumps(self.state)

        with open(file_path, "w") as state_file:
            state_file.write(data)

    def _load_state_file(self) -> Munch:
        file_path = self._search_state_file()

        if not os.path.exists(file_path):
            return Munch()

        with open(file_path) as state_file:
            data = state_file.read()
            state = json.loads(data)
            return munchify(state)

    def _search_state_file(self) -> str:
        cur_dir = self._dir_name
        cur_file = self._get_state_file_path(cur_dir)

        while True:
            if os.path.exists(cur_file):
                return cur_file

            if cur_dir == "/":
                return self._get_state_file_path(self._dir_name)

            if self._is_top_dir(cur_dir):
                return self._get_state_file_path(cur_dir)

            if not os.path.exists(cur_file):
                if self._is_top_dir(cur_dir):
                    return

            cur_dir = os.path.dirname(cur_dir)
            cur_file = self._get_state_file_path(cur_dir)

    def _is_top_dir(self, dir_name: str) -> bool:
        if dir == "/":
            return True

        for m in self._MARKERS:
            m_path = os.path.join(dir_name, m)
            if os.path.exists(m_path):
                return True

        return False

    def _get_state_file_path(self, dir_name: str) -> str:
        return os.path.join(dir_name, self._STATE_FILE)

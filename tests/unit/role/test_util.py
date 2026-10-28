# Copyright 2026 Rapyuta Robotics
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

from __future__ import annotations

from riocli.role.util import get_subject


def test_user_name_is_lower_cased():
    # The server stores user emails in lower case, so lookups must match.
    assert get_subject("User:Ops@Rapyuta.io") == ("User", "ops@rapyuta.io")


def test_other_subject_names_keep_their_case():
    assert get_subject("ServiceAccount:Deployer") == ("ServiceAccount", "Deployer")
    assert get_subject("UserGroup:RoboOps") == ("UserGroup", "RoboOps")

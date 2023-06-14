# Copyright 2023 Rapyuta Robotics
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

import base64
import json


def mermaid_safe(s: str):
    return s.replace(" ", "_")


def js_string_to_byte(data: str):
    return bytes(data, 'iso-8859-1')


def js_bytes_to_string(data: bytes):
    return data.decode('iso-8859-1')


def js_btoa(data: bytes):
    return base64.b64encode(data)


def mermaid_link(diagram):
    obj = {
        "code": diagram,
        "mermaid": {
            "theme": "default"
        },
        "updateEditor": False,
        "autoSync": True,
        "updateDiagram": False
    }
    json_str = json.dumps(obj)
    json_bytes = js_string_to_byte(json_str)
    encoded_uri = js_btoa(json_bytes)
    return 'https://mermaid.live/view#base64:{}'.format(
        js_bytes_to_string(encoded_uri))

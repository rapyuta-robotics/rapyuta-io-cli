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

from typing import Optional
from base64 import b64encode
from etcd3gw import Etcd3Client


def import_in_etcd(data: dict, endpoint: str, port: Optional[int] = None, prefix: Optional[str] = None) -> None:
    if port is None:
        port = 2379

    cli = Etcd3Client(host=endpoint, port=port)

    if prefix:
        cli.delete_prefix(prefix)
    else:
        _delete_all_keys(client=cli)

    compares, failures = [], []

    for key, val in data.items():
        if prefix:
            key = '{}/{}'.format(prefix, key)

        enc_key = b64encode(str(key).encode('utf-8')).decode()
        enc_val = b64encode(str(val).encode('utf-8')).decode()
        compares.append({
            'key': enc_key,
            'result': 'EQUAL',
            'target': 'VALUE',
            'value': enc_val,
        })
        failures.append({
            'request_put': {
                'key': enc_key,
                'value': enc_val
            }
        })

    txn = {
        'compare': compares,
        'failure': failures,
    }

    cli.transaction(txn)

def _delete_all_keys(client: Etcd3Client) -> None:
    null_char = '\x00'
    enc_null  = b64encode(null_char.encode('utf-8')).decode()

    client.delete('\x00', range_end=enc_null)

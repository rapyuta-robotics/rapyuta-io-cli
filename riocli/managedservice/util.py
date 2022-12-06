# Copyright 2022 Rapyuta Robotics
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
import typing

from rapyuta_io.utils.rest_client import HttpMethod, RestClient

from riocli.config import Configuration


class ManagedServicesClient(object):
    PROD_V2API_URL = "https://api.rapyuta.io"

    def __init__(self):
        super().__init__()
        config = Configuration()
        self.host = config.data.get('v2api_host', self.PROD_V2API_URL)
        self.base_url = "{}/v2/managedservices".format(self.host)

    def list_providers(self):
        url = "{}/providers/".format(self.base_url)
        headers = Configuration().get_auth_header()
        response = RestClient(url).method(
            HttpMethod.GET).headers(headers).execute()
        data = json.loads(response.text)
        if not response.ok:
            err_msg = data.get('error')
            raise Exception("managedservice: {}".format(err_msg))
        return data.get('items', [])

    def list_instances(self):
        url = "{}/".format(self.base_url)
        headers = Configuration().get_auth_header()
        offset = 0
        result = []
        while True:
            response = RestClient(url).method(HttpMethod.GET).query_param({
                "continue": offset,
            }).headers(headers).execute()
            data = json.loads(response.text)
            if not response.ok:
                err_msg = data.get('error')
                raise Exception("managedservice: {}".format(err_msg))
            instances = data.get('items', [])
            if not instances:
                break
            offset = data['metadata']['continue']
            result.extend(instances)

        return sorted(result, key=lambda x: x['metadata']['name'])

    def get_instance(self, instance_name: str) -> typing.Dict:
        url = "{}/{}/".format(self.base_url, instance_name)
        headers = Configuration().get_auth_header()
        response = RestClient(url).method(
            HttpMethod.GET).headers(headers).execute()
        data = json.loads(response.text)
        if not response.ok:
            err_msg = data.get('error')
            raise Exception("managedservice: {}".format(err_msg))
        return data

    def create_instance(self, instance: typing.Any) -> typing.Dict:
        url = "{}/".format(self.base_url)
        headers = Configuration().get_auth_header()

        payload = {
            "metadata": {
                "name": instance.metadata.name,
                "labels": instance.metadata.get("labels", None),
            },
            "spec": {
                "provider": instance.spec.provider,
                "config": instance.spec.get("config", None)
            }
        }

        response = RestClient(url).method(HttpMethod.POST).headers(
            headers).execute(payload=payload)
        data = json.loads(response.text)
        if not response.ok:
            err_msg = data.get('error')
            raise Exception("managedservice: {}".format(err_msg))
        return data

    def delete_instance(self, instance_name):
        url = "{}/{}/".format(self.base_url, instance_name)
        headers = Configuration().get_auth_header()
        response = RestClient(url).method(
            HttpMethod.DELETE).headers(headers).execute()
        data = json.loads(response.text)
        if not response.ok:
            err_msg = data.get('error')
            raise Exception("managedservice: {}".format(err_msg))
        return data

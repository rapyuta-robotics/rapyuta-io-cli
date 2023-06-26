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
import http
import json
import typing

import requests
from munch import munchify, Munch
from rapyuta_io.utils.rest_client import HttpMethod, RestClient


class _Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(
                _Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


def handle_server_errors(response: requests.Response):
    status_code = response.status_code
    # 500 Internal Server Error
    if status_code == http.HTTPStatus.INTERNAL_SERVER_ERROR:
        raise Exception('internal server error')
    # 501 Not Implemented
    if status_code == http.HTTPStatus.NOT_IMPLEMENTED:
        raise Exception('not implemented')
    # 502 Bad Gateway
    if status_code == http.HTTPStatus.BAD_GATEWAY:
        raise Exception('bad gateway')
    # 503 Service Unavailable
    if status_code == http.HTTPStatus.SERVICE_UNAVAILABLE:
        raise Exception('service unavailable')
    # 504 Gateway Timeout
    if status_code == http.HTTPStatus.GATEWAY_TIMEOUT:
        raise Exception('gateway timeout')
    # Anything else that is not known
    if status_code > 504:
        raise Exception('unknown server error')


class Client(metaclass=_Singleton):
    """
    v2 API Client
    """
    PROD_V2API_URL = "https://api.rapyuta.io"

    def __init__(self, config, auth_token: str, project: str = None):
        super().__init__()
        self._config = config
        self._host = config.data.get('v2api_host', self.PROD_V2API_URL)
        self._project = project
        self._token = auth_token

    def _get_auth_token(self) -> typing.Text:
        return "Bearer {}".format(self._token)

    # Project APIs

    def list_projects(
            self,
            organization_guid: str = None,
            query: dict = None
    ) -> Munch:
        """
        List all projects in an organization
        """
        organization_guid = organization_guid or self._config.data.get(
            'organization_id')
        if not organization_guid:
            raise Exception("projects: organization cannot be empty")

        url = "{}/v2/projects/".format(self._host)
        headers = {"Authorization": self._get_auth_token()}

        params = {
            "organizations": organization_guid,
        }

        params.update(query or {})

        offset, result = 0, []
        while True:
            params.update({
                "continue": offset,
                "limit": 500,
            })
            response = RestClient(url).method(HttpMethod.GET).query_param(
                params).headers(headers).execute()
            data = json.loads(response.text)
            if not response.ok:
                err_msg = data.get('error')
                raise Exception("projects: {}".format(err_msg))
            projects = data.get('items', [])
            if not projects:
                break
            offset = data['metadata']['continue']
            result.extend(projects)

        return munchify(result)

    def get_project(self, project_guid: str) -> Munch:
        """
        Get a project by its GUID
        """
        url = "{}/v2/projects/{}/".format(self._host, project_guid)
        headers = self._config.get_auth_header()
        response = RestClient(url).method(
            HttpMethod.GET).headers(headers).execute()

        handle_server_errors(response)

        data = json.loads(response.text)
        if not response.ok:
            err_msg = data.get('error')
            raise Exception("projects: {}".format(err_msg))

        return munchify(data)

    def create_project(self, spec: dict) -> Munch:
        """
        Create a new project
        """
        url = "{}/v2/projects/".format(self._host)
        headers = {"Authorization": self._get_auth_token()}
        response = RestClient(url).method(HttpMethod.POST).headers(
            headers).execute(payload=spec)

        handle_server_errors(response)

        data = json.loads(response.text)
        if not response.ok:
            err_msg = data.get('error')
            raise Exception("projects: {}".format(err_msg))

        return munchify(data)

    def update_project(self, project_guid: str, spec: dict) -> Munch:
        """
        Update an existing project
        """
        url = "{}/v2/projects/{}/".format(self._host, project_guid)
        headers = {"Authorization": self._get_auth_token()}
        response = RestClient(url).method(HttpMethod.PUT).headers(
            headers).execute(payload=spec)

        handle_server_errors(response)

        data = json.loads(response.text)
        if not response.ok:
            err_msg = data.get('error')
            raise Exception("projects: {}".format(err_msg))

        return munchify(data)

    def delete_project(self, project_guid: str) -> Munch:
        """
        Delete a project by its GUID
        """
        url = "{}/v2/projects/{}/".format(self._host, project_guid)
        headers = {"Authorization": self._get_auth_token()}
        response = RestClient(url).method(
            HttpMethod.DELETE).headers(headers).execute()

        handle_server_errors(response)

        data = json.loads(response.text)
        if not response.ok:
            err_msg = data.get('error')
            raise Exception("projects: {}".format(err_msg))

        return munchify(data)

    # ManagedService APIs
    def list_providers(self) -> typing.List:
        """
        List all managedservice provider
        """
        url = "{}/v2/managedservices/providers/".format(self._host)
        headers = self._config.get_auth_header()
        response = RestClient(url).method(
            HttpMethod.GET).headers(headers).execute()

        handle_server_errors(response)

        data = json.loads(response.text)
        if not response.ok:
            err_msg = data.get('error')
            raise Exception("managedservice: {}".format(err_msg))

        return munchify(data.get('items', []))

    def list_instances(self) -> typing.List:
        """
        List all managedservice instances in a project
        """
        url = "{}/v2/managedservices/".format(self._host)
        headers = self._config.get_auth_header()
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

        return munchify(sorted(result, key=lambda x: x['metadata']['name']))

    def get_instance(self, instance_name: str) -> Munch:
        """
        Get a managedservice instance by instance_name
        """
        url = "{}/v2/managedservices/{}/".format(self._host, instance_name)
        headers = self._config.get_auth_header()
        response = RestClient(url).method(
            HttpMethod.GET).headers(headers).execute()

        handle_server_errors(response)

        data = json.loads(response.text)
        if not response.ok:
            err_msg = data.get('error')
            raise Exception("managedservice: {}".format(err_msg))

        return munchify(data)

    def create_instance(self, instance: typing.Dict) -> Munch:
        url = "{}/v2/managedservices/".format(self._host)
        headers = self._config.get_auth_header()

        response = RestClient(url).method(HttpMethod.POST).headers(
            headers).execute(payload=instance)

        handle_server_errors(response)

        data = json.loads(response.text)
        if not response.ok:
            err_msg = data.get('error')
            raise Exception("managedservice: {}".format(err_msg))

        return munchify(data)

    def delete_instance(self, instance_name) -> Munch:
        url = "{}/v2/managedservices/{}/".format(self._host, instance_name)
        headers = self._config.get_auth_header()
        response = RestClient(url).method(
            HttpMethod.DELETE).headers(headers).execute()

        handle_server_errors(response)

        data = json.loads(response.text)
        if not response.ok:
            err_msg = data.get('error')
            raise Exception("managedservice: {}".format(err_msg))

        return munchify(data)

    def create_instance_binding(self, instance_name, binding: dict) -> Munch:
        """
        Create a new managed service instance binding
        """
        url = "{}/v2/managedservices/{}/bindings/".format(
            self._host, instance_name)
        headers = self._config.get_auth_header()
        response = RestClient(url).method(
            HttpMethod.POST).headers(headers).execute(payload=binding)

        handle_server_errors(response)

        data = json.loads(response.text)
        if not response.ok:
            err_msg = data.get('error')
            raise Exception("managedservice: {}".format(err_msg))

        return munchify(data)

    def get_instance_binding(self, instance_name: str, binding_name: str) -> Munch:
        """
        Get a managed service instance binding
        """
        url = "{}/v2/managedservices/{}/bindings/{}/".format(
            self._host, instance_name, binding_name)
        headers = self._config.get_auth_header()
        response = RestClient(url).method(
            HttpMethod.GET).headers(headers).execute()

        handle_server_errors(response)

        data = json.loads(response.text)
        if not response.ok:
            err_msg = data.get('error')
            raise Exception("managedservice: {}".format(err_msg))

        return munchify(data)

    def delete_instance_binding(self, instance_name: str, binding_name: str) -> Munch:
        """
        Delete a managed service instance binding
        """
        url = "{}/v2/managedservices/{}/bindings/{}/".format(
            self._host, instance_name, binding_name)
        headers = self._config.get_auth_header()
        response = RestClient(url).method(
            HttpMethod.DELETE).headers(headers).execute()

        handle_server_errors(response)

        data = json.loads(response.text)
        if not response.ok:
            err_msg = data.get('error')
            raise Exception("managedservice: {}".format(err_msg))

        return munchify(data)

    def list_static_routes(
            self,
            query: dict = None
    ) -> Munch:
        """
        List all static routes in a project
        """
        url = "{}/v2/staticroutes/".format(self._host)
        headers = self._config.get_auth_header()

        params = {}
        params.update(query or {})

        offset, result = 0, []
        while True:
            params.update({
                "continue": offset,
                "limit": 10,
            })
            response = RestClient(url).method(HttpMethod.GET).query_param(
                params).headers(headers).execute()
            data = json.loads(response.text)
            if not response.ok:
                err_msg = data.get('error')
                raise Exception("static routes: {}".format(err_msg))
            staticRoutes = data.get('items', [])
            if not staticRoutes:
                break
            offset = data['metadata']['continue']
            result.extend(staticRoutes)

        return munchify(result)

    def get_static_route(self, name: str) -> Munch:
        """
        Get a static route by its name
        """
        url = "{}/v2/staticroutes/{}/".format(self._host, name)
        headers = self._config.get_auth_header()
        response = RestClient(url).method(
            HttpMethod.GET).headers(headers).execute()

        handle_server_errors(response)

        data = json.loads(response.text)
        if not response.ok:
            err_msg = data.get('error')
            raise Exception("static routes: {}".format(err_msg))

        return munchify(data)

    def create_static_route(self, metadata: dict) -> Munch:
        """
        Create a new static route
        """
        url = "{}/v2/staticroutes/".format(self._host)
        headers = self._config.get_auth_header()
        response = RestClient(url).method(HttpMethod.POST).headers(
            headers).execute(payload=metadata)

        handle_server_errors(response)

        data = json.loads(response.text)
        if not response.ok:
            err_msg = data.get('error')
            raise Exception("static routes: {}".format(err_msg))

        return munchify(data)

    def delete_static_route(self, name: str) -> Munch:
        """
        Delete a static route by its name
        """
        url = "{}/v2/staticroutes/{}/".format(self._host, name)
        headers = self._config.get_auth_header()
        response = RestClient(url).method(
            HttpMethod.DELETE).headers(headers).execute()

        handle_server_errors(response)

        data = json.loads(response.text)
        if not response.ok:
            err_msg = data.get('error')
            raise Exception("static routes: {}".format(err_msg))

        return munchify(data)

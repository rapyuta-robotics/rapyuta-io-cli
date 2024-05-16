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
from __future__ import annotations
import os

import http
import json
import magic
from typing import List, Optional, Dict, Any
from hashlib import md5

import requests
from munch import munchify, Munch
from rapyuta_io.utils.rest_client import HttpMethod, RestClient


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


class Client(object):
    """
    v2 API Client
    """
    PROD_V2API_URL = "https://api.rapyuta.io"

    def __init__(self, config, auth_token: str, project: Optional[str] = None):
        self._config = config
        self._host = config.data.get('v2api_host', self.PROD_V2API_URL)
        self._project = project
        self._token = 'Bearer {}'.format(auth_token)

    def _get_auth_header(self: Client, with_org: bool = False, with_project: bool = True) -> dict:
        headers = dict(Authorization=self._token)

        if with_project and self._project is not None:
            headers['project'] = self._project

        if with_org:
            headers['organizationguid'] = self._config.organization_guid

        return headers

    # Project APIs

    def list_projects(
            self,
            organization_guid: str = None,
            query: dict = None
    ) -> Munch:
        """
        List all projects in an organization
        """

        url = "{}/v2/projects/".format(self._host)
        headers = self._get_auth_header(with_project=False)

        params = {}

        if organization_guid:
            params.update({
                "organizations": organization_guid,
            })

        params.update(query or {})

        client = RestClient(url).method(HttpMethod.GET).headers(headers)
        return self._walk_pages(client, params=params)

    def get_project(self, project_guid: str) -> Munch:
        """
        Get a project by its GUID
        """
        url = "{}/v2/projects/{}/".format(self._host, project_guid)
        headers = self._get_auth_header()
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
        headers = self._get_auth_header(with_project=False)
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
        headers = self._get_auth_header(with_project=False)
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
        headers = self._get_auth_header(with_project=False)
        response = RestClient(url).method(
            HttpMethod.DELETE).headers(headers).execute()

        handle_server_errors(response)

        data = json.loads(response.text)
        if not response.ok:
            err_msg = data.get('error')
            raise Exception("projects: {}".format(err_msg))

        return munchify(data)

    # ManagedService APIs
    def list_providers(self) -> List:
        """
        List all managedservice provider
        """
        url = "{}/v2/managedservices/providers/".format(self._host)
        headers = self._get_auth_header(with_project=False)
        response = RestClient(url).method(
            HttpMethod.GET).headers(headers).execute()

        handle_server_errors(response)

        data = json.loads(response.text)
        if not response.ok:
            err_msg = data.get('error')
            raise Exception("managedservice: {}".format(err_msg))

        return munchify(data.get('items', []))

    def list_instances(self) -> List:
        """
        List all managedservice instances in a project
        """
        url = "{}/v2/managedservices/".format(self._host)
        headers = self._get_auth_header()

        client = RestClient(url).method(HttpMethod.GET).headers(headers)
        return self._walk_pages(client)

    def get_instance(self, instance_name: str) -> Munch:
        """
        Get a managedservice instance by instance_name
        """
        url = "{}/v2/managedservices/{}/".format(self._host, instance_name)
        headers = self._get_auth_header()
        response = RestClient(url).method(
            HttpMethod.GET).headers(headers).execute()

        handle_server_errors(response)

        data = json.loads(response.text)
        if not response.ok:
            err_msg = data.get('error')
            raise Exception("managedservice: {}".format(err_msg))

        return munchify(data)

    def create_instance(self, instance: Dict) -> Munch:
        url = "{}/v2/managedservices/".format(self._host)
        headers = self._get_auth_header()

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
        headers = self._get_auth_header()
        response = RestClient(url).method(
            HttpMethod.DELETE).headers(headers).execute()

        handle_server_errors(response)

        data = json.loads(response.text)
        if not response.ok:
            err_msg = data.get('error')
            raise Exception("managedservice: {}".format(err_msg))

        return munchify(data)

    def list_instance_bindings(self, instance_name: str, labels: str = '') -> List:
        """
        List all managedservice instances in a project
        """
        url = "{}/v2/managedservices/{}/bindings/".format(self._host, instance_name)
        headers = self._get_auth_header()

        client = RestClient(url).method(HttpMethod.GET).headers(headers)
        return self._walk_pages(client, params={'labelSelector': labels})


    def create_instance_binding(self, instance_name, binding: dict) -> Munch:
        """
        Create a new managed service instance binding
        """
        url = "{}/v2/managedservices/{}/bindings/".format(
            self._host, instance_name)
        headers = self._get_auth_header()
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
        headers = self._get_auth_header()
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
        headers = self._get_auth_header()
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
        headers = self._get_auth_header()

        params = {}
        params.update(query or {})

        client = RestClient(url).method(HttpMethod.GET).headers(headers)
        return self._walk_pages(client, params=params)

    def get_static_route(self, name: str) -> Munch:
        """
        Get a static route by its name
        """
        url = "{}/v2/staticroutes/{}/".format(self._host, name)
        headers = self._get_auth_header()
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
        headers = self._get_auth_header()
        response = RestClient(url).method(HttpMethod.POST).headers(
            headers).execute(payload=metadata)

        handle_server_errors(response)

        data = json.loads(response.text)
        if not response.ok:
            err_msg = data.get('error')
            raise Exception("static routes: {}".format(err_msg))

        return munchify(data)

    def update_static_route(self, name: str, sr: dict) -> Munch:
        """
        Update the new static route
        """
        url = "{}/v2/staticroutes/{}/".format(self._host, name)
        headers = self._get_auth_header()
        response = RestClient(url).method(HttpMethod.PUT).headers(
            headers).execute(payload=sr)

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
        headers = self._get_auth_header()
        response = RestClient(url).method(
            HttpMethod.DELETE).headers(headers).execute()

        handle_server_errors(response)

        data = json.loads(response.text)
        if not response.ok:
            err_msg = data.get('error')
            raise Exception("static routes: {}".format(err_msg))

        return munchify(data)

    def create_secret(self, payload: dict) -> Munch:
        """
        Create a new secret
        """
        url = "{}/v2/secrets/".format(self._host)
        headers = self._get_auth_header()
        response = RestClient(url).method(HttpMethod.POST).headers(
            headers).execute(payload=payload)
        handle_server_errors(response)

        data = json.loads(response.text)
        if not response.ok:
            err_msg = data.get('error')
            raise Exception("secret: {}".format(err_msg))

        return munchify(data)

    def delete_secret(self, secret_name: str) -> Munch:
        """
        Delete a secret
        """
        url = "{}/v2/secrets/{}/".format(self._host, secret_name)
        headers = self._get_auth_header()
        response = RestClient(url).method(HttpMethod.DELETE).headers(
            headers).execute()
        handle_server_errors(response)

        data = json.loads(response.text)
        if not response.ok:
            err_msg = data.get('error')
            raise Exception("secret: {}".format(err_msg))

        return munchify(data)

    def list_secrets(
            self,
            query: dict = None
    ) -> Munch:
        """
        List all secrets in a project
        """
        url = "{}/v2/secrets/".format(self._host)
        headers = self._get_auth_header()

        params = {}
        params.update(query or {})

        client = RestClient(url).method(HttpMethod.GET).headers(headers)
        return self._walk_pages(client, params=params)

    def get_secret(
            self,
            secret_name: str
    ) -> Munch:
        """
        Get secret by name
        """
        url = "{}/v2/secrets/{}/".format(self._host, secret_name)
        headers = self._get_auth_header()

        response = RestClient(url).method(HttpMethod.GET).headers(headers).execute()
        data = json.loads(response.text)
        if not response.ok:
            err_msg = data.get('error')
            raise Exception("secrets: {}".format(err_msg))

        return munchify(data)

    def update_secret(self, secret_name: str, spec: dict) -> Munch:
        """
        Update a secret
        """
        url = "{}/v2/secrets/{}/".format(self._host, secret_name)
        headers = self._get_auth_header()
        response = RestClient(url).method(HttpMethod.PUT).headers(
            headers).execute(payload=spec)
        handle_server_errors(response)

        data = json.loads(response.text)
        if not response.ok:
            err_msg = data.get('error')
            raise Exception("secret: {}".format(err_msg))

        return munchify(data)

    # ConfigTrees APIs
    def list_config_trees(self) -> Munch:
        url = "{}/v2/configtrees/".format(self._host)
        headers = self._get_auth_header(with_org=True)
        client = RestClient(url).method(HttpMethod.GET).headers(headers)
        return self._walk_pages(client)

    def create_config_tree(self, tree_spec: dict) -> Munch:
        url = "{}/v2/configtrees/".format(self._host)
        headers = self._get_auth_header(with_org=True)
        response = RestClient(url).method(HttpMethod.POST).headers(
            headers).execute(payload=tree_spec)
        handle_server_errors(response)

        data = json.loads(response.text)
        if not response.ok:
            err_msg = data.get('error')
            raise Exception("configtree: {}".format(err_msg))

        return munchify(data)

    def delete_config_tree(self, tree_name: str) -> Munch:
        url = "{}/v2/configtrees/{}/".format(self._host, tree_name)
        headers = self._get_auth_header(with_org=True)
        response = RestClient(url).method(HttpMethod.DELETE).headers(
            headers).execute()
        handle_server_errors(response)

        data = json.loads(response.text)
        if not response.ok:
            err_msg = data.get('error')
            raise Exception("configtree: {}".format(err_msg))

        return munchify(data)

    def get_config_tree(self, tree_name: str, rev_id: Optional[str] = None,
                               include_data: bool = False, filter_content_types: Optional[List[str]] = None,
                               filter_prefixes: Optional[List[str]] = None) -> Munch:
        url = "{}/v2/configtrees/{}/".format(self._host, tree_name)
        query = {
            'includeData': include_data,
            'contentTypes': filter_content_types,
            'keyPrefixes': filter_prefixes,
            'revision': rev_id,
        }
        headers = self._get_auth_header(with_org=True)
        response = RestClient(url).method(HttpMethod.GET).headers(
            headers).query_param(query).execute()
        handle_server_errors(response)

        data = json.loads(response.text)
        if not response.ok:
            err_msg = data.get('error')
            raise Exception("configtree: {}".format(err_msg))

        return munchify(data)

    def set_revision_config_tree(self, tree_name: str, spec: dict) -> Munch:
        url = "{}/v2/configtrees/{}/".format(self._host, tree_name)
        headers = self._get_auth_header(with_org=True)
        response = RestClient(url).method(HttpMethod.PUT).headers(
            headers).execute(payload=spec)
        handle_server_errors(response)

        data = json.loads(response.text)
        if not response.ok:
            err_msg = data.get('error')
            raise Exception("configtree: {}".format(err_msg))

        return munchify(data)

    def list_config_tree_revisions(self, tree_name: str) -> Munch:
        url = "{}/v2/configtrees/{}/revisions/".format(self._host, tree_name)
        headers = self._get_auth_header(with_org=True)
        client = RestClient(url).method(HttpMethod.GET).headers(headers)
        return self._walk_pages(client)

    def initialize_config_tree_revision(self, tree_name: str) -> Munch:
        url = "{}/v2/configtrees/{}/revisions/".format(self._host, tree_name)
        headers = self._get_auth_header(with_org=True)
        response = RestClient(url).method(HttpMethod.POST).headers(
            headers).execute()
        handle_server_errors(response)

        data = json.loads(response.text)
        if not response.ok:
            err_msg = data.get('error')
            raise Exception("configtree: {}".format(err_msg))

        return munchify(data)

    def commit_config_tree_revision(self, tree_name: str, rev_id: str, payload: dict) -> Munch:
        url = "{}/v2/configtrees/{}/revisions/{}/".format(self._host, tree_name, rev_id)
        headers = self._get_auth_header(with_org=True)
        response = RestClient(url).method(HttpMethod.PATCH).headers(
            headers).execute(payload=payload)
        handle_server_errors(response)

        data = json.loads(response.text)
        if not response.ok:
            err_msg = data.get('error')
            raise Exception("configtree: {}".format(err_msg))

        return munchify(data)

    def store_keys_in_revision(self, tree_name: str, rev_id: str, payload: Any) -> Munch:
        url = "{}/v2/configtrees/{}/revisions/{}/".format(self._host, tree_name, rev_id)
        headers = self._get_auth_header(with_org=True)
        response = RestClient(url).method(HttpMethod.PUT).headers(
            headers).execute(payload=payload)
        handle_server_errors(response)

        data = json.loads(response.text)
        if not response.ok:
            err_msg = data.get('error')
            raise Exception("configtree: {}".format(err_msg))

        return munchify(data)


    def store_key_in_revision(self, tree_name: str, rev_id: str, key: str, value: str, perms: int = 644) -> Munch:
        url = "{}/v2/configtrees/{}/revisions/{}/{}".format(self._host, tree_name, rev_id, key)
        headers = self._get_auth_header(with_org=True)
        headers['Content-Type'] = 'kv'
        headers['X-Checksum'] = md5(str(value).encode('utf-8')).hexdigest()
        headers['X-Permissions'] = str(perms)

        response = RestClient(url).method(HttpMethod.PUT).headers(
            headers).execute(value)
        handle_server_errors(response)

        data = json.loads(response.text)
        if not response.ok:
            err_msg = data.get('error')
            raise Exception("configtree: {}".format(err_msg))

        return munchify(data)

    def store_file_in_revision(self, tree_name: str, rev_id: str, key: str, file_path: str) -> Munch:
        stat = os.stat(file_path)
        perms = oct(stat.st_mode & 0o777)[-3:]

        content_type = magic.from_file(file_path, mime=True)

        url = "{}/v2/configtrees/{}/revisions/{}/{}".format(self._host, tree_name, rev_id, key)
        headers = self._get_auth_header(with_org=True)
        headers['Content-Type'] = content_type
        headers['X-Permissions'] = perms

        with open(file_path, 'rb') as f:
            file_hash = md5()
            chunk = f.read(8192)
            while chunk:
                file_hash.update(chunk)
                chunk = f.read(8192)

            headers['X-Checksum'] = file_hash.hexdigest()
            f.seek(0)

            response = RestClient(url).method(HttpMethod.PUT).headers(headers).execute(payload=f, raw=True)
            handle_server_errors(response)

        data = json.loads(response.text)
        if not response.ok:
            err_msg = data.get('error')
            raise Exception("configtree: {}".format(err_msg))

        return munchify(data)

    def delete_key_in_revision(self, tree_name: str, rev_id: str, key: str) -> Munch:
        url = "{}/v2/configtrees/{}/revisions/{}/{}".format(self._host, tree_name, rev_id, key)
        headers = self._get_auth_header(with_org=True)
        response = RestClient(url).method(HttpMethod.DELETE).headers(headers).execute()
        handle_server_errors(response)

        data = json.loads(response.text)
        if not response.ok:
            err_msg = data.get('error')
            raise Exception("configtree: {}".format(err_msg))

        return munchify(data)

    def _walk_pages(self, c: RestClient, params: dict = {}, limit: Optional[int] = None) -> Munch:
        offset, result = 0, []

        if limit is not None:
            params["limit"] = limit

        while True:
            params["continue"] = offset

            response = c.query_param(params).execute()
            data = json.loads(response.text)
            if not response.ok:
                err_msg = data.get('error')
                raise Exception("listing: {}".format(err_msg))

            items = data.get('items', [])
            if not items:
                break

            offset = data['metadata']['continue']
            result.extend(items)

        return munchify(result)

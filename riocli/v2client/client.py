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
from __future__ import annotations

import json
import os
import time
from hashlib import md5
from typing import Any, Dict, List, Optional, Sequence

import magic
from munch import Munch, munchify
from rapyuta_io.utils.rest_client import HttpMethod, RestClient

from riocli.v2client.enums import DeploymentPhaseConstants, DiskStatusConstants
from riocli.v2client.error import DeploymentNotRunning, ImagePullError, RetriesExhausted
from riocli.v2client.util import handle_server_errors, process_errors


class Client(object):
    """
    v2 API Client
    """

    PROD_V2API_URL = "https://api.rapyuta.io"

    def __init__(self, config, auth_token: str, project: Optional[str] = None):
        self._config = config
        self._host = config.data.get("v2api_host", self.PROD_V2API_URL)
        self._project = project
        self._token = "Bearer {}".format(auth_token)

    def _get_auth_header(
        self: Client,
        with_organization: bool = True,
        with_project: bool = True,
        organization_guid: Optional[str] = None,
    ) -> dict:
        headers = dict(Authorization=self._token)

        if with_organization:
            headers["organizationguid"] = (
                organization_guid or self._config.organization_guid
            )

        if with_project and self._project is not None:
            headers["project"] = self._project

        custom_client_request_id = os.getenv("REQUEST_ID")
        if custom_client_request_id:
            headers["X-Request-ID"] = custom_client_request_id

        return headers

    # Project APIs

    def list_projects(
        self,
        organization_guid: Optional[str] = None,
        query: Optional[dict] = None,
    ) -> Munch:
        """
        List all projects in an organization or where user have the access to in all organizations.
        """

        url = "{}/v2/projects/".format(self._host)
        headers = self._get_auth_header(with_project=False, with_organization=False)

        params = {}

        if organization_guid:
            params.update(
                {
                    "organizations": organization_guid,
                }
            )

        params.update(query or {})

        client = RestClient(url).method(HttpMethod.GET).headers(headers)
        return self._walk_pages(client, params=params)

    def get_project(self, project_guid: str) -> Munch:
        """
        Get a project by its GUID
        """
        url = "{}/v2/projects/{}/".format(self._host, project_guid)
        headers = self._get_auth_header(with_organization=False)
        response = RestClient(url).method(HttpMethod.GET).headers(headers).execute()

        handle_server_errors(response)

        data = json.loads(response.text)
        if not response.ok:
            err_msg = data.get("error")
            raise Exception("projects: {}".format(err_msg))

        return munchify(data)

    def create_project(self, spec: dict) -> Munch:
        """
        Create a new project
        """
        url = "{}/v2/projects/".format(self._host)
        headers = self._get_auth_header(with_project=False)

        # Set the organizationguid header
        if spec["metadata"].get("organizationGUID"):
            headers["organizationguid"] = spec["metadata"].get("organizationGUID")

        response = (
            RestClient(url).method(HttpMethod.POST).headers(headers).execute(payload=spec)
        )

        handle_server_errors(response)

        data = json.loads(response.text)
        if not response.ok:
            err_msg = data.get("error")
            raise Exception("projects: {}".format(err_msg))

        return munchify(data)

    def update_project(self, project_guid: str, spec: dict) -> Munch:
        """
        Update an existing project
        """
        url = "{}/v2/projects/{}/".format(self._host, project_guid)
        headers = self._get_auth_header(with_project=False)
        response = (
            RestClient(url).method(HttpMethod.PUT).headers(headers).execute(payload=spec)
        )

        handle_server_errors(response)

        data = json.loads(response.text)
        if not response.ok:
            err_msg = data.get("error")
            raise Exception("projects: {}".format(err_msg))

        return munchify(data)

    def update_project_owner(self, project_guid: str, new_owner_guid: str) -> Munch:
        """
        Update an existing project's owner (creator)
        """
        url = "{}/v2/projects/{}/owner/".format(self._host, project_guid)
        headers = self._get_auth_header(with_project=False)
        response = (
            RestClient(url)
            .method(HttpMethod.PUT)
            .headers(headers)
            .execute(payload={"metadata": {"creatorGUID": new_owner_guid}})
        )

        handle_server_errors(response)

        data = json.loads(response.text)
        if not response.ok:
            err_msg = data.get("error")
            raise Exception("projects: {}".format(err_msg))

        return munchify(data)

    def delete_project(self, project_guid: str) -> Munch:
        """
        Delete a project by its GUID
        """
        url = "{}/v2/projects/{}/".format(self._host, project_guid)
        headers = self._get_auth_header(with_project=False)
        response = RestClient(url).method(HttpMethod.DELETE).headers(headers).execute()

        handle_server_errors(response)

        data = json.loads(response.text)
        if not response.ok:
            err_msg = data.get("error")
            raise Exception("projects: {}".format(err_msg))

        return munchify(data)

    # Organization APIs
    def get_organization(self, organization_guid: str) -> Munch:
        """
        Get an organization by its GUID
        """
        url = "{}/v2/organizations/{}/".format(self._host, organization_guid)
        headers = self._get_auth_header(
            with_project=False, organization_guid=organization_guid
        )
        response = RestClient(url).method(HttpMethod.GET).headers(headers).execute()

        handle_server_errors(response)

        data = json.loads(response.text)
        if not response.ok:
            err_msg = data.get("error")
            raise Exception("organizations: {}".format(err_msg))

        return munchify(data)

    def update_organization(self, organization_guid: str, data: dict) -> Munch:
        """
        Update an organization
        """
        url = "{}/v2/organizations/{}/".format(self._host, organization_guid)
        headers = self._get_auth_header(
            with_project=False, organization_guid=organization_guid
        )
        response = (
            RestClient(url).method(HttpMethod.PUT).headers(headers).execute(payload=data)
        )

        handle_server_errors(response)

        data = json.loads(response.text)
        if not response.ok:
            err_msg = data.get("error")
            raise Exception("{}".format(err_msg))

        return munchify(data)

    # Users APIs
    def get_user(self) -> Munch:
        url = "{}/v2/users/me/".format(self._host)
        headers = self._get_auth_header(with_project=False, with_organization=False)
        response = RestClient(url).method(HttpMethod.GET).headers(headers).execute()

        handle_server_errors(response)

        data = json.loads(response.text)
        if not response.ok:
            err_msg = data.get("error")
            raise Exception("users: {}".format(err_msg))

        return munchify(data)

    # ManagedService APIs
    def list_providers(self) -> List:
        """
        List all managedservice provider
        """
        url = "{}/v2/managedservices/providers/".format(self._host)
        headers = self._get_auth_header(with_project=False)
        response = RestClient(url).method(HttpMethod.GET).headers(headers).execute()

        handle_server_errors(response)

        data = json.loads(response.text)
        if not response.ok:
            err_msg = data.get("error")
            raise Exception("managedservice: {}".format(err_msg))

        return munchify(data.get("items", []))

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
        response = RestClient(url).method(HttpMethod.GET).headers(headers).execute()

        handle_server_errors(response)

        data = json.loads(response.text)
        if not response.ok:
            err_msg = data.get("error")
            raise Exception("managedservice: {}".format(err_msg))

        return munchify(data)

    def create_instance(self, instance: Dict) -> Munch:
        url = "{}/v2/managedservices/".format(self._host)
        headers = self._get_auth_header()

        response = (
            RestClient(url)
            .method(HttpMethod.POST)
            .headers(headers)
            .execute(payload=instance)
        )

        handle_server_errors(response)

        data = json.loads(response.text)
        if not response.ok:
            err_msg = data.get("error")
            raise Exception("managedservice: {}".format(err_msg))

        return munchify(data)

    def delete_instance(self, instance_name) -> Munch:
        url = "{}/v2/managedservices/{}/".format(self._host, instance_name)
        headers = self._get_auth_header()
        response = RestClient(url).method(HttpMethod.DELETE).headers(headers).execute()

        handle_server_errors(response)

        data = json.loads(response.text)
        if not response.ok:
            err_msg = data.get("error")
            raise Exception("managedservice: {}".format(err_msg))

        return munchify(data)

    def list_instance_bindings(self, instance_name: str, labels: str = "") -> List:
        """
        List all managedservice instances in a project
        """
        url = "{}/v2/managedservices/{}/bindings/".format(self._host, instance_name)
        headers = self._get_auth_header()

        client = RestClient(url).method(HttpMethod.GET).headers(headers)
        return self._walk_pages(client, params={"labelSelector": labels})

    def create_instance_binding(self, instance_name, binding: dict) -> Munch:
        """
        Create a new managed service instance binding
        """
        url = "{}/v2/managedservices/{}/bindings/".format(self._host, instance_name)
        headers = self._get_auth_header()
        response = (
            RestClient(url)
            .method(HttpMethod.POST)
            .headers(headers)
            .execute(payload=binding)
        )

        handle_server_errors(response)

        data = json.loads(response.text)
        if not response.ok:
            err_msg = data.get("error")
            raise Exception("managedservice: {}".format(err_msg))

        return munchify(data)

    def get_instance_binding(self, instance_name: str, binding_name: str) -> Munch:
        """
        Get a managed service instance binding
        """
        url = "{}/v2/managedservices/{}/bindings/{}/".format(
            self._host, instance_name, binding_name
        )
        headers = self._get_auth_header()
        response = RestClient(url).method(HttpMethod.GET).headers(headers).execute()

        handle_server_errors(response)

        data = json.loads(response.text)
        if not response.ok:
            err_msg = data.get("error")
            raise Exception("managedservice: {}".format(err_msg))

        return munchify(data)

    def delete_instance_binding(self, instance_name: str, binding_name: str) -> Munch:
        """
        Delete a managed service instance binding
        """
        url = "{}/v2/managedservices/{}/bindings/{}/".format(
            self._host, instance_name, binding_name
        )
        headers = self._get_auth_header()
        response = RestClient(url).method(HttpMethod.DELETE).headers(headers).execute()

        handle_server_errors(response)

        data = json.loads(response.text)
        if not response.ok:
            err_msg = data.get("error")
            raise Exception("managedservice: {}".format(err_msg))

        return munchify(data)

    def list_static_routes(self, query: dict = None) -> Munch:
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
        response = RestClient(url).method(HttpMethod.GET).headers(headers).execute()

        handle_server_errors(response)

        data = json.loads(response.text)
        if not response.ok:
            err_msg = data.get("error")
            raise Exception("static routes: {}".format(err_msg))

        return munchify(data)

    def create_static_route(self, metadata: dict) -> Munch:
        """
        Create a new static route
        """
        url = "{}/v2/staticroutes/".format(self._host)
        headers = self._get_auth_header()
        response = (
            RestClient(url)
            .method(HttpMethod.POST)
            .headers(headers)
            .execute(payload=metadata)
        )

        handle_server_errors(response)

        data = json.loads(response.text)
        if not response.ok:
            err_msg = data.get("error")
            raise Exception("static routes: {}".format(err_msg))

        return munchify(data)

    def update_static_route(self, name: str, sr: dict) -> Munch:
        """
        Update the new static route
        """
        url = "{}/v2/staticroutes/{}/".format(self._host, name)
        headers = self._get_auth_header()
        response = (
            RestClient(url).method(HttpMethod.PUT).headers(headers).execute(payload=sr)
        )

        handle_server_errors(response)

        data = json.loads(response.text)
        if not response.ok:
            err_msg = data.get("error")
            raise Exception("static routes: {}".format(err_msg))

        return munchify(data)

    def delete_static_route(self, name: str) -> Munch:
        """
        Delete a static route by its name
        """
        url = "{}/v2/staticroutes/{}/".format(self._host, name)
        headers = self._get_auth_header()
        response = RestClient(url).method(HttpMethod.DELETE).headers(headers).execute()

        handle_server_errors(response)

        data = json.loads(response.text)
        if not response.ok:
            err_msg = data.get("error")
            raise Exception("static routes: {}".format(err_msg))

        return munchify(data)

    def create_secret(self, payload: dict) -> Munch:
        """
        Create a new secret
        """
        url = "{}/v2/secrets/".format(self._host)
        headers = self._get_auth_header()
        response = (
            RestClient(url)
            .method(HttpMethod.POST)
            .headers(headers)
            .execute(payload=payload)
        )
        handle_server_errors(response)

        data = json.loads(response.text)
        if not response.ok:
            err_msg = data.get("error")
            raise Exception("secret: {}".format(err_msg))

        return munchify(data)

    def delete_secret(self, secret_name: str) -> Munch:
        """
        Delete a secret
        """
        url = "{}/v2/secrets/{}/".format(self._host, secret_name)
        headers = self._get_auth_header()
        response = RestClient(url).method(HttpMethod.DELETE).headers(headers).execute()
        handle_server_errors(response)

        data = json.loads(response.text)
        if not response.ok:
            err_msg = data.get("error")
            raise Exception("secret: {}".format(err_msg))

        return munchify(data)

    def list_secrets(self, query: dict = None) -> Munch:
        """
        List all secrets in a project
        """
        url = "{}/v2/secrets/".format(self._host)
        headers = self._get_auth_header()

        params = {}
        params.update(query or {})

        client = RestClient(url).method(HttpMethod.GET).headers(headers)
        return self._walk_pages(client, params=params)

    def get_secret(self, secret_name: str) -> Munch:
        """
        Get secret by name
        """
        url = "{}/v2/secrets/{}/".format(self._host, secret_name)
        headers = self._get_auth_header()

        response = RestClient(url).method(HttpMethod.GET).headers(headers).execute()
        data = json.loads(response.text)
        if not response.ok:
            err_msg = data.get("error")
            raise Exception("secrets: {}".format(err_msg))

        return munchify(data)

    def update_secret(self, secret_name: str, spec: dict) -> Munch:
        """
        Update a secret
        """
        url = "{}/v2/secrets/{}/".format(self._host, secret_name)
        headers = self._get_auth_header()
        response = (
            RestClient(url).method(HttpMethod.PUT).headers(headers).execute(payload=spec)
        )
        handle_server_errors(response)

        data = json.loads(response.text)
        if not response.ok:
            err_msg = data.get("error")
            raise Exception("secret: {}".format(err_msg))

        return munchify(data)

    # ConfigTrees APIs
    def list_config_trees(self) -> Munch:
        url = "{}/v2/configtrees/".format(self._host)
        headers = self._get_auth_header()
        client = RestClient(url).method(HttpMethod.GET).headers(headers)
        return self._walk_pages(client)

    def create_config_tree(self, tree_spec: dict) -> Munch:
        url = "{}/v2/configtrees/".format(self._host)
        headers = self._get_auth_header()
        response = (
            RestClient(url)
            .method(HttpMethod.POST)
            .headers(headers)
            .execute(payload=tree_spec)
        )
        handle_server_errors(response)

        data = json.loads(response.text)
        if not response.ok:
            err_msg = data.get("error")
            raise Exception("configtree: {}".format(err_msg))

        return munchify(data)

    def delete_config_tree(self, tree_name: str) -> Munch:
        url = "{}/v2/configtrees/{}/".format(self._host, tree_name)
        headers = self._get_auth_header()
        response = RestClient(url).method(HttpMethod.DELETE).headers(headers).execute()
        handle_server_errors(response)

        data = json.loads(response.text)
        if not response.ok:
            err_msg = data.get("error")
            raise Exception("configtree: {}".format(err_msg))

        return munchify(data)

    def get_config_tree(
        self,
        tree_name: str,
        rev_id: Optional[str] = None,
        include_data: bool = False,
        filter_content_types: Optional[List[str]] = None,
        filter_prefixes: Optional[List[str]] = None,
    ) -> Munch:
        url = "{}/v2/configtrees/{}/".format(self._host, tree_name)
        query = {
            "includeData": include_data,
            "contentTypes": filter_content_types,
            "keyPrefixes": filter_prefixes,
            "revision": rev_id,
        }
        headers = self._get_auth_header()
        response = (
            RestClient(url)
            .method(HttpMethod.GET)
            .headers(headers)
            .query_param(query)
            .execute()
        )
        handle_server_errors(response)

        data = json.loads(response.text)
        if not response.ok:
            err_msg = data.get("error")
            raise Exception("configtree: {}".format(err_msg))

        return munchify(data)

    def set_revision_config_tree(self, tree_name: str, spec: dict) -> Munch:
        url = "{}/v2/configtrees/{}/".format(self._host, tree_name)
        headers = self._get_auth_header()
        response = (
            RestClient(url).method(HttpMethod.PUT).headers(headers).execute(payload=spec)
        )
        handle_server_errors(response)

        data = json.loads(response.text)
        if not response.ok:
            err_msg = data.get("error")
            raise Exception("configtree: {}".format(err_msg))

        return munchify(data)

    def list_config_tree_revisions(self, tree_name: str, labels: str = "") -> Munch:
        url = "{}/v2/configtrees/{}/revisions/".format(self._host, tree_name)
        headers = self._get_auth_header()
        client = RestClient(url).method(HttpMethod.GET).headers(headers)
        return self._walk_pages(client, params={"labelSelector": labels})

    def initialize_config_tree_revision(self, tree_name: str) -> Munch:
        url = "{}/v2/configtrees/{}/revisions/".format(self._host, tree_name)
        headers = self._get_auth_header()
        response = RestClient(url).method(HttpMethod.POST).headers(headers).execute()
        handle_server_errors(response)

        data = json.loads(response.text)
        if not response.ok:
            err_msg = data.get("error")
            raise Exception("configtree: {}".format(err_msg))

        return munchify(data)

    def commit_config_tree_revision(
        self, tree_name: str, rev_id: str, payload: dict
    ) -> Munch:
        url = "{}/v2/configtrees/{}/revisions/{}/".format(self._host, tree_name, rev_id)
        headers = self._get_auth_header()
        response = (
            RestClient(url)
            .method(HttpMethod.PATCH)
            .headers(headers)
            .execute(payload=payload)
        )
        handle_server_errors(response)

        data = json.loads(response.text)
        if not response.ok:
            err_msg = data.get("error")
            raise Exception("configtree: {}".format(err_msg))

        return munchify(data)

    def store_keys_in_revision(self, tree_name: str, rev_id: str, payload: Any) -> Munch:
        url = "{}/v2/configtrees/{}/revisions/{}/".format(self._host, tree_name, rev_id)
        headers = self._get_auth_header()
        response = (
            RestClient(url)
            .method(HttpMethod.PUT)
            .headers(headers)
            .execute(payload=payload)
        )
        handle_server_errors(response)

        data = json.loads(response.text)
        if not response.ok:
            err_msg = data.get("error")
            raise Exception("configtree: {}".format(err_msg))

        return munchify(data)

    def store_key_in_revision(
        self, tree_name: str, rev_id: str, key: str, value: str, perms: int = 644
    ) -> Munch:
        url = "{}/v2/configtrees/{}/revisions/{}/{}".format(
            self._host, tree_name, rev_id, key
        )
        headers = self._get_auth_header()
        headers["Content-Type"] = "kv"
        headers["X-Checksum"] = md5(str(value).encode("utf-8")).hexdigest()
        headers["X-Permissions"] = str(perms)

        response = RestClient(url).method(HttpMethod.PUT).headers(headers).execute(value)
        handle_server_errors(response)

        data = json.loads(response.text)
        if not response.ok:
            err_msg = data.get("error")
            raise Exception("configtree: {}".format(err_msg))

        return munchify(data)

    def store_file_in_revision(
        self, tree_name: str, rev_id: str, key: str, file_path: str
    ) -> Munch:
        stat = os.stat(file_path)
        perms = oct(stat.st_mode & 0o777)[-3:]

        content_type = magic.from_file(file_path, mime=True)

        url = "{}/v2/configtrees/{}/revisions/{}/{}".format(
            self._host, tree_name, rev_id, key
        )
        headers = self._get_auth_header()
        headers["Content-Type"] = content_type
        headers["X-Permissions"] = perms

        with open(file_path, "rb") as f:
            file_hash = md5()
            chunk = f.read(8192)
            while chunk:
                file_hash.update(chunk)
                chunk = f.read(8192)

            headers["X-Checksum"] = file_hash.hexdigest()
            f.seek(0)

            response = (
                RestClient(url)
                .method(HttpMethod.PUT)
                .headers(headers)
                .execute(payload=f, raw=True)
            )
            handle_server_errors(response)

        data = json.loads(response.text)
        if not response.ok:
            err_msg = data.get("error")
            raise Exception("configtree: {}".format(err_msg))

        return munchify(data)

    def delete_key_in_revision(self, tree_name: str, rev_id: str, key: str) -> Munch:
        url = "{}/v2/configtrees/{}/revisions/{}/{}".format(
            self._host, tree_name, rev_id, key
        )
        headers = self._get_auth_header()
        response = RestClient(url).method(HttpMethod.DELETE).headers(headers).execute()
        handle_server_errors(response)

        data = json.loads(response.text)
        if not response.ok:
            err_msg = data.get("error")
            raise Exception("configtree: {}".format(err_msg))

        return munchify(data)

    def _walk_pages(
        self, c: RestClient, params: dict = None, limit: Optional[int] = None
    ) -> Munch:
        offset, result = 0, []

        params = params or {}

        if limit is not None:
            params["limit"] = limit

        while True:
            params["continue"] = offset

            response = c.query_param(params).execute()
            data = response.json()
            if not response.ok:
                err_msg = data.get("error")
                raise Exception("listing: {}".format(err_msg))

            items = data.get("items", [])
            if not items:
                break

            offset = data["metadata"]["continue"]
            result.extend(items)

        return munchify(result)

    def list_packages(self, query: dict = None) -> Munch:
        """
        List all packages in a project
        """
        url = "{}/v2/packages/".format(self._host)
        headers = self._get_auth_header()

        client = RestClient(url).method(HttpMethod.GET).headers(headers)
        return self._walk_pages(client, params=query)

    def create_package(self, payload: dict) -> Munch:
        """
        Create a new package
        """
        url = "{}/v2/packages/".format(self._host)
        headers = self._get_auth_header()
        response = (
            RestClient(url)
            .method(HttpMethod.POST)
            .headers(headers)
            .execute(payload=payload)
        )
        handle_server_errors(response)

        data = json.loads(response.text)
        if not response.ok:
            err_msg = data.get("error")
            raise Exception("package: {}".format(err_msg))

        return munchify(data)

    def get_package(
        self,
        name: str,
        query: dict = None,
    ) -> Munch:
        """
        List all packages in a project
        """
        url = "{}/v2/packages/{}/".format(self._host, name)
        headers = self._get_auth_header()

        params = {}
        params.update(query or {})

        response = (
            RestClient(url)
            .method(HttpMethod.GET)
            .query_param(params)
            .headers(headers)
            .execute()
        )
        data = json.loads(response.text)
        if not response.ok:
            err_msg = data.get("error")
            raise Exception("package: {}".format(err_msg))

        return munchify(data)

    def delete_package(self, package_name: str, query: dict = None) -> Munch:
        """
        Delete a secret
        """
        url = "{}/v2/packages/{}/".format(self._host, package_name)
        headers = self._get_auth_header()

        params = {}
        params.update(query or {})

        response = (
            RestClient(url)
            .method(HttpMethod.DELETE)
            .query_param(params)
            .headers(headers)
            .execute()
        )
        handle_server_errors(response)

        data = json.loads(response.text)
        if not response.ok:
            err_msg = data.get("error")
            raise Exception("package: {}".format(err_msg))

        return munchify(data)

    def list_networks(
        self,
        query: dict = None,
    ) -> Munch:
        """
        List all networks in a project
        """
        url = "{}/v2/networks/".format(self._host)
        headers = self._get_auth_header()

        params = {}
        params.update(query or {})
        offset, result = 0, []
        while True:
            params.update(
                {
                    "continue": offset,
                }
            )
            response = (
                RestClient(url)
                .method(HttpMethod.GET)
                .query_param(params)
                .headers(headers)
                .execute()
            )
            data = json.loads(response.text)
            if not response.ok:
                err_msg = data.get("error")
                raise Exception("networks: {}".format(err_msg))
            networks = data.get("items", [])
            if not networks:
                break
            offset = data["metadata"]["continue"]
            result.extend(networks)

        return munchify(result)

    def create_network(self, payload: dict) -> Munch:
        """
        Create a new network
        """
        url = "{}/v2/networks/".format(self._host)
        headers = self._get_auth_header()
        response = (
            RestClient(url)
            .method(HttpMethod.POST)
            .headers(headers)
            .execute(payload=payload)
        )

        handle_server_errors(response)

        data = json.loads(response.text)
        if not response.ok:
            err_msg = data.get("error")
            raise Exception("network: {}".format(err_msg))

        return munchify(data)

    def get_network(
        self,
        name: str,
        query: dict = None,
    ) -> Munch:
        """
        get a network in a project
        """
        url = "{}/v2/networks/{}/".format(self._host, name)
        headers = self._get_auth_header()

        params = {}
        params.update(query or {})

        response = (
            RestClient(url)
            .method(HttpMethod.GET)
            .query_param(params)
            .headers(headers)
            .execute()
        )

        handle_server_errors(response)

        data = json.loads(response.text)

        if not response.ok:
            err_msg = data.get("error")
            raise Exception("network: {}".format(err_msg))

        return munchify(data)

    def delete_network(
        self,
        network_name: str,
        query: dict = None,
    ) -> Munch:
        """
        Delete a secret
        """
        url = "{}/v2/networks/{}/".format(self._host, network_name)
        headers = self._get_auth_header()

        params = {}
        params.update(query or {})

        response = (
            RestClient(url)
            .method(HttpMethod.DELETE)
            .query_param(params)
            .headers(headers)
            .execute()
        )
        handle_server_errors(response)

        data = json.loads(response.text)
        if not response.ok:
            err_msg = data.get("error")
            raise Exception("network: {}".format(err_msg))

        return munchify(data)

    def poll_network(
        self,
        name: str,
        retry_count: int = 50,
        sleep_interval: int = 6,
        ready_phases: List[str] = None,
    ) -> Munch:
        if ready_phases is None:
            ready_phases = []

        network = self.get_network(name)

        status = network.status

        for _ in range(retry_count):
            if status.phase in ready_phases:
                return network

            if status.phase == DeploymentPhaseConstants.DeploymentPhaseProvisioning.value:
                errors = status.get("error_codes", [])
                if (
                    "DEP_E153" in errors
                ):  # DEP_E153 (image-pull error) will persist across retries
                    raise ImagePullError(
                        "Network not running. Phase: Provisioning Status: {}".format(
                            status.phase
                        )
                    )
            elif status.phase == DeploymentPhaseConstants.DeploymentPhaseSucceeded.value:
                return network
            elif status.phase == DeploymentPhaseConstants.DeploymentPhaseStopped.value:
                raise DeploymentNotRunning(
                    "Network not running. Phase: Stopped  Status: {}".format(status.phase)
                )

            time.sleep(sleep_interval)
            network = self.get_network(name)
            status = network.status

        msg = "Retries exhausted: Tried {} times with {}s interval. Network: phase={} status={} \n{}".format(
            retry_count,
            sleep_interval,
            status.phase,
            status.status,
            process_errors(status.get("error_codes", [])),
        )

        raise RetriesExhausted(msg)

    def list_deployments(self, query: dict = None) -> Munch:
        """
        List all deployments in a project
        """
        url = "{}/v2/deployments/".format(self._host)
        headers = self._get_auth_header()
        client = RestClient(url).method(HttpMethod.GET).headers(headers)
        return self._walk_pages(client, params=query)

    def create_deployment(self, deployment: dict) -> Munch:
        """
        Create a new deployment
        """
        url = "{}/v2/deployments/".format(self._host)
        headers = self._get_auth_header()

        deployment["metadata"]["projectGUID"] = headers["project"]
        response = (
            RestClient(url)
            .method(HttpMethod.POST)
            .headers(headers)
            .execute(payload=deployment)
        )

        handle_server_errors(response)

        data = json.loads(response.text)
        if not response.ok:
            err_msg = data.get("error")
            raise Exception("deployment: {}".format(err_msg))

        return munchify(data)

    def get_deployment(self, name: str):
        url = "{}/v2/deployments/{}/".format(self._host, name)
        headers = self._get_auth_header()

        response = RestClient(url).method(HttpMethod.GET).headers(headers).execute()

        handle_server_errors(response)

        data = json.loads(response.text)

        if not response.ok:
            err_msg = data.get("error")
            raise Exception("deployment: {}".format(err_msg))

        return munchify(data)

    def update_deployment(self, name: str, dep: dict) -> Munch:
        """
        Update a deployment
        """
        url = "{}/v2/deployments/{}/".format(self._host, name)
        headers = self._get_auth_header()
        response = (
            RestClient(url).method(HttpMethod.PATCH).headers(headers).execute(payload=dep)
        )
        handle_server_errors(response)
        data = json.loads(response.text)
        if not response.ok:
            err_msg = data.get("error")
            raise Exception("deployment: {}".format(err_msg))

        return munchify(data)

    def delete_deployment(self, name: str, query: dict = None) -> Munch:
        """
        Delete a deployment
        """
        url = "{}/v2/deployments/{}/".format(self._host, name)
        headers = self._get_auth_header()
        params = {}
        params.update(query or {})
        response = RestClient(url).method(HttpMethod.DELETE).headers(headers).execute()
        handle_server_errors(response)
        data = json.loads(response.text)
        if not response.ok:
            err_msg = data.get("error")
            raise Exception("deployment: {}".format(err_msg))

        return munchify(data)

    def poll_deployment(
        self,
        name: str,
        retry_count: int = 50,
        sleep_interval: int = 6,
        ready_phases: List[str] = None,
    ) -> Munch:
        if ready_phases is None:
            ready_phases = []

        deployment = self.get_deployment(name)

        status = deployment.status

        for _ in range(retry_count):
            if status.phase in ready_phases:
                return deployment

            if status.phase == DeploymentPhaseConstants.DeploymentPhaseProvisioning.value:
                errors = status.get("error_codes", [])
                if (
                    "DEP_E153" in errors
                ):  # DEP_E153 (image-pull error) will persist across retries
                    raise ImagePullError(
                        "Deployment not running. Phase: Provisioning Status: {}".format(
                            status.phase
                        )
                    )
            elif status.phase == DeploymentPhaseConstants.DeploymentPhaseSucceeded.value:
                return deployment
            elif status.phase == DeploymentPhaseConstants.DeploymentPhaseStopped.value:
                raise DeploymentNotRunning(
                    "Deployment not running. Phase: Stopped  Status: {}".format(
                        status.phase
                    )
                )

            time.sleep(sleep_interval)
            deployment = self.get_deployment(name)
            status = deployment.status

        msg = "Retries exhausted: Tried {} times with {}s interval. Deployment: phase={} status={} \n{}".format(
            retry_count,
            sleep_interval,
            status.phase,
            status.status,
            process_errors(status.get("error_codes", [])),
        )

        raise RetriesExhausted(msg)

    def stream_deployment_logs(
        self,
        name: str,
        executable: str,
        replica: int = 0,
    ):
        url = "{}/v2/deployments/{}/logs/?replica={}&executable={}".format(
            self._host, name, replica, executable
        )
        headers = self._get_auth_header()

        curl = 'curl -H "project: {}" -H "Authorization: {}" "{}"'.format(
            headers["project"], headers["Authorization"], url
        )

        os.system(curl)

    def list_disks(
        self,
        query: dict = None,
    ) -> Munch:
        """
        List all disks in a project
        """
        url = "{}/v2/disks/".format(self._host)
        headers = self._get_auth_header()

        client = RestClient(url).method(HttpMethod.GET).headers(headers)
        return self._walk_pages(client, params=query)

    def get_disk(self, name: str) -> Munch:
        """
        Get a Disk by its name
        """
        url = "{}/v2/disks/{}/".format(self._host, name)
        headers = self._get_auth_header()
        response = RestClient(url).method(HttpMethod.GET).headers(headers).execute()

        handle_server_errors(response)

        data = json.loads(response.text)
        if not response.ok:
            err_msg = data.get("error")
            raise Exception("disks: {}".format(err_msg))

        return munchify(data)

    def create_disk(self, disk: dict) -> Munch:
        """
        Create a new disk
        """
        url = "{}/v2/disks/".format(self._host)
        headers = self._get_auth_header()
        response = (
            RestClient(url).method(HttpMethod.POST).headers(headers).execute(payload=disk)
        )

        handle_server_errors(response)

        data = json.loads(response.text)
        if not response.ok:
            err_msg = data.get("error")
            raise Exception("disks: {}".format(err_msg))

        return munchify(data)

    def delete_disk(self, name: str) -> Munch:
        """
        Delete a disk by its name
        """
        url = "{}/v2/disks/{}/".format(self._host, name)
        headers = self._get_auth_header()
        response = RestClient(url).method(HttpMethod.DELETE).headers(headers).execute()

        handle_server_errors(response)

        data = json.loads(response.text)
        if not response.ok:
            err_msg = data.get("error")
            raise Exception("disks: {}".format(err_msg))

        return munchify(data)

    def poll_disk(
        self,
        name: str,
        retry_count: int = 50,
        sleep_interval: int = 6,
    ) -> Munch:
        disk = self.get_disk(name)

        status = disk.status

        for _ in range(retry_count):
            if status.status in [
                DiskStatusConstants.DiskStatusAvailable.value,
                DiskStatusConstants.DiskStatusReleased.value,
            ]:
                return disk
            elif status.status == DiskStatusConstants.DiskStatusFailed.value:
                raise DeploymentNotRunning(
                    "Disk not running. Status: {}".format(status.status)
                )

            time.sleep(sleep_interval)
            disk = self.get_disk(name)
            status = disk.status

        raise RetriesExhausted(
            "Retries exhausted: Tried {} times with {}s interval. Disk: status={}".format(
                retry_count, sleep_interval, status.status
            )
        )

    # Devices
    def get_device_daemons(self, device_guid: str) -> Munch:
        url = "{}/v2/devices/daemons/{}/".format(self._host, device_guid)
        headers = self._get_auth_header()
        response = RestClient(url).method(HttpMethod.GET).headers(headers).execute()

        handle_server_errors(response)

        data = json.loads(response.text)
        if not response.ok:
            err_msg = data.get("error")
            raise Exception("device daemons: {}".format(err_msg))

        return munchify(data)

    # OAuth2 Clients
    def list_oauth2_clients(self, query: Optional[dict] = None) -> Munch:
        """
        List all OAuth2 Clients in the organization.
        """
        url = "{}/v2/oauth2/clients/".format(self._host)
        headers = self._get_auth_header(with_project=False)
        params = query or dict()

        client = RestClient(url).method(HttpMethod.GET).headers(headers)
        return self._walk_pages(client, params=params, limit=50)

    def get_oauth2_client(self, client_id: str) -> Munch:
        """
        Get an OAuth2 Client by its ID
        """
        url = "{}/v2/oauth2/clients/{}/".format(self._host, client_id)
        headers = self._get_auth_header(with_project=False)
        response = RestClient(url).method(HttpMethod.GET).headers(headers).execute()

        handle_server_errors(response)

        data = json.loads(response.text)
        if not response.ok:
            err_msg = data.get("error")
            raise Exception("oauth2 client: {}".format(err_msg))

        return munchify(data)

    def create_oauth2_client(self, client: dict[str, Any]) -> Munch:
        """
        Create a new OAuth2 Client.
        """
        url = "{}/v2/oauth2/clients/".format(self._host)
        headers = self._get_auth_header(with_project=False)
        response = (
            RestClient(url).method(HttpMethod.POST).headers(headers).execute(payload=client)
        )

        handle_server_errors(response)

        data = json.loads(response.text)
        if not response.ok:
            err_msg = data.get("error")
            raise Exception("oauth2 client: {}".format(err_msg))

        return munchify(data)

    def update_oauth2_client(self, client_id: str, client: dict[str, Any]) -> Munch:
        """
        Create a new OAuth2 Client.
        """
        url = "{}/v2/oauth2/clients/{}/".format(self._host, client_id)
        headers = self._get_auth_header(with_project=False)
        response = (
            RestClient(url).method(HttpMethod.PUT).headers(headers).execute(payload=client)
        )

        handle_server_errors(response)

        data = json.loads(response.text)
        if not response.ok:
            err_msg = data.get("error")
            raise Exception("oauth2 client: {}".format(err_msg))

        return munchify(data)

    def update_oauth2_client_uris(self, client_id: str, payload: dict[str, Optional[Sequence[str]]]) -> Munch:
        url = "{}/v2/oauth2/clients/{}/uris/".format(self._host, client_id)
        headers = self._get_auth_header(with_project=False)
        response = (
            RestClient(url).method(HttpMethod.PUT).headers(headers).execute(payload=payload)
        )

        handle_server_errors(response)

        data = json.loads(response.text)
        if not response.ok:
            err_msg = data.get("error")
            raise Exception("oauth2 client: {}".format(err_msg))

        return munchify(data)

    def delete_oauth2_client(self, client_id: str) -> Munch:
        """
        Delete an OAuth2 client by its id.
        """
        url = "{}/v2/oauth2/clients/{}/".format(self._host, client_id)
        headers = self._get_auth_header(with_project=False)
        response = RestClient(url).method(HttpMethod.DELETE).headers(headers).execute()

        handle_server_errors(response)

        data = json.loads(response.text)
        if not response.ok:
            err_msg = data.get("error")
            raise Exception("oauth2 client: {}".format(err_msg))

        return munchify(data)

import json
import typing

from munch import munchify, Munch
from rapyuta_io.utils.rest_client import HttpMethod, RestClient


class _Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(
                _Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class Client(metaclass=_Singleton):
    PROD_V2API_URL = "https://api.rapyuta.io"

    def __init__(self, config, auth_token: str, project: str = None):
        super().__init__()
        self._config = config
        self._host = config.data.get('v2api_host', self.PROD_V2API_URL)
        self._project = project
        self._token = auth_token

    def _get_auth_token(self):
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

    def get_project(self, project_guid: str):
        url = "{}/v2/projects/{}/".format(self._host, project_guid)
        headers = self._config.get_auth_header()
        response = RestClient(url).method(
            HttpMethod.GET).headers(headers).execute()

        data = json.loads(response.text)
        if not response.ok:
            err_msg = data.get('error')
            raise Exception("projects: {}".format(err_msg))

        return munchify(data)

    def create_project(self, spec: dict):
        url = "{}/v2/projects/".format(self._host)
        headers = {"Authorization": self._get_auth_token()}
        response = RestClient(url).method(HttpMethod.POST).headers(
            headers).execute(payload=spec)

        data = json.loads(response.text)
        if not response.ok:
            err_msg = data.get('error')
            raise Exception("projects: {}".format(err_msg))

        return munchify(data)

    def update_project(self, project_guid: str, spec: dict):
        url = "{}/v2/projects/{}/".format(self._host, project_guid)
        headers = {"Authorization": self._get_auth_token()}
        response = RestClient(url).method(HttpMethod.PUT).headers(
            headers).execute(payload=spec)

        data = json.loads(response.text)
        if not response.ok:
            err_msg = data.get('error')
            raise Exception("projects: {}".format(err_msg))

        return munchify(data)

    def delete_project(self, project_guid: str):
        url = "{}/v2/projects/{}/".format(self._host, project_guid)
        headers = {"Authorization": self._get_auth_token()}
        response = RestClient(url).method(
            HttpMethod.DELETE).headers(headers).execute()

        data = json.loads(response.text)
        if not response.ok:
            err_msg = data.get('error')
            raise Exception("projects: {}".format(err_msg))

        return munchify(data)

    def list_providers(self) -> typing.List:
        url = "{}/v2/managedservices/providers/".format(self._host)
        headers = self._config.get_auth_header()
        response = RestClient(url).method(
            HttpMethod.GET).headers(headers).execute()
        data = json.loads(response.text)
        if not response.ok:
            err_msg = data.get('error')
            raise Exception("managedservice: {}".format(err_msg))

        return munchify(data.get('items', []))

    def list_instances(self) -> typing.List:
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
        url = "{}/v2/managedservices/{}/".format(self._host, instance_name)
        headers = self._config.get_auth_header()
        response = RestClient(url).method(
            HttpMethod.GET).headers(headers).execute()
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
        data = json.loads(response.text)
        if not response.ok:
            err_msg = data.get('error')
            raise Exception("managedservice: {}".format(err_msg))

        return munchify(data)

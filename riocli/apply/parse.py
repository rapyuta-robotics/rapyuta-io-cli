#!/usr/bin/env python3
import functools
import re
import typing
from graphlib import TopologicalSorter

import yaml
import json
import click
from munch import munchify
from rapyuta_io import Client, DeploymentPhaseConstants
from rapyuta_io.utils.rest_client import HttpMethod, RestClient

from riocli.config import Configuration


class ResolverCache(object):
    KIND_REGEX = {
        "organization": "^org-.*",
        "project": "^project-.*",
        "secret": "^secret-.*",
        "package": "^pkg-.*",
        "staticroute": "^staticroute-.*",
        "build": "^build-.*",
        "disk": "^disk-.*",
        "deployment": "^dep-.*",
        "network": "net-.*",
        "device": "UUID_REGEX",
        "user": "UUID_REGEX",
    }

    GUID_KEYS = ['guid', 'GUID', 'uuid', 'ID', 'Id', 'id']
    NAME_KEYS = ['name', 'urlPrefix']


    def list_functors(self, kind):
        mapping = {
            'secret': self.client.list_secrets,
            "project": self.client.list_projects,
            "package": self.client.get_all_packages,
            "staticroute": self.client.get_all_static_routes,
            "build": self.client.list_builds,
            "deployment": functools.partial(self.client.get_all_deployments, phases=[DeploymentPhaseConstants.SUCCEEDED, DeploymentPhaseConstants.PROVISIONING]),
            "network": self.list_networks,
            "disk": self.list_disks,
            "device": self.client.get_all_devices,
        }

        return mapping[kind]

    def __init__(self, files: typing.List):
        self.config = Configuration()
        self.client = self.config.new_client()
        self.dependencies = {}
        self.objects = {}
        self.graph = {}
        self._read_files(files)

    def _read_files(self, files):
        self.files = {}
        for f in files:
            with open(f) as opened:
                data = opened.read()

            loaded_data = []
            if f.endswith("json"):
                # FIXME: Handle for JSON List.
                loaded = json.loads(data)
                loaded_data.append(loaded)
            elif f.endswith('yaml') or f.endswith('yml'):
                loaded = yaml.safe_load_all(data)
                loaded_data = list(loaded)

            if not loaded_data:
                click.secho('{} file is empty', f)
                continue

            for object in loaded_data:
                self.register_object(object)

            self.files[f] = loaded_data

    def register_object(self, data):
        kind = data['kind'].lower()
        name = data['metadata']['name']

        key = '{}:{}'.format(kind, name)
        self.objects[key] = data

    def parse_dependencies(self):
        for f, data in self.files.items():
            for model in data:
                key = '{}:{}'.format(model['kind'], model['metadata']['name']).lower()
                self.parse_dependency(model)
                dependencies = self.parse_dependency(model)
                self.graph[key] = dependencies

    def parse_dependency(self, model):
        dependencies = set()
        for key, value in model.items():
            if key == "depends" and value.get('kind'):
                local = self.resolve_dependency(value)
                if local:
                    dependencies |= {local}

                continue

            if isinstance(value, dict):
                dependencies |= self.parse_dependency(value)
                continue

            if isinstance(value, list):
                for each in value:
                    if isinstance(each, dict):
                        dependencies |= self.parse_dependency(each)

        return dependencies

    def resolve_dependency(self, dependency):
        kind = dependency.get('kind')
        nameOrGUID = dependency.get('nameOrGUID')
        key = '{}:{}'.format(kind, nameOrGUID)

        if not self.dependencies.get(kind):
            self.dependencies[kind] = {}

        guid = nameOrGUID if re.fullmatch(self.KIND_REGEX[kind], nameOrGUID) else None

        list = self.list_objects(kind)
        for obj in list:
            obj_guid = self.get_attr(obj, self.GUID_KEYS)
            obj_name = self.get_attr(obj, self.NAME_KEYS)

            if (guid and obj_guid == guid) or (nameOrGUID == obj_name):
                self.dependencies[kind][nameOrGUID] = {
                        'guid': obj_guid,
                        'raw': obj,
                        'local': False,
                    }
                return key

            if kind == 'staticroute' and nameOrGUID in obj_name:
                self.dependencies[kind][nameOrGUID] = {
                    'guid': obj_guid,
                    'raw': obj,
                    'local': False,
                }
                return key

        self.dependencies[kind][nameOrGUID] = {'local': True}
        return key

    def get_attr(self, object, accept_keys):
        for key in accept_keys:
            if hasattr(object, key):
                return getattr(object, key)

        raise Exception('guid resolve failed')

    # @functools.lru_cache()
    def list_objects(self, kind):
        # return [kind]
        return self.list_functors(kind)()

    # def create_dag(read_files, server_resource, local_resource):
    #     return [[res1, res2], [res4, res3]]
    #     pass

    # def fetch_resource_list(kind):
    #     switch kind:
    #        #sdk
    #        #request

    def list_networks(self):
        native = self.client.list_native_networks()
        routed = self.client.get_all_routed_networks()

        list = []
        if native:
            list.extend(native)

        if routed:
            list.extend(routed)
        return list

    def list_disks(self):
        config = Configuration()
        catalog_host = config.data.get('catalog_host', 'https://gacatalog.apps.rapyuta.io')
        url = '{}/disk'.format(catalog_host)
        headers = config.get_auth_header()
        response = RestClient(url).method(HttpMethod.GET).headers(headers).execute()
        data = json.loads(response.text)
        if not response.ok:
            err_msg = data.get('error')
            raise Exception(err_msg)
        return munchify(data)

    def order(self):
        return TopologicalSorter(self.graph).static_order()

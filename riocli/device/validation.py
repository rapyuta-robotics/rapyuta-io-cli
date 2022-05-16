VERSION = "2.15.3"
import re
from fastjsonschema import JsonSchemaValueException


REGEX_PATTERNS = {
    '^project-[a-z]{24}$': re.compile('^project-[a-z]{24}\\Z'),
    '^[a-fA-F0-9]{8}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{12}$': re.compile('^[a-fA-F0-9]{8}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{12}\\Z')
}

NoneType = type(None)

def validate(data, custom_formats={}):
    validate___definitions_device(data, custom_formats)
    return data

def validate___definitions_device(data, custom_formats={}):
    if not isinstance(data, (dict)):
        raise JsonSchemaValueException("data must be object", value=data, name="data", definition={'type': 'object', 'properties': {'apiVersion': {'const': 'apiextensions.rapyuta.io/v1'}, 'kind': {'const': 'Device'}, 'metadata': {'$ref': '#/definitions/metadata'}, 'spec': {'$ref': '#/definitions/deviceSpec'}, 'status': {'$ref': '#/definitions/deviceStatus'}}, 'required': ['apiVersion', 'kind', 'metadata', 'spec']}, rule='type')
    data_is_dict = isinstance(data, dict)
    if data_is_dict:
        data_len = len(data)
        if not all(prop in data for prop in ['apiVersion', 'kind', 'metadata', 'spec']):
            raise JsonSchemaValueException("data must contain ['apiVersion', 'kind', 'metadata', 'spec'] properties", value=data, name="data", definition={'type': 'object', 'properties': {'apiVersion': {'const': 'apiextensions.rapyuta.io/v1'}, 'kind': {'const': 'Device'}, 'metadata': {'$ref': '#/definitions/metadata'}, 'spec': {'$ref': '#/definitions/deviceSpec'}, 'status': {'$ref': '#/definitions/deviceStatus'}}, 'required': ['apiVersion', 'kind', 'metadata', 'spec']}, rule='required')
        data_keys = set(data.keys())
        if "apiVersion" in data_keys:
            data_keys.remove("apiVersion")
            data__apiVersion = data["apiVersion"]
            if data__apiVersion != "apiextensions.rapyuta.io/v1":
                raise JsonSchemaValueException("data.apiVersion must be same as const definition: apiextensions.rapyuta.io/v1", value=data__apiVersion, name="data.apiVersion", definition={'const': 'apiextensions.rapyuta.io/v1'}, rule='const')
        if "kind" in data_keys:
            data_keys.remove("kind")
            data__kind = data["kind"]
            if data__kind != "Device":
                raise JsonSchemaValueException("data.kind must be same as const definition: Device", value=data__kind, name="data.kind", definition={'const': 'Device'}, rule='const')
        if "metadata" in data_keys:
            data_keys.remove("metadata")
            data__metadata = data["metadata"]
            validate___definitions_metadata(data__metadata, custom_formats)
        if "spec" in data_keys:
            data_keys.remove("spec")
            data__spec = data["spec"]
            validate___definitions_devicespec(data__spec, custom_formats)
        if "status" in data_keys:
            data_keys.remove("status")
            data__status = data["status"]
            validate___definitions_devicestatus(data__status, custom_formats)
    return data

def validate___definitions_devicestatus(data, custom_formats={}):
    if not isinstance(data, (dict)):
        raise JsonSchemaValueException("data must be object", value=data, name="data", definition={'type': 'object', 'properties': {'status': {'$ref': '#/definitions/status'}, 'configVariables': {'$ref': '#/definitions/stringMap'}, 'os': {'type': 'string'}, 'lastOnlineTime': {'type': 'string'}}}, rule='type')
    data_is_dict = isinstance(data, dict)
    if data_is_dict:
        data_keys = set(data.keys())
        if "status" in data_keys:
            data_keys.remove("status")
            data__status = data["status"]
            validate___definitions_status(data__status, custom_formats)
        if "configVariables" in data_keys:
            data_keys.remove("configVariables")
            data__configVariables = data["configVariables"]
            validate___definitions_stringmap(data__configVariables, custom_formats)
        if "os" in data_keys:
            data_keys.remove("os")
            data__os = data["os"]
            if not isinstance(data__os, (str)):
                raise JsonSchemaValueException("data.os must be string", value=data__os, name="data.os", definition={'type': 'string'}, rule='type')
        if "lastOnlineTime" in data_keys:
            data_keys.remove("lastOnlineTime")
            data__lastOnlineTime = data["lastOnlineTime"]
            if not isinstance(data__lastOnlineTime, (str)):
                raise JsonSchemaValueException("data.lastOnlineTime must be string", value=data__lastOnlineTime, name="data.lastOnlineTime", definition={'type': 'string'}, rule='type')
    return data

def validate___definitions_stringmap(data, custom_formats={}):
    if not isinstance(data, (dict)):
        raise JsonSchemaValueException("data must be object", value=data, name="data", definition={'type': 'object', 'additionalProperties': {'type': 'string'}}, rule='type')
    data_is_dict = isinstance(data, dict)
    if data_is_dict:
        data_keys = set(data.keys())
        for data_key in data_keys:
            if data_key not in []:
                data_value = data.get(data_key)
                if not isinstance(data_value, (str)):
                    raise JsonSchemaValueException(""+"data.{data_key}".format(**locals())+" must be string", value=data_value, name=""+"data.{data_key}".format(**locals())+"", definition={'type': 'string'}, rule='type')
    return data

def validate___definitions_status(data, custom_formats={}):
    if data not in ['Registered', 'Online', 'Offline', 'Initializing', 'Error', 'Failed']:
        raise JsonSchemaValueException("data must be one of ['Registered', 'Online', 'Offline', 'Initializing', 'Error', 'Failed']", value=data, name="data", definition={'enum': ['Registered', 'Online', 'Offline', 'Initializing', 'Error', 'Failed']}, rule='enum')
    return data

def validate___definitions_devicespec(data, custom_formats={}):
    if not isinstance(data, (dict)):
        raise JsonSchemaValueException("data must be object", value=data, name="data", definition={'type': 'object', 'properties': {'runtime': {'$ref': '#/definitions/runtime'}, 'rosDistro': {'$ref': '#/definitions/rosDistro'}, 'python': {'$ref': '#/definitions/pythonVersion'}}, 'required': ['runtime', 'rosDistro', 'python'], 'allOf': [{'if': {'properties': {'runtime': {'const': 'Docker'}}}, 'then': {'properties': {'rosbagMountPath': {'type': 'string', 'default': '/opt/rapyuta/volumes/rosbag'}}}}, {'if': {'properties': {'runtime': {'const': 'Preinstalled'}}}, 'then': {'properties': {'catkinWorkspace': {'type': 'string', 'default': 'Dockerfile'}}, 'required': ['catkinWorkspace']}}]}, rule='type')
    try:
        data_is_dict = isinstance(data, dict)
        if data_is_dict:
            data_keys = set(data.keys())
            if "runtime" in data_keys:
                data_keys.remove("runtime")
                data__runtime = data["runtime"]
                if data__runtime != "Docker":
                    raise JsonSchemaValueException("data.runtime must be same as const definition: Docker", value=data__runtime, name="data.runtime", definition={'const': 'Docker'}, rule='const')
    except JsonSchemaValueException:
        pass
    else:
        data_is_dict = isinstance(data, dict)
        if data_is_dict:
            data_keys = set(data.keys())
            if "rosbagMountPath" in data_keys:
                data_keys.remove("rosbagMountPath")
                data__rosbagMountPath = data["rosbagMountPath"]
                if not isinstance(data__rosbagMountPath, (str)):
                    raise JsonSchemaValueException("data.rosbagMountPath must be string", value=data__rosbagMountPath, name="data.rosbagMountPath", definition={'type': 'string', 'default': '/opt/rapyuta/volumes/rosbag'}, rule='type')
            else: data["rosbagMountPath"] = '/opt/rapyuta/volumes/rosbag'
    try:
        data_is_dict = isinstance(data, dict)
        if data_is_dict:
            data_keys = set(data.keys())
            if "runtime" in data_keys:
                data_keys.remove("runtime")
                data__runtime = data["runtime"]
                if data__runtime != "Preinstalled":
                    raise JsonSchemaValueException("data.runtime must be same as const definition: Preinstalled", value=data__runtime, name="data.runtime", definition={'const': 'Preinstalled'}, rule='const')
    except JsonSchemaValueException:
        pass
    else:
        data_is_dict = isinstance(data, dict)
        if data_is_dict:
            data_len = len(data)
            if not all(prop in data for prop in ['catkinWorkspace']):
                raise JsonSchemaValueException("data must contain ['catkinWorkspace'] properties", value=data, name="data", definition={'properties': {'catkinWorkspace': {'type': 'string', 'default': 'Dockerfile'}}, 'required': ['catkinWorkspace']}, rule='required')
            data_keys = set(data.keys())
            if "catkinWorkspace" in data_keys:
                data_keys.remove("catkinWorkspace")
                data__catkinWorkspace = data["catkinWorkspace"]
                if not isinstance(data__catkinWorkspace, (str)):
                    raise JsonSchemaValueException("data.catkinWorkspace must be string", value=data__catkinWorkspace, name="data.catkinWorkspace", definition={'type': 'string', 'default': 'Dockerfile'}, rule='type')
            else: data["catkinWorkspace"] = 'Dockerfile'
    data_is_dict = isinstance(data, dict)
    if data_is_dict:
        data_len = len(data)
        if not all(prop in data for prop in ['runtime', 'rosDistro', 'python']):
            raise JsonSchemaValueException("data must contain ['runtime', 'rosDistro', 'python'] properties", value=data, name="data", definition={'type': 'object', 'properties': {'runtime': {'$ref': '#/definitions/runtime'}, 'rosDistro': {'$ref': '#/definitions/rosDistro'}, 'python': {'$ref': '#/definitions/pythonVersion'}}, 'required': ['runtime', 'rosDistro', 'python'], 'allOf': [{'if': {'properties': {'runtime': {'const': 'Docker'}}}, 'then': {'properties': {'rosbagMountPath': {'type': 'string', 'default': '/opt/rapyuta/volumes/rosbag'}}}}, {'if': {'properties': {'runtime': {'const': 'Preinstalled'}}}, 'then': {'properties': {'catkinWorkspace': {'type': 'string', 'default': 'Dockerfile'}}, 'required': ['catkinWorkspace']}}]}, rule='required')
        data_keys = set(data.keys())
        if "runtime" in data_keys:
            data_keys.remove("runtime")
            data__runtime = data["runtime"]
            validate___definitions_runtime(data__runtime, custom_formats)
        if "rosDistro" in data_keys:
            data_keys.remove("rosDistro")
            data__rosDistro = data["rosDistro"]
            validate___definitions_rosdistro(data__rosDistro, custom_formats)
        if "python" in data_keys:
            data_keys.remove("python")
            data__python = data["python"]
            validate___definitions_pythonversion(data__python, custom_formats)
    return data

def validate___definitions_pythonversion(data, custom_formats={}):
    if data not in [3, 2]:
        raise JsonSchemaValueException("data must be one of [3, 2]", value=data, name="data", definition={'enum': [3, 2]}, rule='enum')
    return data

def validate___definitions_rosdistro(data, custom_formats={}):
    if data not in ['melodic', 'kinetic', 'noetic']:
        raise JsonSchemaValueException("data must be one of ['melodic', 'kinetic', 'noetic']", value=data, name="data", definition={'enum': ['melodic', 'kinetic', 'noetic']}, rule='enum')
    return data

def validate___definitions_runtime(data, custom_formats={}):
    if data not in ['Docker', 'Preinstalled']:
        raise JsonSchemaValueException("data must be one of ['Docker', 'Preinstalled']", value=data, name="data", definition={'enum': ['Docker', 'Preinstalled']}, rule='enum')
    return data

def validate___definitions_metadata(data, custom_formats={}):
    if not isinstance(data, (dict)):
        raise JsonSchemaValueException("data must be object", value=data, name="data", definition={'type': 'object', 'properties': {'name': {'type': 'string'}, 'guid': {'$ref': '#/definitions/uuid'}, 'creator': {'$ref': '#/definitions/uuid'}, 'project': {'$ref': '#/definitions/projectGUID'}, 'labels': {'$ref': '#/definitions/stringMap', 'uniqueItems': True}}, 'required': ['name']}, rule='type')
    data_is_dict = isinstance(data, dict)
    if data_is_dict:
        data_len = len(data)
        if not all(prop in data for prop in ['name']):
            raise JsonSchemaValueException("data must contain ['name'] properties", value=data, name="data", definition={'type': 'object', 'properties': {'name': {'type': 'string'}, 'guid': {'$ref': '#/definitions/uuid'}, 'creator': {'$ref': '#/definitions/uuid'}, 'project': {'$ref': '#/definitions/projectGUID'}, 'labels': {'$ref': '#/definitions/stringMap', 'uniqueItems': True}}, 'required': ['name']}, rule='required')
        data_keys = set(data.keys())
        if "name" in data_keys:
            data_keys.remove("name")
            data__name = data["name"]
            if not isinstance(data__name, (str)):
                raise JsonSchemaValueException("data.name must be string", value=data__name, name="data.name", definition={'type': 'string'}, rule='type')
        if "guid" in data_keys:
            data_keys.remove("guid")
            data__guid = data["guid"]
            validate___definitions_uuid(data__guid, custom_formats)
        if "creator" in data_keys:
            data_keys.remove("creator")
            data__creator = data["creator"]
            validate___definitions_uuid(data__creator, custom_formats)
        if "project" in data_keys:
            data_keys.remove("project")
            data__project = data["project"]
            validate___definitions_projectguid(data__project, custom_formats)
        if "labels" in data_keys:
            data_keys.remove("labels")
            data__labels = data["labels"]
            validate___definitions_stringmap(data__labels, custom_formats)
    return data

def validate___definitions_projectguid(data, custom_formats={}):
    if not isinstance(data, (str)):
        raise JsonSchemaValueException("data must be string", value=data, name="data", definition={'type': 'string', 'pattern': '^project-[a-z]{24}$'}, rule='type')
    if isinstance(data, str):
        if not REGEX_PATTERNS['^project-[a-z]{24}$'].search(data):
            raise JsonSchemaValueException("data must match pattern ^project-[a-z]{24}$", value=data, name="data", definition={'type': 'string', 'pattern': '^project-[a-z]{24}$'}, rule='pattern')
    return data

def validate___definitions_uuid(data, custom_formats={}):
    if not isinstance(data, (str)):
        raise JsonSchemaValueException("data must be string", value=data, name="data", definition={'type': 'string', 'pattern': '^[a-fA-F0-9]{8}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{12}$'}, rule='type')
    if isinstance(data, str):
        if not REGEX_PATTERNS['^[a-fA-F0-9]{8}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{12}$'].search(data):
            raise JsonSchemaValueException("data must match pattern ^[a-fA-F0-9]{8}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{12}$", value=data, name="data", definition={'type': 'string', 'pattern': '^[a-fA-F0-9]{8}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{12}$'}, rule='pattern')
    return data
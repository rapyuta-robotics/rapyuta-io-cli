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
        raise JsonSchemaValueException("data must be object", value=data, name="data", definition={'type': 'object', 'properties': {'apiVersion': {'const': 'apiextensions.rapyuta.io/v1'}, 'kind': {'const': 'Device'}, 'metadata': {'$ref': '#/definitions/metadata'}, 'spec': {'$ref': '#/definitions/deviceSpec'}}, 'required': ['apiVersion', 'kind', 'metadata', 'spec']}, rule='type')
    data_is_dict = isinstance(data, dict)
    if data_is_dict:
        data_len = len(data)
        if not all(prop in data for prop in ['apiVersion', 'kind', 'metadata', 'spec']):
            raise JsonSchemaValueException("data must contain ['apiVersion', 'kind', 'metadata', 'spec'] properties", value=data, name="data", definition={'type': 'object', 'properties': {'apiVersion': {'const': 'apiextensions.rapyuta.io/v1'}, 'kind': {'const': 'Device'}, 'metadata': {'$ref': '#/definitions/metadata'}, 'spec': {'$ref': '#/definitions/deviceSpec'}}, 'required': ['apiVersion', 'kind', 'metadata', 'spec']}, rule='required')
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
    return data

def validate___definitions_devicespec(data, custom_formats={}):
    if not isinstance(data, (dict)):
        raise JsonSchemaValueException("data must be object", value=data, name="data", definition={'type': 'object', 'properties': {'rosDistro': {'type': 'string', 'enum': ['kinetic', 'melodic', 'noetic'], 'default': 'melodic'}, 'python': {'type': 'string', 'enum': ['2', '3'], 'default': '3'}}, 'dependencies': {'docker': {'oneOf': [{'properties': {'enabled': {'enum': [False]}}}, {'properties': {'enabled': {'enum': [True]}, 'rosbagMountPath': {'type': 'string', 'default': '/opt/rapyuta/volumes/rosbag'}}}]}, 'preinstalled': {'oneOf': [{'properties': {'enabled': {'enum': [False]}}}, {'properties': {'enabled': {'enum': [True]}, 'catkinWorkspace': {'type': 'string'}}}]}}}, rule='type')
    data_is_dict = isinstance(data, dict)
    if data_is_dict:
        if "docker" in data:
            data_one_of_count1 = 0
            if data_one_of_count1 < 2:
                try:
                    data_is_dict = isinstance(data, dict)
                    if data_is_dict:
                        data_keys = set(data.keys())
                        if "enabled" in data_keys:
                            data_keys.remove("enabled")
                            data__enabled = data["enabled"]
                            if data__enabled not in [False]:
                                raise JsonSchemaValueException("data.enabled must be one of [False]", value=data__enabled, name="data.enabled", definition={'enum': [False]}, rule='enum')
                    data_one_of_count1 += 1
                except JsonSchemaValueException: pass
            if data_one_of_count1 < 2:
                try:
                    data_is_dict = isinstance(data, dict)
                    if data_is_dict:
                        data_keys = set(data.keys())
                        if "enabled" in data_keys:
                            data_keys.remove("enabled")
                            data__enabled = data["enabled"]
                            if data__enabled not in [True]:
                                raise JsonSchemaValueException("data.enabled must be one of [True]", value=data__enabled, name="data.enabled", definition={'enum': [True]}, rule='enum')
                        if "rosbagMountPath" in data_keys:
                            data_keys.remove("rosbagMountPath")
                            data__rosbagMountPath = data["rosbagMountPath"]
                            if not isinstance(data__rosbagMountPath, (str)):
                                raise JsonSchemaValueException("data.rosbagMountPath must be string", value=data__rosbagMountPath, name="data.rosbagMountPath", definition={'type': 'string', 'default': '/opt/rapyuta/volumes/rosbag'}, rule='type')
                        else: data["rosbagMountPath"] = '/opt/rapyuta/volumes/rosbag'
                    data_one_of_count1 += 1
                except JsonSchemaValueException: pass
            if data_one_of_count1 != 1:
                raise JsonSchemaValueException("data must be valid exactly by one of oneOf definition", value=data, name="data", definition={'oneOf': [{'properties': {'enabled': {'enum': [False]}}}, {'properties': {'enabled': {'enum': [True]}, 'rosbagMountPath': {'type': 'string', 'default': '/opt/rapyuta/volumes/rosbag'}}}]}, rule='oneOf')
        if "preinstalled" in data:
            data_one_of_count2 = 0
            if data_one_of_count2 < 2:
                try:
                    data_is_dict = isinstance(data, dict)
                    if data_is_dict:
                        data_keys = set(data.keys())
                        if "enabled" in data_keys:
                            data_keys.remove("enabled")
                            data__enabled = data["enabled"]
                            if data__enabled not in [False]:
                                raise JsonSchemaValueException("data.enabled must be one of [False]", value=data__enabled, name="data.enabled", definition={'enum': [False]}, rule='enum')
                    data_one_of_count2 += 1
                except JsonSchemaValueException: pass
            if data_one_of_count2 < 2:
                try:
                    data_is_dict = isinstance(data, dict)
                    if data_is_dict:
                        data_keys = set(data.keys())
                        if "enabled" in data_keys:
                            data_keys.remove("enabled")
                            data__enabled = data["enabled"]
                            if data__enabled not in [True]:
                                raise JsonSchemaValueException("data.enabled must be one of [True]", value=data__enabled, name="data.enabled", definition={'enum': [True]}, rule='enum')
                        if "catkinWorkspace" in data_keys:
                            data_keys.remove("catkinWorkspace")
                            data__catkinWorkspace = data["catkinWorkspace"]
                            if not isinstance(data__catkinWorkspace, (str)):
                                raise JsonSchemaValueException("data.catkinWorkspace must be string", value=data__catkinWorkspace, name="data.catkinWorkspace", definition={'type': 'string'}, rule='type')
                    data_one_of_count2 += 1
                except JsonSchemaValueException: pass
            if data_one_of_count2 != 1:
                raise JsonSchemaValueException("data must be valid exactly by one of oneOf definition", value=data, name="data", definition={'oneOf': [{'properties': {'enabled': {'enum': [False]}}}, {'properties': {'enabled': {'enum': [True]}, 'catkinWorkspace': {'type': 'string'}}}]}, rule='oneOf')
        data_keys = set(data.keys())
        if "rosDistro" in data_keys:
            data_keys.remove("rosDistro")
            data__rosDistro = data["rosDistro"]
            if not isinstance(data__rosDistro, (str)):
                raise JsonSchemaValueException("data.rosDistro must be string", value=data__rosDistro, name="data.rosDistro", definition={'type': 'string', 'enum': ['kinetic', 'melodic', 'noetic'], 'default': 'melodic'}, rule='type')
            if data__rosDistro not in ['kinetic', 'melodic', 'noetic']:
                raise JsonSchemaValueException("data.rosDistro must be one of ['kinetic', 'melodic', 'noetic']", value=data__rosDistro, name="data.rosDistro", definition={'type': 'string', 'enum': ['kinetic', 'melodic', 'noetic'], 'default': 'melodic'}, rule='enum')
        else: data["rosDistro"] = 'melodic'
        if "python" in data_keys:
            data_keys.remove("python")
            data__python = data["python"]
            if not isinstance(data__python, (str)):
                raise JsonSchemaValueException("data.python must be string", value=data__python, name="data.python", definition={'type': 'string', 'enum': ['2', '3'], 'default': '3'}, rule='type')
            if data__python not in ['2', '3']:
                raise JsonSchemaValueException("data.python must be one of ['2', '3']", value=data__python, name="data.python", definition={'type': 'string', 'enum': ['2', '3'], 'default': '3'}, rule='enum')
        else: data["python"] = '3'
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
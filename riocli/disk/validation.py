VERSION = "2.16.2"
import re
from fastjsonschema import JsonSchemaValueException


REGEX_PATTERNS = {
    '^project-[a-z]{24}$': re.compile('^project-[a-z]{24}\\Z'),
    '^[a-fA-F0-9]{8}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{12}$': re.compile('^[a-fA-F0-9]{8}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{12}\\Z'),
    '^disk-[a-z]{24}$': re.compile('^disk-[a-z]{24}\\Z')
}

NoneType = type(None)

def validate(data, custom_formats={}, name_prefix=None):
    validate___definitions_disk(data, custom_formats, (name_prefix or "data") + "")
    return data

def validate___definitions_disk(data, custom_formats={}, name_prefix=None):
    if not isinstance(data, (dict)):
        raise JsonSchemaValueException("" + (name_prefix or "data") + " must be object", value=data, name="" + (name_prefix or "data") + "", definition={'type': 'object', 'properties': {'apiVersion': {'const': 'apiextensions.rapyuta.io/v1', 'default': 'apiextensions.rapyuta.io/v1'}, 'kind': {'const': 'Disk', 'default': 'Disk'}, 'metadata': {'type': 'object', 'properties': {'name': {'type': 'string'}, 'guid': {'$ref': '#/definitions/diskGUID'}, 'creator': {'$ref': '#/definitions/uuid'}, 'project': {'$ref': '#/definitions/projectGUID'}, 'labels': {'$ref': '#/definitions/stringMap'}}, 'required': ['name']}, 'spec': {'type': 'object', 'properties': {'runtime': {'default': 'cloud', 'const': 'cloud'}, 'capacity': {'type': 'number', 'enum': [4, 8, 16, 32, 64, 128, 256, 512]}}}}, 'required': ['apiVersion', 'kind', 'metadata', 'spec']}, rule='type')
    data_is_dict = isinstance(data, dict)
    if data_is_dict:
        data_len = len(data)
        if not all(prop in data for prop in ['apiVersion', 'kind', 'metadata', 'spec']):
            raise JsonSchemaValueException("" + (name_prefix or "data") + " must contain ['apiVersion', 'kind', 'metadata', 'spec'] properties", value=data, name="" + (name_prefix or "data") + "", definition={'type': 'object', 'properties': {'apiVersion': {'const': 'apiextensions.rapyuta.io/v1', 'default': 'apiextensions.rapyuta.io/v1'}, 'kind': {'const': 'Disk', 'default': 'Disk'}, 'metadata': {'type': 'object', 'properties': {'name': {'type': 'string'}, 'guid': {'$ref': '#/definitions/diskGUID'}, 'creator': {'$ref': '#/definitions/uuid'}, 'project': {'$ref': '#/definitions/projectGUID'}, 'labels': {'$ref': '#/definitions/stringMap'}}, 'required': ['name']}, 'spec': {'type': 'object', 'properties': {'runtime': {'default': 'cloud', 'const': 'cloud'}, 'capacity': {'type': 'number', 'enum': [4, 8, 16, 32, 64, 128, 256, 512]}}}}, 'required': ['apiVersion', 'kind', 'metadata', 'spec']}, rule='required')
        data_keys = set(data.keys())
        if "apiVersion" in data_keys:
            data_keys.remove("apiVersion")
            data__apiVersion = data["apiVersion"]
            if data__apiVersion != "apiextensions.rapyuta.io/v1":
                raise JsonSchemaValueException("" + (name_prefix or "data") + ".apiVersion must be same as const definition: apiextensions.rapyuta.io/v1", value=data__apiVersion, name="" + (name_prefix or "data") + ".apiVersion", definition={'const': 'apiextensions.rapyuta.io/v1', 'default': 'apiextensions.rapyuta.io/v1'}, rule='const')
        else: data["apiVersion"] = 'apiextensions.rapyuta.io/v1'
        if "kind" in data_keys:
            data_keys.remove("kind")
            data__kind = data["kind"]
            if data__kind != "Disk":
                raise JsonSchemaValueException("" + (name_prefix or "data") + ".kind must be same as const definition: Disk", value=data__kind, name="" + (name_prefix or "data") + ".kind", definition={'const': 'Disk', 'default': 'Disk'}, rule='const')
        else: data["kind"] = 'Disk'
        if "metadata" in data_keys:
            data_keys.remove("metadata")
            data__metadata = data["metadata"]
            validate___definitions_metadata(data__metadata, custom_formats, (name_prefix or "data") + ".metadata")
        if "spec" in data_keys:
            data_keys.remove("spec")
            data__spec = data["spec"]
            validate___definitions_diskspec(data__spec, custom_formats, (name_prefix or "data") + ".spec")
    return data

def validate___definitions_diskspec(data, custom_formats={}, name_prefix=None):
    if not isinstance(data, (dict)):
        raise JsonSchemaValueException("" + (name_prefix or "data") + " must be object", value=data, name="" + (name_prefix or "data") + "", definition={'type': 'object', 'properties': {'runtime': {'default': 'cloud', 'const': 'cloud'}, 'capacity': {'type': 'number', 'enum': [4, 8, 16, 32, 64, 128, 256, 512]}}}, rule='type')
    data_is_dict = isinstance(data, dict)
    if data_is_dict:
        data_keys = set(data.keys())
        if "runtime" in data_keys:
            data_keys.remove("runtime")
            data__runtime = data["runtime"]
            if data__runtime != "cloud":
                raise JsonSchemaValueException("" + (name_prefix or "data") + ".runtime must be same as const definition: cloud", value=data__runtime, name="" + (name_prefix or "data") + ".runtime", definition={'default': 'cloud', 'const': 'cloud'}, rule='const')
        else: data["runtime"] = 'cloud'
        if "capacity" in data_keys:
            data_keys.remove("capacity")
            data__capacity = data["capacity"]
            if not isinstance(data__capacity, (int, float)) or isinstance(data__capacity, bool):
                raise JsonSchemaValueException("" + (name_prefix or "data") + ".capacity must be number", value=data__capacity, name="" + (name_prefix or "data") + ".capacity", definition={'type': 'number', 'enum': [4, 8, 16, 32, 64, 128, 256, 512]}, rule='type')
            if data__capacity not in [4, 8, 16, 32, 64, 128, 256, 512]:
                raise JsonSchemaValueException("" + (name_prefix or "data") + ".capacity must be one of [4, 8, 16, 32, 64, 128, 256, 512]", value=data__capacity, name="" + (name_prefix or "data") + ".capacity", definition={'type': 'number', 'enum': [4, 8, 16, 32, 64, 128, 256, 512]}, rule='enum')
    return data

def validate___definitions_metadata(data, custom_formats={}, name_prefix=None):
    if not isinstance(data, (dict)):
        raise JsonSchemaValueException("" + (name_prefix or "data") + " must be object", value=data, name="" + (name_prefix or "data") + "", definition={'type': 'object', 'properties': {'name': {'type': 'string'}, 'guid': {'type': 'string', 'pattern': '^disk-[a-z]{24}$'}, 'creator': {'type': 'string', 'pattern': '^[a-fA-F0-9]{8}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{12}$'}, 'project': {'type': 'string', 'pattern': '^project-[a-z]{24}$'}, 'labels': {'type': 'object', 'additionalProperties': {'type': 'string'}}}, 'required': ['name']}, rule='type')
    data_is_dict = isinstance(data, dict)
    if data_is_dict:
        data_len = len(data)
        if not all(prop in data for prop in ['name']):
            raise JsonSchemaValueException("" + (name_prefix or "data") + " must contain ['name'] properties", value=data, name="" + (name_prefix or "data") + "", definition={'type': 'object', 'properties': {'name': {'type': 'string'}, 'guid': {'type': 'string', 'pattern': '^disk-[a-z]{24}$'}, 'creator': {'type': 'string', 'pattern': '^[a-fA-F0-9]{8}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{12}$'}, 'project': {'type': 'string', 'pattern': '^project-[a-z]{24}$'}, 'labels': {'type': 'object', 'additionalProperties': {'type': 'string'}}}, 'required': ['name']}, rule='required')
        data_keys = set(data.keys())
        if "name" in data_keys:
            data_keys.remove("name")
            data__name = data["name"]
            if not isinstance(data__name, (str)):
                raise JsonSchemaValueException("" + (name_prefix or "data") + ".name must be string", value=data__name, name="" + (name_prefix or "data") + ".name", definition={'type': 'string'}, rule='type')
        if "guid" in data_keys:
            data_keys.remove("guid")
            data__guid = data["guid"]
            validate___definitions_diskguid(data__guid, custom_formats, (name_prefix or "data") + ".guid")
        if "creator" in data_keys:
            data_keys.remove("creator")
            data__creator = data["creator"]
            validate___definitions_uuid(data__creator, custom_formats, (name_prefix or "data") + ".creator")
        if "project" in data_keys:
            data_keys.remove("project")
            data__project = data["project"]
            validate___definitions_projectguid(data__project, custom_formats, (name_prefix or "data") + ".project")
        if "labels" in data_keys:
            data_keys.remove("labels")
            data__labels = data["labels"]
            validate___definitions_stringmap(data__labels, custom_formats, (name_prefix or "data") + ".labels")
    return data

def validate___definitions_stringmap(data, custom_formats={}, name_prefix=None):
    if not isinstance(data, (dict)):
        raise JsonSchemaValueException("" + (name_prefix or "data") + " must be object", value=data, name="" + (name_prefix or "data") + "", definition={'type': 'object', 'additionalProperties': {'type': 'string'}}, rule='type')
    data_is_dict = isinstance(data, dict)
    if data_is_dict:
        data_keys = set(data.keys())
        for data_key in data_keys:
            if data_key not in []:
                data_value = data.get(data_key)
                if not isinstance(data_value, (str)):
                    raise JsonSchemaValueException("" + (name_prefix or "data") + ".{data_key}".format(**locals()) + " must be string", value=data_value, name="" + (name_prefix or "data") + ".{data_key}".format(**locals()) + "", definition={'type': 'string'}, rule='type')
    return data

def validate___definitions_projectguid(data, custom_formats={}, name_prefix=None):
    if not isinstance(data, (str)):
        raise JsonSchemaValueException("" + (name_prefix or "data") + " must be string", value=data, name="" + (name_prefix or "data") + "", definition={'type': 'string', 'pattern': '^project-[a-z]{24}$'}, rule='type')
    if isinstance(data, str):
        if not REGEX_PATTERNS['^project-[a-z]{24}$'].search(data):
            raise JsonSchemaValueException("" + (name_prefix or "data") + " must match pattern ^project-[a-z]{24}$", value=data, name="" + (name_prefix or "data") + "", definition={'type': 'string', 'pattern': '^project-[a-z]{24}$'}, rule='pattern')
    return data

def validate___definitions_uuid(data, custom_formats={}, name_prefix=None):
    if not isinstance(data, (str)):
        raise JsonSchemaValueException("" + (name_prefix or "data") + " must be string", value=data, name="" + (name_prefix or "data") + "", definition={'type': 'string', 'pattern': '^[a-fA-F0-9]{8}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{12}$'}, rule='type')
    if isinstance(data, str):
        if not REGEX_PATTERNS['^[a-fA-F0-9]{8}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{12}$'].search(data):
            raise JsonSchemaValueException("" + (name_prefix or "data") + " must match pattern ^[a-fA-F0-9]{8}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{12}$", value=data, name="" + (name_prefix or "data") + "", definition={'type': 'string', 'pattern': '^[a-fA-F0-9]{8}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{12}$'}, rule='pattern')
    return data

def validate___definitions_diskguid(data, custom_formats={}, name_prefix=None):
    if not isinstance(data, (str)):
        raise JsonSchemaValueException("" + (name_prefix or "data") + " must be string", value=data, name="" + (name_prefix or "data") + "", definition={'type': 'string', 'pattern': '^disk-[a-z]{24}$'}, rule='type')
    if isinstance(data, str):
        if not REGEX_PATTERNS['^disk-[a-z]{24}$'].search(data):
            raise JsonSchemaValueException("" + (name_prefix or "data") + " must match pattern ^disk-[a-z]{24}$", value=data, name="" + (name_prefix or "data") + "", definition={'type': 'string', 'pattern': '^disk-[a-z]{24}$'}, rule='pattern')
    return data
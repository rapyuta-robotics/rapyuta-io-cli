VERSION = "2.15.3"
import re
from fastjsonschema import JsonSchemaValueException


REGEX_PATTERNS = {
    '^[a-fA-F0-9]{8}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{12}$': re.compile('^[a-fA-F0-9]{8}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{12}\\Z'),
    '^project-[a-z]{24}$': re.compile('^project-[a-z]{24}\\Z')
}

NoneType = type(None)

def validate(data, custom_formats={}):
    validate___definitions_staticroute(data, custom_formats)
    return data

def validate___definitions_staticroute(data, custom_formats={}):
    if not isinstance(data, (dict)):
        raise JsonSchemaValueException("data must be object", value=data, name="data", definition={'type': 'object', 'properties': {'apiVersion': {'const': 'apiextensions.rapyuta.io/v1', 'default': 'apiextensions.rapyuta.io/v1'}, 'kind': {'const': 'StaticRoute'}, 'metadata': {'$ref': '#/definitions/metadata'}}, 'required': ['apiVersion', 'kind', 'metadata']}, rule='type')
    data_is_dict = isinstance(data, dict)
    if data_is_dict:
        data_len = len(data)
        if not all(prop in data for prop in ['apiVersion', 'kind', 'metadata']):
            raise JsonSchemaValueException("data must contain ['apiVersion', 'kind', 'metadata'] properties", value=data, name="data", definition={'type': 'object', 'properties': {'apiVersion': {'const': 'apiextensions.rapyuta.io/v1', 'default': 'apiextensions.rapyuta.io/v1'}, 'kind': {'const': 'StaticRoute'}, 'metadata': {'$ref': '#/definitions/metadata'}}, 'required': ['apiVersion', 'kind', 'metadata']}, rule='required')
        data_keys = set(data.keys())
        if "apiVersion" in data_keys:
            data_keys.remove("apiVersion")
            data__apiVersion = data["apiVersion"]
            if data__apiVersion != "apiextensions.rapyuta.io/v1":
                raise JsonSchemaValueException("data.apiVersion must be same as const definition: apiextensions.rapyuta.io/v1", value=data__apiVersion, name="data.apiVersion", definition={'const': 'apiextensions.rapyuta.io/v1', 'default': 'apiextensions.rapyuta.io/v1'}, rule='const')
        else: data["apiVersion"] = 'apiextensions.rapyuta.io/v1'
        if "kind" in data_keys:
            data_keys.remove("kind")
            data__kind = data["kind"]
            if data__kind != "StaticRoute":
                raise JsonSchemaValueException("data.kind must be same as const definition: StaticRoute", value=data__kind, name="data.kind", definition={'const': 'StaticRoute'}, rule='const')
        if "metadata" in data_keys:
            data_keys.remove("metadata")
            data__metadata = data["metadata"]
            validate___definitions_metadata(data__metadata, custom_formats)
    return data

def validate___definitions_metadata(data, custom_formats={}):
    if not isinstance(data, (dict)):
        raise JsonSchemaValueException("data must be object", value=data, name="data", definition={'type': 'object', 'properties': {'name': {'type': 'string'}, 'guid': {'$ref': '#/definitions/projectGUID'}, 'creator': {'$ref': '#/definitions/uuid'}, 'project': {'$ref': '#/definitions/projectGUID'}, 'labels': {'$ref': '#/definitions/stringMap', 'uniqueItems': True}}, 'required': ['name']}, rule='type')
    data_is_dict = isinstance(data, dict)
    if data_is_dict:
        data_len = len(data)
        if not all(prop in data for prop in ['name']):
            raise JsonSchemaValueException("data must contain ['name'] properties", value=data, name="data", definition={'type': 'object', 'properties': {'name': {'type': 'string'}, 'guid': {'$ref': '#/definitions/projectGUID'}, 'creator': {'$ref': '#/definitions/uuid'}, 'project': {'$ref': '#/definitions/projectGUID'}, 'labels': {'$ref': '#/definitions/stringMap', 'uniqueItems': True}}, 'required': ['name']}, rule='required')
        data_keys = set(data.keys())
        if "name" in data_keys:
            data_keys.remove("name")
            data__name = data["name"]
            if not isinstance(data__name, (str)):
                raise JsonSchemaValueException("data.name must be string", value=data__name, name="data.name", definition={'type': 'string'}, rule='type')
        if "guid" in data_keys:
            data_keys.remove("guid")
            data__guid = data["guid"]
            validate___definitions_projectguid(data__guid, custom_formats)
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

def validate___definitions_uuid(data, custom_formats={}):
    if not isinstance(data, (str)):
        raise JsonSchemaValueException("data must be string", value=data, name="data", definition={'type': 'string', 'pattern': '^[a-fA-F0-9]{8}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{12}$'}, rule='type')
    if isinstance(data, str):
        if not REGEX_PATTERNS['^[a-fA-F0-9]{8}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{12}$'].search(data):
            raise JsonSchemaValueException("data must match pattern ^[a-fA-F0-9]{8}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{12}$", value=data, name="data", definition={'type': 'string', 'pattern': '^[a-fA-F0-9]{8}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{12}$'}, rule='pattern')
    return data

def validate___definitions_projectguid(data, custom_formats={}):
    if not isinstance(data, (str)):
        raise JsonSchemaValueException("data must be string", value=data, name="data", definition={'type': 'string', 'pattern': '^project-[a-z]{24}$'}, rule='type')
    if isinstance(data, str):
        if not REGEX_PATTERNS['^project-[a-z]{24}$'].search(data):
            raise JsonSchemaValueException("data must match pattern ^project-[a-z]{24}$", value=data, name="data", definition={'type': 'string', 'pattern': '^project-[a-z]{24}$'}, rule='pattern')
    return data
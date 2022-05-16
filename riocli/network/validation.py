VERSION = "2.15.3"
import re
from fastjsonschema import JsonSchemaValueException


REGEX_PATTERNS = {
    '^[a-fA-F0-9]{8}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{12}$': re.compile('^[a-fA-F0-9]{8}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{12}\\Z'),
    '^project-[a-z]{24}$': re.compile('^project-[a-z]{24}\\Z'),
    '^network-[a-z]{24}$': re.compile('^network-[a-z]{24}\\Z')
}

NoneType = type(None)

def validate(data, custom_formats={}):
    validate___definitions_network(data, custom_formats)
    return data

def validate___definitions_network(data, custom_formats={}):
    if not isinstance(data, (dict)):
        raise JsonSchemaValueException("data must be object", value=data, name="data", definition={'type': 'object', 'properties': {'apiVersion': {'const': 'apiextensions.rapyuta.io/v1'}, 'kind': {'const': 'Network'}, 'metadata': {'$ref': '#/definitions/metadata'}, 'spec': {'$ref': '#/definitions/networkSpec'}}, 'required': ['apiVersion', 'kind', 'metadata', 'spec']}, rule='type')
    data_is_dict = isinstance(data, dict)
    if data_is_dict:
        data_len = len(data)
        if not all(prop in data for prop in ['apiVersion', 'kind', 'metadata', 'spec']):
            raise JsonSchemaValueException("data must contain ['apiVersion', 'kind', 'metadata', 'spec'] properties", value=data, name="data", definition={'type': 'object', 'properties': {'apiVersion': {'const': 'apiextensions.rapyuta.io/v1'}, 'kind': {'const': 'Network'}, 'metadata': {'$ref': '#/definitions/metadata'}, 'spec': {'$ref': '#/definitions/networkSpec'}}, 'required': ['apiVersion', 'kind', 'metadata', 'spec']}, rule='required')
        data_keys = set(data.keys())
        if "apiVersion" in data_keys:
            data_keys.remove("apiVersion")
            data__apiVersion = data["apiVersion"]
            if data__apiVersion != "apiextensions.rapyuta.io/v1":
                raise JsonSchemaValueException("data.apiVersion must be same as const definition: apiextensions.rapyuta.io/v1", value=data__apiVersion, name="data.apiVersion", definition={'const': 'apiextensions.rapyuta.io/v1'}, rule='const')
        if "kind" in data_keys:
            data_keys.remove("kind")
            data__kind = data["kind"]
            if data__kind != "Network":
                raise JsonSchemaValueException("data.kind must be same as const definition: Network", value=data__kind, name="data.kind", definition={'const': 'Network'}, rule='const')
        if "metadata" in data_keys:
            data_keys.remove("metadata")
            data__metadata = data["metadata"]
            validate___definitions_metadata(data__metadata, custom_formats)
        if "spec" in data_keys:
            data_keys.remove("spec")
            data__spec = data["spec"]
            validate___definitions_networkspec(data__spec, custom_formats)
    return data

def validate___definitions_networkspec(data, custom_formats={}):
    if not isinstance(data, (dict)):
        raise JsonSchemaValueException("data must be object", value=data, name="data", definition={'type': 'object', 'properties': {'runtime': {'$ref': '#/definitions/runtime'}, 'type': {'$ref': '#/definitions/networkType'}, 'rosDistro': {'$ref': '#/definitions/rosDistro'}}, 'required': ['runtime', 'type', 'rosDistro'], 'allOf': [{'if': {'properties': {'runtime': {'const': 'Cloud'}}}, 'then': {'properties': {'resourceLimits': {'$ref': '#/definitions/resourceLimits'}}, 'required': ['resourceLimits']}}, {'if': {'properties': {'runtime': {'const': 'Device'}}}, 'then': {'properties': {'deviceGUID': {'$ref': '#/definitions/uuid'}, 'networkInterface': {'type': 'string'}}, 'required': ['deviceGUID', 'networkInterface']}}]}, rule='type')
    try:
        data_is_dict = isinstance(data, dict)
        if data_is_dict:
            data_keys = set(data.keys())
            if "runtime" in data_keys:
                data_keys.remove("runtime")
                data__runtime = data["runtime"]
                if data__runtime != "Cloud":
                    raise JsonSchemaValueException("data.runtime must be same as const definition: Cloud", value=data__runtime, name="data.runtime", definition={'const': 'Cloud'}, rule='const')
    except JsonSchemaValueException:
        pass
    else:
        data_is_dict = isinstance(data, dict)
        if data_is_dict:
            data_len = len(data)
            if not all(prop in data for prop in ['resourceLimits']):
                raise JsonSchemaValueException("data must contain ['resourceLimits'] properties", value=data, name="data", definition={'properties': {'resourceLimits': {'$ref': '#/definitions/resourceLimits'}}, 'required': ['resourceLimits']}, rule='required')
            data_keys = set(data.keys())
            if "resourceLimits" in data_keys:
                data_keys.remove("resourceLimits")
                data__resourceLimits = data["resourceLimits"]
                validate___definitions_resourcelimits(data__resourceLimits, custom_formats)
    try:
        data_is_dict = isinstance(data, dict)
        if data_is_dict:
            data_keys = set(data.keys())
            if "runtime" in data_keys:
                data_keys.remove("runtime")
                data__runtime = data["runtime"]
                if data__runtime != "Device":
                    raise JsonSchemaValueException("data.runtime must be same as const definition: Device", value=data__runtime, name="data.runtime", definition={'const': 'Device'}, rule='const')
    except JsonSchemaValueException:
        pass
    else:
        data_is_dict = isinstance(data, dict)
        if data_is_dict:
            data_len = len(data)
            if not all(prop in data for prop in ['deviceGUID', 'networkInterface']):
                raise JsonSchemaValueException("data must contain ['deviceGUID', 'networkInterface'] properties", value=data, name="data", definition={'properties': {'deviceGUID': {'$ref': '#/definitions/uuid'}, 'networkInterface': {'type': 'string'}}, 'required': ['deviceGUID', 'networkInterface']}, rule='required')
            data_keys = set(data.keys())
            if "deviceGUID" in data_keys:
                data_keys.remove("deviceGUID")
                data__deviceGUID = data["deviceGUID"]
                validate___definitions_uuid(data__deviceGUID, custom_formats)
            if "networkInterface" in data_keys:
                data_keys.remove("networkInterface")
                data__networkInterface = data["networkInterface"]
                if not isinstance(data__networkInterface, (str)):
                    raise JsonSchemaValueException("data.networkInterface must be string", value=data__networkInterface, name="data.networkInterface", definition={'type': 'string'}, rule='type')
    data_is_dict = isinstance(data, dict)
    if data_is_dict:
        data_len = len(data)
        if not all(prop in data for prop in ['runtime', 'type', 'rosDistro']):
            raise JsonSchemaValueException("data must contain ['runtime', 'type', 'rosDistro'] properties", value=data, name="data", definition={'type': 'object', 'properties': {'runtime': {'$ref': '#/definitions/runtime'}, 'type': {'$ref': '#/definitions/networkType'}, 'rosDistro': {'$ref': '#/definitions/rosDistro'}}, 'required': ['runtime', 'type', 'rosDistro'], 'allOf': [{'if': {'properties': {'runtime': {'const': 'Cloud'}}}, 'then': {'properties': {'resourceLimits': {'$ref': '#/definitions/resourceLimits'}}, 'required': ['resourceLimits']}}, {'if': {'properties': {'runtime': {'const': 'Device'}}}, 'then': {'properties': {'deviceGUID': {'$ref': '#/definitions/uuid'}, 'networkInterface': {'type': 'string'}}, 'required': ['deviceGUID', 'networkInterface']}}]}, rule='required')
        data_keys = set(data.keys())
        if "runtime" in data_keys:
            data_keys.remove("runtime")
            data__runtime = data["runtime"]
            validate___definitions_runtime(data__runtime, custom_formats)
        if "type" in data_keys:
            data_keys.remove("type")
            data__type = data["type"]
            validate___definitions_networktype(data__type, custom_formats)
        if "rosDistro" in data_keys:
            data_keys.remove("rosDistro")
            data__rosDistro = data["rosDistro"]
            validate___definitions_rosdistro(data__rosDistro, custom_formats)
    return data

def validate___definitions_rosdistro(data, custom_formats={}):
    if data not in ['melodic', 'kinetic', 'noetic']:
        raise JsonSchemaValueException("data must be one of ['melodic', 'kinetic', 'noetic']", value=data, name="data", definition={'enum': ['melodic', 'kinetic', 'noetic']}, rule='enum')
    return data

def validate___definitions_networktype(data, custom_formats={}):
    if data not in ['Routed', 'Native']:
        raise JsonSchemaValueException("data must be one of ['Routed', 'Native']", value=data, name="data", definition={'enum': ['Routed', 'Native']}, rule='enum')
    return data

def validate___definitions_runtime(data, custom_formats={}):
    if data not in ['Cloud', 'Device']:
        raise JsonSchemaValueException("data must be one of ['Cloud', 'Device']", value=data, name="data", definition={'enum': ['Cloud', 'Device']}, rule='enum')
    return data

def validate___definitions_uuid(data, custom_formats={}):
    if not isinstance(data, (str)):
        raise JsonSchemaValueException("data must be string", value=data, name="data", definition={'type': 'string', 'pattern': '^[a-fA-F0-9]{8}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{12}$'}, rule='type')
    if isinstance(data, str):
        if not REGEX_PATTERNS['^[a-fA-F0-9]{8}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{12}$'].search(data):
            raise JsonSchemaValueException("data must match pattern ^[a-fA-F0-9]{8}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{12}$", value=data, name="data", definition={'type': 'string', 'pattern': '^[a-fA-F0-9]{8}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{12}$'}, rule='pattern')
    return data

def validate___definitions_resourcelimits(data, custom_formats={}):
    if data not in ['XSmall', 'Small', 'Medium', 'Large']:
        raise JsonSchemaValueException("data must be one of ['XSmall', 'Small', 'Medium', 'Large']", value=data, name="data", definition={'enum': ['XSmall', 'Small', 'Medium', 'Large']}, rule='enum')
    return data

def validate___definitions_metadata(data, custom_formats={}):
    if not isinstance(data, (dict)):
        raise JsonSchemaValueException("data must be object", value=data, name="data", definition={'type': 'object', 'properties': {'name': {'type': 'string'}, 'guid': {'$ref': '#/definitions/networkGUID'}, 'creator': {'$ref': '#/definitions/uuid'}, 'project': {'$ref': '#/definitions/projectGUID'}, 'labels': {'$ref': '#/definitions/stringMap', 'uniqueItems': True}}, 'required': ['name']}, rule='type')
    data_is_dict = isinstance(data, dict)
    if data_is_dict:
        data_len = len(data)
        if not all(prop in data for prop in ['name']):
            raise JsonSchemaValueException("data must contain ['name'] properties", value=data, name="data", definition={'type': 'object', 'properties': {'name': {'type': 'string'}, 'guid': {'$ref': '#/definitions/networkGUID'}, 'creator': {'$ref': '#/definitions/uuid'}, 'project': {'$ref': '#/definitions/projectGUID'}, 'labels': {'$ref': '#/definitions/stringMap', 'uniqueItems': True}}, 'required': ['name']}, rule='required')
        data_keys = set(data.keys())
        if "name" in data_keys:
            data_keys.remove("name")
            data__name = data["name"]
            if not isinstance(data__name, (str)):
                raise JsonSchemaValueException("data.name must be string", value=data__name, name="data.name", definition={'type': 'string'}, rule='type')
        if "guid" in data_keys:
            data_keys.remove("guid")
            data__guid = data["guid"]
            validate___definitions_networkguid(data__guid, custom_formats)
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

def validate___definitions_networkguid(data, custom_formats={}):
    if not isinstance(data, (str)):
        raise JsonSchemaValueException("data must be string", value=data, name="data", definition={'type': 'string', 'pattern': '^network-[a-z]{24}$'}, rule='type')
    if isinstance(data, str):
        if not REGEX_PATTERNS['^network-[a-z]{24}$'].search(data):
            raise JsonSchemaValueException("data must match pattern ^network-[a-z]{24}$", value=data, name="data", definition={'type': 'string', 'pattern': '^network-[a-z]{24}$'}, rule='pattern')
    return data
VERSION = "2.15.3"
import re
from fastjsonschema import JsonSchemaValueException


REGEX_PATTERNS = {
    '^[a-fA-F0-9]{8}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{12}$': re.compile('^[a-fA-F0-9]{8}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{12}\\Z'),
    '^project-[a-z]{24}$': re.compile('^project-[a-z]{24}\\Z')
}

NoneType = type(None)

def validate(data, custom_formats={}):
    validate___definitions_project(data, custom_formats)
    return data

def validate___definitions_project(data, custom_formats={}):
    if not isinstance(data, (dict)):
        raise JsonSchemaValueException("data must be object", value=data, name="data", definition={'type': 'object', 'properties': {'apiVersion': {'const': 'apiextensions.rapyuta.io/v1', 'default': 'apiextensions.rapyuta.io/v1'}, 'kind': {'const': 'Project'}, 'metadata': {'$ref': '#/definitions/metadata'}, 'spec': {'$ref': '#/definitions/projectSpec'}, 'status': {'$ref': '#/definitions/projectStatus'}}, 'required': ['apiVersion', 'kind', 'metadata', 'spec']}, rule='type')
    data_is_dict = isinstance(data, dict)
    if data_is_dict:
        data_len = len(data)
        if not all(prop in data for prop in ['apiVersion', 'kind', 'metadata', 'spec']):
            raise JsonSchemaValueException("data must contain ['apiVersion', 'kind', 'metadata', 'spec'] properties", value=data, name="data", definition={'type': 'object', 'properties': {'apiVersion': {'const': 'apiextensions.rapyuta.io/v1', 'default': 'apiextensions.rapyuta.io/v1'}, 'kind': {'const': 'Project'}, 'metadata': {'$ref': '#/definitions/metadata'}, 'spec': {'$ref': '#/definitions/projectSpec'}, 'status': {'$ref': '#/definitions/projectStatus'}}, 'required': ['apiVersion', 'kind', 'metadata', 'spec']}, rule='required')
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
            if data__kind != "Project":
                raise JsonSchemaValueException("data.kind must be same as const definition: Project", value=data__kind, name="data.kind", definition={'const': 'Project'}, rule='const')
        if "metadata" in data_keys:
            data_keys.remove("metadata")
            data__metadata = data["metadata"]
            validate___definitions_metadata(data__metadata, custom_formats)
        if "spec" in data_keys:
            data_keys.remove("spec")
            data__spec = data["spec"]
            validate___definitions_projectspec(data__spec, custom_formats)
        if "status" in data_keys:
            data_keys.remove("status")
            data__status = data["status"]
            validate___definitions_projectstatus(data__status, custom_formats)
    return data

def validate___definitions_projectstatus(data, custom_formats={}):
    if not isinstance(data, (dict)):
        raise JsonSchemaValueException("data must be object", value=data, name="data", definition={'type': 'object', 'properties': {'users': {'type': 'array', 'items': {'$ref': '#/definitions/user'}, 'uniqueItems': True}}, 'required': ['users']}, rule='type')
    data_is_dict = isinstance(data, dict)
    if data_is_dict:
        data_len = len(data)
        if not all(prop in data for prop in ['users']):
            raise JsonSchemaValueException("data must contain ['users'] properties", value=data, name="data", definition={'type': 'object', 'properties': {'users': {'type': 'array', 'items': {'$ref': '#/definitions/user'}, 'uniqueItems': True}}, 'required': ['users']}, rule='required')
        data_keys = set(data.keys())
        if "users" in data_keys:
            data_keys.remove("users")
            data__users = data["users"]
            if not isinstance(data__users, (list, tuple)):
                raise JsonSchemaValueException("data.users must be array", value=data__users, name="data.users", definition={'type': 'array', 'items': {'$ref': '#/definitions/user'}, 'uniqueItems': True}, rule='type')
            data__users_is_list = isinstance(data__users, (list, tuple))
            if data__users_is_list:
                def fn(var): return frozenset(dict((k, fn(v)) for k, v in var.items()).items()) if hasattr(var, "items") else tuple(fn(v) for v in var) if isinstance(var, (dict, list)) else str(var) if isinstance(var, bool) else var
                data__users_len = len(data__users)
                if data__users_len > len(set(fn(data__users_x) for data__users_x in data__users)):
                    raise JsonSchemaValueException("data.users must contain unique items", value=data__users, name="data.users", definition={'type': 'array', 'items': {'$ref': '#/definitions/user'}, 'uniqueItems': True}, rule='uniqueItems')
                for data__users_x, data__users_item in enumerate(data__users):
                    validate___definitions_user(data__users_item, custom_formats)
    return data

def validate___definitions_user(data, custom_formats={}):
    if not isinstance(data, (dict)):
        raise JsonSchemaValueException("data must be object", value=data, name="data", definition={'type': 'object', 'properties': {'email_id': {'type': 'string'}, 'first_name': {'type': 'string'}, 'last_name': {'type': 'string'}, 'guid': {'$ref': '#/definitions/uuid'}, 'state': {'type': 'string'}}, 'required': ['guid', 'state', 'email_id']}, rule='type')
    data_is_dict = isinstance(data, dict)
    if data_is_dict:
        data_len = len(data)
        if not all(prop in data for prop in ['guid', 'state', 'email_id']):
            raise JsonSchemaValueException("data must contain ['guid', 'state', 'email_id'] properties", value=data, name="data", definition={'type': 'object', 'properties': {'email_id': {'type': 'string'}, 'first_name': {'type': 'string'}, 'last_name': {'type': 'string'}, 'guid': {'$ref': '#/definitions/uuid'}, 'state': {'type': 'string'}}, 'required': ['guid', 'state', 'email_id']}, rule='required')
        data_keys = set(data.keys())
        if "email_id" in data_keys:
            data_keys.remove("email_id")
            data__emailid = data["email_id"]
            if not isinstance(data__emailid, (str)):
                raise JsonSchemaValueException("data.email_id must be string", value=data__emailid, name="data.email_id", definition={'type': 'string'}, rule='type')
        if "first_name" in data_keys:
            data_keys.remove("first_name")
            data__firstname = data["first_name"]
            if not isinstance(data__firstname, (str)):
                raise JsonSchemaValueException("data.first_name must be string", value=data__firstname, name="data.first_name", definition={'type': 'string'}, rule='type')
        if "last_name" in data_keys:
            data_keys.remove("last_name")
            data__lastname = data["last_name"]
            if not isinstance(data__lastname, (str)):
                raise JsonSchemaValueException("data.last_name must be string", value=data__lastname, name="data.last_name", definition={'type': 'string'}, rule='type')
        if "guid" in data_keys:
            data_keys.remove("guid")
            data__guid = data["guid"]
            validate___definitions_uuid(data__guid, custom_formats)
        if "state" in data_keys:
            data_keys.remove("state")
            data__state = data["state"]
            if not isinstance(data__state, (str)):
                raise JsonSchemaValueException("data.state must be string", value=data__state, name="data.state", definition={'type': 'string'}, rule='type')
    return data

def validate___definitions_uuid(data, custom_formats={}):
    if not isinstance(data, (str)):
        raise JsonSchemaValueException("data must be string", value=data, name="data", definition={'type': 'string', 'pattern': '^[a-fA-F0-9]{8}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{12}$'}, rule='type')
    if isinstance(data, str):
        if not REGEX_PATTERNS['^[a-fA-F0-9]{8}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{12}$'].search(data):
            raise JsonSchemaValueException("data must match pattern ^[a-fA-F0-9]{8}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{12}$", value=data, name="data", definition={'type': 'string', 'pattern': '^[a-fA-F0-9]{8}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{12}$'}, rule='pattern')
    return data

def validate___definitions_projectspec(data, custom_formats={}):
    if not isinstance(data, (dict)):
        raise JsonSchemaValueException("data must be object", value=data, name="data", definition={'type': 'object', 'properties': {'users': {'type': 'array', 'items': {'type': 'string'}}}, 'required': ['users']}, rule='type')
    data_is_dict = isinstance(data, dict)
    if data_is_dict:
        data_len = len(data)
        if not all(prop in data for prop in ['users']):
            raise JsonSchemaValueException("data must contain ['users'] properties", value=data, name="data", definition={'type': 'object', 'properties': {'users': {'type': 'array', 'items': {'type': 'string'}}}, 'required': ['users']}, rule='required')
        data_keys = set(data.keys())
        if "users" in data_keys:
            data_keys.remove("users")
            data__users = data["users"]
            if not isinstance(data__users, (list, tuple)):
                raise JsonSchemaValueException("data.users must be array", value=data__users, name="data.users", definition={'type': 'array', 'items': {'type': 'string'}}, rule='type')
            data__users_is_list = isinstance(data__users, (list, tuple))
            if data__users_is_list:
                data__users_len = len(data__users)
                for data__users_x, data__users_item in enumerate(data__users):
                    if not isinstance(data__users_item, (str)):
                        raise JsonSchemaValueException(""+"data.users[{data__users_x}]".format(**locals())+" must be string", value=data__users_item, name=""+"data.users[{data__users_x}]".format(**locals())+"", definition={'type': 'string'}, rule='type')
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

def validate___definitions_projectguid(data, custom_formats={}):
    if not isinstance(data, (str)):
        raise JsonSchemaValueException("data must be string", value=data, name="data", definition={'type': 'string', 'pattern': '^project-[a-z]{24}$'}, rule='type')
    if isinstance(data, str):
        if not REGEX_PATTERNS['^project-[a-z]{24}$'].search(data):
            raise JsonSchemaValueException("data must match pattern ^project-[a-z]{24}$", value=data, name="data", definition={'type': 'string', 'pattern': '^project-[a-z]{24}$'}, rule='pattern')
    return data
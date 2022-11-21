VERSION = "2.16.2"
import re
from fastjsonschema import JsonSchemaValueException


REGEX_PATTERNS = {
    '^[a-fA-F0-9]{8}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{12}$': re.compile('^[a-fA-F0-9]{8}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{12}\\Z'),
    '^project-[a-z]{24}$': re.compile('^project-[a-z]{24}\\Z')
}

NoneType = type(None)

def validate(data, custom_formats={}, name_prefix=None):
    validate___definitions_project(data, custom_formats, (name_prefix or "data") + "")
    return data

def validate___definitions_project(data, custom_formats={}, name_prefix=None):
    if not isinstance(data, (dict)):
        raise JsonSchemaValueException("" + (name_prefix or "data") + " must be object", value=data, name="" + (name_prefix or "data") + "", definition={'type': 'object', 'properties': {'apiVersion': {'const': 'apiextensions.rapyuta.io/v1', 'default': 'apiextensions.rapyuta.io/v1'}, 'kind': {'const': 'Project'}, 'metadata': {'type': 'object', 'properties': {'name': {'type': 'string'}, 'guid': {'$ref': '#/definitions/projectGUID'}, 'creator': {'$ref': '#/definitions/uuid'}, 'project': {'$ref': '#/definitions/projectGUID'}, 'labels': {'$ref': '#/definitions/stringMap', 'uniqueItems': True}}, 'required': ['name']}, 'spec': {'type': 'object', 'properties': {'users': {'type': 'array', 'items': {'type': 'string'}}}, 'required': ['users']}, 'status': {'type': 'object', 'properties': {'users': {'type': 'array', 'items': {'$ref': '#/definitions/user'}, 'uniqueItems': True}}, 'required': ['users']}}, 'required': ['apiVersion', 'kind', 'metadata', 'spec']}, rule='type')
    data_is_dict = isinstance(data, dict)
    if data_is_dict:
        data_len = len(data)
        if not all(prop in data for prop in ['apiVersion', 'kind', 'metadata', 'spec']):
            raise JsonSchemaValueException("" + (name_prefix or "data") + " must contain ['apiVersion', 'kind', 'metadata', 'spec'] properties", value=data, name="" + (name_prefix or "data") + "", definition={'type': 'object', 'properties': {'apiVersion': {'const': 'apiextensions.rapyuta.io/v1', 'default': 'apiextensions.rapyuta.io/v1'}, 'kind': {'const': 'Project'}, 'metadata': {'type': 'object', 'properties': {'name': {'type': 'string'}, 'guid': {'$ref': '#/definitions/projectGUID'}, 'creator': {'$ref': '#/definitions/uuid'}, 'project': {'$ref': '#/definitions/projectGUID'}, 'labels': {'$ref': '#/definitions/stringMap', 'uniqueItems': True}}, 'required': ['name']}, 'spec': {'type': 'object', 'properties': {'users': {'type': 'array', 'items': {'type': 'string'}}}, 'required': ['users']}, 'status': {'type': 'object', 'properties': {'users': {'type': 'array', 'items': {'$ref': '#/definitions/user'}, 'uniqueItems': True}}, 'required': ['users']}}, 'required': ['apiVersion', 'kind', 'metadata', 'spec']}, rule='required')
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
            if data__kind != "Project":
                raise JsonSchemaValueException("" + (name_prefix or "data") + ".kind must be same as const definition: Project", value=data__kind, name="" + (name_prefix or "data") + ".kind", definition={'const': 'Project'}, rule='const')
        if "metadata" in data_keys:
            data_keys.remove("metadata")
            data__metadata = data["metadata"]
            validate___definitions_metadata(data__metadata, custom_formats, (name_prefix or "data") + ".metadata")
        if "spec" in data_keys:
            data_keys.remove("spec")
            data__spec = data["spec"]
            validate___definitions_projectspec(data__spec, custom_formats, (name_prefix or "data") + ".spec")
        if "status" in data_keys:
            data_keys.remove("status")
            data__status = data["status"]
            validate___definitions_projectstatus(data__status, custom_formats, (name_prefix or "data") + ".status")
    return data

def validate___definitions_projectstatus(data, custom_formats={}, name_prefix=None):
    if not isinstance(data, (dict)):
        raise JsonSchemaValueException("" + (name_prefix or "data") + " must be object", value=data, name="" + (name_prefix or "data") + "", definition={'type': 'object', 'properties': {'users': {'type': 'array', 'items': {'type': 'object', 'properties': {'email_id': {'type': 'string'}, 'first_name': {'type': 'string'}, 'last_name': {'type': 'string'}, 'guid': {'$ref': '#/definitions/uuid'}, 'state': {'type': 'string'}}, 'required': ['guid', 'state', 'email_id']}, 'uniqueItems': True}}, 'required': ['users']}, rule='type')
    data_is_dict = isinstance(data, dict)
    if data_is_dict:
        data_len = len(data)
        if not all(prop in data for prop in ['users']):
            raise JsonSchemaValueException("" + (name_prefix or "data") + " must contain ['users'] properties", value=data, name="" + (name_prefix or "data") + "", definition={'type': 'object', 'properties': {'users': {'type': 'array', 'items': {'type': 'object', 'properties': {'email_id': {'type': 'string'}, 'first_name': {'type': 'string'}, 'last_name': {'type': 'string'}, 'guid': {'$ref': '#/definitions/uuid'}, 'state': {'type': 'string'}}, 'required': ['guid', 'state', 'email_id']}, 'uniqueItems': True}}, 'required': ['users']}, rule='required')
        data_keys = set(data.keys())
        if "users" in data_keys:
            data_keys.remove("users")
            data__users = data["users"]
            if not isinstance(data__users, (list, tuple)):
                raise JsonSchemaValueException("" + (name_prefix or "data") + ".users must be array", value=data__users, name="" + (name_prefix or "data") + ".users", definition={'type': 'array', 'items': {'type': 'object', 'properties': {'email_id': {'type': 'string'}, 'first_name': {'type': 'string'}, 'last_name': {'type': 'string'}, 'guid': {'$ref': '#/definitions/uuid'}, 'state': {'type': 'string'}}, 'required': ['guid', 'state', 'email_id']}, 'uniqueItems': True}, rule='type')
            data__users_is_list = isinstance(data__users, (list, tuple))
            if data__users_is_list:
                def fn(var): return frozenset(dict((k, fn(v)) for k, v in var.items()).items()) if hasattr(var, "items") else tuple(fn(v) for v in var) if isinstance(var, (dict, list)) else str(var) if isinstance(var, bool) else var
                data__users_len = len(data__users)
                if data__users_len > len(set(fn(data__users_x) for data__users_x in data__users)):
                    raise JsonSchemaValueException("" + (name_prefix or "data") + ".users must contain unique items", value=data__users, name="" + (name_prefix or "data") + ".users", definition={'type': 'array', 'items': {'type': 'object', 'properties': {'email_id': {'type': 'string'}, 'first_name': {'type': 'string'}, 'last_name': {'type': 'string'}, 'guid': {'$ref': '#/definitions/uuid'}, 'state': {'type': 'string'}}, 'required': ['guid', 'state', 'email_id']}, 'uniqueItems': True}, rule='uniqueItems')
                for data__users_x, data__users_item in enumerate(data__users):
                    validate___definitions_user(data__users_item, custom_formats, (name_prefix or "data") + ".users[{data__users_x}]")
    return data

def validate___definitions_user(data, custom_formats={}, name_prefix=None):
    if not isinstance(data, (dict)):
        raise JsonSchemaValueException("" + (name_prefix or "data") + " must be object", value=data, name="" + (name_prefix or "data") + "", definition={'type': 'object', 'properties': {'email_id': {'type': 'string'}, 'first_name': {'type': 'string'}, 'last_name': {'type': 'string'}, 'guid': {'type': 'string', 'pattern': '^[a-fA-F0-9]{8}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{12}$'}, 'state': {'type': 'string'}}, 'required': ['guid', 'state', 'email_id']}, rule='type')
    data_is_dict = isinstance(data, dict)
    if data_is_dict:
        data_len = len(data)
        if not all(prop in data for prop in ['guid', 'state', 'email_id']):
            raise JsonSchemaValueException("" + (name_prefix or "data") + " must contain ['guid', 'state', 'email_id'] properties", value=data, name="" + (name_prefix or "data") + "", definition={'type': 'object', 'properties': {'email_id': {'type': 'string'}, 'first_name': {'type': 'string'}, 'last_name': {'type': 'string'}, 'guid': {'type': 'string', 'pattern': '^[a-fA-F0-9]{8}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{12}$'}, 'state': {'type': 'string'}}, 'required': ['guid', 'state', 'email_id']}, rule='required')
        data_keys = set(data.keys())
        if "email_id" in data_keys:
            data_keys.remove("email_id")
            data__emailid = data["email_id"]
            if not isinstance(data__emailid, (str)):
                raise JsonSchemaValueException("" + (name_prefix or "data") + ".email_id must be string", value=data__emailid, name="" + (name_prefix or "data") + ".email_id", definition={'type': 'string'}, rule='type')
        if "first_name" in data_keys:
            data_keys.remove("first_name")
            data__firstname = data["first_name"]
            if not isinstance(data__firstname, (str)):
                raise JsonSchemaValueException("" + (name_prefix or "data") + ".first_name must be string", value=data__firstname, name="" + (name_prefix or "data") + ".first_name", definition={'type': 'string'}, rule='type')
        if "last_name" in data_keys:
            data_keys.remove("last_name")
            data__lastname = data["last_name"]
            if not isinstance(data__lastname, (str)):
                raise JsonSchemaValueException("" + (name_prefix or "data") + ".last_name must be string", value=data__lastname, name="" + (name_prefix or "data") + ".last_name", definition={'type': 'string'}, rule='type')
        if "guid" in data_keys:
            data_keys.remove("guid")
            data__guid = data["guid"]
            validate___definitions_uuid(data__guid, custom_formats, (name_prefix or "data") + ".guid")
        if "state" in data_keys:
            data_keys.remove("state")
            data__state = data["state"]
            if not isinstance(data__state, (str)):
                raise JsonSchemaValueException("" + (name_prefix or "data") + ".state must be string", value=data__state, name="" + (name_prefix or "data") + ".state", definition={'type': 'string'}, rule='type')
    return data

def validate___definitions_uuid(data, custom_formats={}, name_prefix=None):
    if not isinstance(data, (str)):
        raise JsonSchemaValueException("" + (name_prefix or "data") + " must be string", value=data, name="" + (name_prefix or "data") + "", definition={'type': 'string', 'pattern': '^[a-fA-F0-9]{8}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{12}$'}, rule='type')
    if isinstance(data, str):
        if not REGEX_PATTERNS['^[a-fA-F0-9]{8}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{12}$'].search(data):
            raise JsonSchemaValueException("" + (name_prefix or "data") + " must match pattern ^[a-fA-F0-9]{8}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{12}$", value=data, name="" + (name_prefix or "data") + "", definition={'type': 'string', 'pattern': '^[a-fA-F0-9]{8}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{12}$'}, rule='pattern')
    return data

def validate___definitions_projectspec(data, custom_formats={}, name_prefix=None):
    if not isinstance(data, (dict)):
        raise JsonSchemaValueException("" + (name_prefix or "data") + " must be object", value=data, name="" + (name_prefix or "data") + "", definition={'type': 'object', 'properties': {'users': {'type': 'array', 'items': {'type': 'string'}}}, 'required': ['users']}, rule='type')
    data_is_dict = isinstance(data, dict)
    if data_is_dict:
        data_len = len(data)
        if not all(prop in data for prop in ['users']):
            raise JsonSchemaValueException("" + (name_prefix or "data") + " must contain ['users'] properties", value=data, name="" + (name_prefix or "data") + "", definition={'type': 'object', 'properties': {'users': {'type': 'array', 'items': {'type': 'string'}}}, 'required': ['users']}, rule='required')
        data_keys = set(data.keys())
        if "users" in data_keys:
            data_keys.remove("users")
            data__users = data["users"]
            if not isinstance(data__users, (list, tuple)):
                raise JsonSchemaValueException("" + (name_prefix or "data") + ".users must be array", value=data__users, name="" + (name_prefix or "data") + ".users", definition={'type': 'array', 'items': {'type': 'string'}}, rule='type')
            data__users_is_list = isinstance(data__users, (list, tuple))
            if data__users_is_list:
                data__users_len = len(data__users)
                for data__users_x, data__users_item in enumerate(data__users):
                    if not isinstance(data__users_item, (str)):
                        raise JsonSchemaValueException("" + (name_prefix or "data") + ".users[{data__users_x}]".format(**locals()) + " must be string", value=data__users_item, name="" + (name_prefix or "data") + ".users[{data__users_x}]".format(**locals()) + "", definition={'type': 'string'}, rule='type')
    return data

def validate___definitions_metadata(data, custom_formats={}, name_prefix=None):
    if not isinstance(data, (dict)):
        raise JsonSchemaValueException("" + (name_prefix or "data") + " must be object", value=data, name="" + (name_prefix or "data") + "", definition={'type': 'object', 'properties': {'name': {'type': 'string'}, 'guid': {'type': 'string', 'pattern': '^project-[a-z]{24}$'}, 'creator': {'type': 'string', 'pattern': '^[a-fA-F0-9]{8}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{12}$'}, 'project': {'type': 'string', 'pattern': '^project-[a-z]{24}$'}, 'labels': {'type': 'object', 'additionalProperties': {'type': 'string'}}}, 'required': ['name']}, rule='type')
    data_is_dict = isinstance(data, dict)
    if data_is_dict:
        data_len = len(data)
        if not all(prop in data for prop in ['name']):
            raise JsonSchemaValueException("" + (name_prefix or "data") + " must contain ['name'] properties", value=data, name="" + (name_prefix or "data") + "", definition={'type': 'object', 'properties': {'name': {'type': 'string'}, 'guid': {'type': 'string', 'pattern': '^project-[a-z]{24}$'}, 'creator': {'type': 'string', 'pattern': '^[a-fA-F0-9]{8}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{12}$'}, 'project': {'type': 'string', 'pattern': '^project-[a-z]{24}$'}, 'labels': {'type': 'object', 'additionalProperties': {'type': 'string'}}}, 'required': ['name']}, rule='required')
        data_keys = set(data.keys())
        if "name" in data_keys:
            data_keys.remove("name")
            data__name = data["name"]
            if not isinstance(data__name, (str)):
                raise JsonSchemaValueException("" + (name_prefix or "data") + ".name must be string", value=data__name, name="" + (name_prefix or "data") + ".name", definition={'type': 'string'}, rule='type')
        if "guid" in data_keys:
            data_keys.remove("guid")
            data__guid = data["guid"]
            validate___definitions_projectguid(data__guid, custom_formats, (name_prefix or "data") + ".guid")
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
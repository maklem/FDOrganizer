import json
from typing import Any, Optional, Union
from flask import Request, make_response

from .services.authentication import is_reviewer, organisation, user

from .entities.databases import Databases

def web_error(code: int, message:str, stacktrace: Optional[Union[str, list[str]]] = None, component = "SERVER"):
    error_data: dict[str, Union[str, list[str]]] = {
        'message': message,
        'component': component
    }
    if stacktrace is not None:
        error_data['stacktrace'] = stacktrace
    return make_response(json.dumps(error_data), code)

def web_response(code: int, message:Optional[str] = None, details: Optional[Union[dict[str, Any],list]] = None):
    if message is None and details is None:
        return make_response(code)
    if details is None:
        return make_response(json.dumps(
            {
                'message': message,
            }
        ), code)
    return make_response(json.dumps(details), code)
    
def is_owner(object_with_owner: dict[str, Any], owner) -> bool:
    return object_with_owner.get('owner') == owner

def can_read(restricted_object: dict[str, Any], request: Request) -> bool:
    if is_owner(restricted_object, user(request)):
        return True
    if not organisation(request) == restricted_object.get('organisation'):
        return False
    if is_reviewer(request):
        return True
    return False

def can_add_files(restricted_object: dict[str, Any], request: Request) -> bool:
    if is_owner(restricted_object, user(request)):
        return True
    return False

def can_delete_files(restricted_object: dict[str, Any], request: Request) -> bool:
    if is_owner(restricted_object, user(request)):
        return True
    return False

def can_delete_packages(restricted_object: dict[str, Any], request: Request) -> bool:
    if is_owner(restricted_object, user(request)):
        return True
    return False

def can_update_metadata(restricted_object: dict[str, Any], request: Request) -> bool:
    if is_owner(restricted_object, user(request)):
        return True
    return False

def get_database_from_string(database_type: str) -> Databases:
# Only valid code starting with Python 3.10.
    match database_type:
        case 'folder':
            return Databases.FOLDERS
        case 'package':
            return Databases.PACKAGES
        case 'document':
            return Databases.DOCUMENTS
        case _:
            raise ValueError(f'Database for type {database_type} not found')
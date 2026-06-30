from functools import wraps
import json
import re
from typing import Any, Optional, Union
from flask import Request, make_response, request, render_template, Response
from requests import HTTPError

from .entities import Package, Databases

from .services.database import get

from .services.authentication import is_reviewer, organisation, user

def error_page(code: int = 500, errors: list[str] = []) -> tuple[str,int]:
    return render_template("error.html", errors=errors), code

def web_error(code: int, message:str, stacktrace: Optional[Union[str, list[str]]] = None, component = "SERVER") -> Response:
    error_data: dict[str, Union[str, list[str]]] = {
        'message': message,
        'component': component
    }
    if stacktrace is not None:
        error_data['stacktrace'] = stacktrace
    return make_response(json.dumps(error_data), code)

def web_error_database_connection(error: HTTPError) -> Response:
    if error.response is None:
        return web_error(500, "connection to database failed.", component= "DATABASE")
    return web_error(error.response.status_code, error.response.reason, component= "DATABASE")

def web_response(code: int, message:Optional[str] = None, details: dict[str, Any] | list[Any] | None = None) -> Response:
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
    if is_reviewer(request):
        if not organisation(request) == restricted_object.get('organisation'):
            return False
        return True
    return False

def can_read_folder(folder: dict[str, Any], request: Request) -> bool:
    if is_owner(folder, user(request)):
        return True
    if is_reviewer(request):
        package = Package.from_db(get(Databases.PACKAGES, folder['package_id']).json())
        if not organisation(request) == package.organisation:
            return False
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

def can_edit_name(restricted_object: dict[str, Any], request: Request) -> bool:
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

def can_read_metadata(restricted_object: dict[str, Any], request: Request) -> bool:
    if is_owner(restricted_object, user(request)):
        return True
    if is_reviewer(request):
        return True
    return False

def can_submit_package(restricted_object: dict[str, Any], request: Request) -> bool:
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
        
def json_body(api_method):
  @wraps(api_method)
  def unpack_json_body(*args, **kwargs):
    # Do something with your request here
    data = request.get_json()
    if not data:
      return web_error(400, "Request is missing body", component= "SERVER")
    for key, value in data.items():
        if value is None:
            return web_error(400, f'Request is missing information for {key}', component= "SERVER")
        snake_case_key = re.sub(r'[A-Z]', lambda x: f'_{x.group(0).lower()}', key)
        kwargs[snake_case_key] = value
    return api_method(*args, **kwargs)
  return unpack_json_body
import json
from typing import Any, Optional, Union
from flask import make_response

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
    
def owner(object_with_owner: dict[str, Any], owner) -> bool:
    return object_with_owner.get('owner') == owner

def get_parent_database(parent_type: str) -> Databases:
    # Only valid code starting with Python 3.10.
    # match parent_type:
    #     case 'folder':
    #         return Databases.FOLDERS
    #     case 'package':
    #         return Databases.PACKAGES
    #     case _:
    #         return Databases.PACKAGES
    if parent_type == 'folder':
        return Databases.FOLDERS
    else:
        return Databases.PACKAGES
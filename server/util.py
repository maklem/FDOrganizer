import json
from typing import Any, Optional, Union
from flask import make_response
from pkg_resources import resource_filename

def get_config() -> dict[str, Union[str, list[str]]]:
    with open(resource_filename(__name__, "./conf/config.json"), encoding="utf-8") as config:
        return json.load(config)

def web_error(code: int, message:str, stacktrace: Optional[str | list[str]] = None, component = "SERVER"):
    error_data: dict[str, str | list[str]] = {
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
    
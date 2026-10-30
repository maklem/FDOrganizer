import re
from functools import wraps
from pathlib import Path
from typing import Any

from flask import Request, Response, jsonify, make_response, render_template, request
from requests import HTTPError

from server.entities.errors import PathError

from .entities import Databases, Package
from .services.authentication import userdata
from .services.database import get


def error_page(code: int = 500, errors: list[str] | None = None) -> tuple[str, int]:
    if errors is None:
        errors = []
    return render_template("error.html", errors=errors), code


def web_error(
    code: int,
    message: str,
    stacktrace: str | list[str] | None = None,
    component="SERVER",
) -> Response:
    error_data: dict[str, str | list[str]] = {
        "message": message,
        "component": component,
    }
    if stacktrace is not None:
        error_data["stacktrace"] = stacktrace

    response = jsonify(error_data)
    response.status_code = code
    return response


def web_error_database_connection(error: HTTPError) -> Response:
    if error.response is None:
        return web_error(500, "connection to database failed.", component="DATABASE")
    return web_error(
        error.response.status_code, error.response.reason, component="DATABASE"
    )


def web_response(
    code: int,
    message: str | None = None,
    details: dict[str, Any] | list[Any] | None = None,
) -> Response:
    if message is None and details is None:
        return make_response(code)
    if details is None:
        response = jsonify({"message": message})
        response.status_code = code
        return response
    response = jsonify(details)
    response.status_code = code
    return response


def is_owner(object_with_owner: dict[str, Any], owner) -> bool:
    return object_with_owner.get("owner") == owner


def can_read(restricted_object: dict[str, Any], request: Request) -> bool:
    if is_owner(restricted_object, userdata().username):
        return True
    if userdata().reviewer:
        return userdata().organisation_id == restricted_object.get("organisation")
    return False


def can_read_folder(folder: dict[str, Any], request: Request) -> bool:
    if is_owner(folder, userdata().username):
        return True
    if userdata().reviewer:
        package = Package.from_db(get(Databases.PACKAGES, folder["package_id"]).json())
        return userdata().organisation_id == package.organisation
    return False


def can_add_files(restricted_object: dict[str, Any], request: Request) -> bool:
    return bool(is_owner(restricted_object, userdata().username))


def can_delete_files(restricted_object: dict[str, Any], request: Request) -> bool:
    return bool(is_owner(restricted_object, userdata().username))


def can_edit_name(restricted_object: dict[str, Any], request: Request) -> bool:
    return bool(is_owner(restricted_object, userdata().username))


def can_delete_packages(restricted_object: dict[str, Any], request: Request) -> bool:
    return bool(is_owner(restricted_object, userdata().username))


def can_update_metadata(restricted_object: dict[str, Any], request: Request) -> bool:
    return bool(is_owner(restricted_object, userdata().username))


def can_read_metadata(restricted_object: dict[str, Any], request: Request) -> bool:
    return can_read(restricted_object, request)


def can_submit_package(restricted_object: dict[str, Any], request: Request) -> bool:
    return bool(is_owner(restricted_object, userdata().username))


def get_database_from_string(database_type: str) -> Databases:
    # Only valid code starting with Python 3.10.
    match database_type:
        case "folder":
            return Databases.FOLDERS
        case "package":
            return Databases.PACKAGES
        case "document":
            return Databases.DOCUMENTS
        case _:
            raise ValueError(f"Database for type {database_type} not found")


def json_body(api_method):
    @wraps(api_method)
    def unpack_json_body(*args, **kwargs):
        # Do something with your request here
        data = request.get_json()
        if not data:
            return web_error(400, "Request is missing body", component="SERVER")
        for key, value in data.items():
            if value is None:
                return web_error(
                    400, f"Request is missing information for {key}", component="SERVER"
                )
            snake_case_key = re.sub(r"[A-Z]", lambda x: f"_{x.group(0).lower()}", key)
            kwargs[snake_case_key] = value
        return api_method(*args, **kwargs)

    return unpack_json_body


ALLOWED_FILE_EXPRESSION = re.compile(r"^[A-Za-z0-9._ \-\+\=\[\]\(\)\@]+$")


def is_valid_filename(name: str | None) -> bool:
    if name is None:
        return False
    if "\x00" in name or any(ord(c) < 32 for c in name):
        return False
    if "/" in name or "\\" in name:
        return False
    if name.startswith("-"):
        return False
    if name in ("", ".", ".."):
        return False
    if Path(name).name != name:
        return False

    return bool(ALLOWED_FILE_EXPRESSION.match(name))


def safe_join(base_path: str | Path, *segments: str) -> Path:
    base = Path(base_path)

    for segment in segments:
        if not is_valid_filename(segment):
            raise PathError(f"could not safely join paths: '{base}' and '{segment}'")

        new = base / segment
        if not new.resolve().is_relative_to(base.resolve()):
            raise PathError(f"could not safely join paths: '{base}' and '{segment}'")

        base = new

    return base

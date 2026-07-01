from jinja2.exceptions import UndefinedError
import json
from flask import Response, request
from requests import HTTPError
import traceback

from server.export_utils import create_structmap, create_file_list, build_sip_metadata, check_structmap, create_package_data

from .shared import update_package_state
from .entities import Package, Databases
from .entities.errors import XMLValidationError

from .services.authentication import organisation, user
from .services.database import find, get, update

from .util import can_submit_package, can_update_metadata, json_body, web_error, web_error_database_connection, web_response
from server import APP


@APP.route("/archive/packages", methods=["GET"])
def get_archive_packages():

    query = {
        "selector": {
            "owner": user(request),
            "organisation": organisation(request)
        }
    }

    try:
        packages = find(Databases.PACKAGES, json.dumps(query)).json().get('docs')
    except HTTPError as error:
        return web_error_database_connection(error)
    return web_response(200, details = [Package.convert(x) for x in packages])

@APP.route("/archive/<package_id>/settings", methods=["PATCH"])
@json_body
def change_package_settings(package_id, settings: dict) -> Response:

    package = get(Databases.PACKAGES, package_id).json()
    if not can_update_metadata(package, request):
        return web_error(401, "You don't have permission to delete this content", component= "SERVER")
    try:
        updated_package = update(Databases.PACKAGES, package_id, {'archive_settings': settings}).json()
    except HTTPError as error:
        return web_error_database_connection(error)
    return web_response(200, message="Update successful", details = updated_package)

@APP.route("/archive/check-requirements", methods=["GET"])
def check_export_requirements(package_id: str):
    package: Package = Package.from_dict(get(Databases.PACKAGES, package_id).json())
    requirements = {
        'contains_files': True,
        'has_metadata': True,
    }
    if package.metadata is None:
        requirements['has_metadata'] = False
    if not package.documents and not package.folders:
        requirements['contains_files'] = False
    return web_response(200, details = requirements)


def check_package_validity(package: Package) -> list[str]:
    try:
        package_data = create_package_data(package)
        structmap = create_structmap(package)
        file_list = create_file_list(structmap)
        errors = check_structmap("", structmap)
        if errors:
            return errors
        build_sip_metadata(package_data, file_list, structmap)
    except UndefinedError:
        errors.append(f"*Something* is wrong...\n\n{traceback.format_exc()}")
    except TypeError:
        errors.append(f"*Something* is wrong...\n\n{traceback.format_exc()}")
    except XMLValidationError as error:
        errors.append(f"The generated metadata does not satisfy the schema requirements. ({str(error)})")
    return errors

@APP.route("/archive/check/<package_id>", methods=["GET"])
def check_package(package_id: str)->Response:
    try:
        package = Package.from_db(get(Databases.PACKAGES, package_id).json())
    except KeyError:
        return web_response(200, details={"status": "error", 'details': ["Could not read package from database. A"]})
    except HTTPError:
        return web_response(200, details={"status": "error", 'details': ["Could not read package from database. B"]})
    if errors := check_package_validity(package):
        return web_response(200, details={'status': "error", 'details': errors})
    
    return web_response(200, details={'status': 'success'})

@APP.route("/archive/submit/<package_id>", methods=["POST"])
def submit_for_review(package_id: str) -> Response:
    try:
        package = get(Databases.PACKAGES, package_id).json()
    except HTTPError as error:
        return web_error_database_connection(error)
    if not can_submit_package(package, request):
        return web_error(401, "You don't have permission to submit this package", component= "SERVER")
    if package.get('status') not in ['active', 'rework']:
        return web_error(400, "Package cannot be submitted for review in status {}".format(package.get('status')), component= "SERVER")

    if errors := check_package_validity(Package.from_db(package)):
        return web_error(400, "Could not submit package for review.\nErrors:\n"+ "\n".join(" * " + e for e in errors))
    
    update_package_state(package_id, "review")
    return web_response(200, message="Package submitted for review")
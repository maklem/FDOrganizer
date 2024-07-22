import json
from flask import Response, request
from requests import HTTPError #type: ignore

from .shared import update_package_state


from .entities import Package, Databases

from .services.authentication import organisation, user
from .services.database import find, get, update

from .util import can_submit_package, can_update_metadata, web_error, web_response
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
        return web_error(error.response.status_code, error.response.reason, component= "DATABASE")
    return web_response(200, details = [Package.convert(x) for x in packages])

@APP.route("/archive/<package_id>/settings", methods=["PATCH"])
def change_package_settings(package_id):

    if request.json is None or request.json.get('settings') is None:
        return web_error(400, "Request is missing information", component= "SERVER")

    package_settings = request.json.get('settings')
    package = get(Databases.PACKAGES, package_id).json()
    if not can_update_metadata(package, request):
        return web_error(401, "You don't have permission to delete this content", component= "SERVER")
    try:
        updated_package = update(Databases.PACKAGES, package_id, {'archive_settings': package_settings}).json()
    except HTTPError as error:
        return web_error(error.response.status_code, error.response.reason, component= "DATABASE")
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

@APP.route("/archive/submit/<package_id>", methods=["POST"])
def submit_for_review(package_id: str) -> Response:
    try:
        package = get(Databases.PACKAGES, package_id).json()
    except HTTPError as error:
        return web_error(error.response.status_code, error.response.reason, component= "DATABASE")
    if not can_submit_package(package, request):
        return web_error(401, "You don't have permission to submit this package", component= "SERVER")
    update_package_state(package_id, "review")
    return web_response(200, message="Package submitted for review")
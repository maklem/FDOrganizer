import json
from flask import request
from requests import HTTPError #type: ignore


from .entities import Package, Databases

from .services.authentication import organisation, user
from .services.database import find, get, update

from .util import can_update_metadata, web_error, web_response
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
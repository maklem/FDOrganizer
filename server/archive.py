import json
from flask import request
from requests import HTTPError


from .entities.package import Package
from .entities.databases import Databases

from .services.authentication import user
from .services.database import find, get, update

from .util import owner, web_error, web_response
from server import APP


@APP.route("/archive/packages", methods=["GET"])
def get_archive_packages():

    username = user(request)
    query = {
        "selector": {
            "owner": username,
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
    if not owner(package, user(request)):
        return web_error(401, "You don't have permission to delete this content", component= "SERVER")

    try:
        updated_package = update(Databases.PACKAGES, package_id, {'archive_settings': package_settings}).json()
    except HTTPError as error:
        return web_error(error.response.status_code, error.response.reason, component= "DATABASE")
    return web_response(200, message="Update successful")
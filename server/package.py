import json
import time
from flask import request
from requests import HTTPError

from server.entities.package import Package
from server.entities.databases import Databases

from server.services.authentication import user
from server.services.database import delete, find, post

from server.util import web_error, web_response
from server import APP


@APP.route("/package/all", methods=["GET"])
def get_packages():

    username = user(request)
    query = {
        "selector": {
            "owner": username,
            "status": "active"
        }
    }

    try:
        packages = find(Databases.PACKAGES, json.dumps(query)).json().get('docs')
    except HTTPError as error:
        return web_error(error.response.status_code, error.response.reason, component= "DATABASE")
    return web_response(200, details = list(map(Package.convert, packages)))

@APP.route("/package", methods=["PUT"])
def create_package():
    username = user(request)
    now = round(time.time()*1000)
    if not request.json:
        return web_error(400, "Not a valid package name", component= "SERVER")
    name = request.json.get('name')
    package = Package(name=name, status='active', documents=[], folders=[], owner=username, created=now, last_changed=now)
    try:
        package_created = post(Databases.PACKAGES, package.to_json())
    except HTTPError as error:
        return web_error(error.response.status_code, error.response.reason, component= "DATABASE")
    return web_response(200, 'Success', package_created.json())

@APP.route("/package/<id>", methods=["DELETE"])
def delete_package(id):
    #TODO delete dependent folders + documents
    try:
        package_deleted = delete(Databases.PACKAGES, id)
    except HTTPError as error:
        return web_error(error.response.status_code, error.response.reason, component= "DATABASE")
    return web_response(200, 'Success', package_deleted.json())
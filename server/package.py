import json
import time
from typing import Any
from flask import request
from requests import HTTPError

from server.entities.package import Package
from server.entities.databases import Databases
from server.util import web_error, web_response
from server.services.authentication import user
from server.services.database import delete, get, post
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
        packages = get(Databases.PACKAGES, json.dumps(query))
    except HTTPError as error:
        return web_error(error.response.status_code, error.response.reason, component= "DATABASE")
    return web_response(200, details = convert_packages(packages.json().get('docs')))

@APP.route("/package", methods=["PUT"])
def create_package():
    username = user(request)
    now = round(time.time()*1000)
    if not request.json:
        return web_error(400, "Kein gültiger Name für ein Package", component= "SERVER")
    name = request.json.get('name')
    package = Package(name=name, status='active', documents=[], folders=[], owner=username, created=now, last_changed=now)
    try:
        package_created = post(Databases.PACKAGES, package.to_json())
    except HTTPError as error:
        return web_error(error.response.status_code, error.response.reason, component= "DATABASE")
    return web_response(200, 'Success', package_created.json())

@APP.route("/package/<id>", methods=["DELETE"])
def delete_package(id):
    try:
        package_deleted = delete(Databases.PACKAGES, id)
    except HTTPError as error:
        return web_error(error.response.status_code, error.response.reason, component= "DATABASE")
    return web_response(200, 'Success', package_deleted.json())

def convert_package(package: dict[str, Any]) -> Package:
    pkg = Package.from_dict(package)
    pkg.id = package.get('_id')
    return pkg.to_dict()

def convert_packages(packages: list[dict[str, Any]]) -> list[Package]:
    return list(map(convert_package, packages))
import json
import time
from typing import Any
from flask import request
from requests import HTTPError

from server.entities.document import Document
from server.entities.folder import Folder
from server.entities.package import Package
from server.entities.databases import Databases

from server.services.authentication import user
from server.services.database import delete, find, post, update

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
        packages = find(Databases.PACKAGES, json.dumps(query))
    except HTTPError as error:
        return web_error(error.response.status_code, error.response.reason, component= "DATABASE")
    return web_response(200, details = convert_packages(packages.json().get('docs')))

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

@APP.route("/package/<id>/content", methods=["GET"])
def get_package(id):

    username = user(request)
    query = {
        "selector": {
            "_id": id,
        }
    }

    try:
        packages = find(Databases.PACKAGES, json.dumps(query))
    except HTTPError as error:
        return web_error(error.response.status_code, error.response.reason, component= "DATABASE")
    package = packages.json().get('docs')[0]
    if package.get('owner') != username:
                return web_error(401, "You don't have permission to view this content", component= "SERVER")
    return web_response(200, details = convert_package(package))

@APP.route("/package/<id>", methods=["DELETE"])
def delete_package(id):
    #TODO delete dependent folders + documents
    try:
        package_deleted = delete(Databases.PACKAGES, id)
    except HTTPError as error:
        return web_error(error.response.status_code, error.response.reason, component= "DATABASE")
    return web_response(200, 'Success', package_deleted.json())

@APP.route("/package/content", methods=["POST"])
def get_content():
    if not request.json:
        return web_error(400, "No request body", component= "SERVER")
    folders = request.json.get('folders')
    documents = request.json.get('documents')

    try:
        found_folders =find(
            Databases.FOLDERS,
            json.dumps(content_query(folders))
        ).json().get('docs')
        found_documents = find(
            Databases.DOCUMENTS,
            json.dumps(content_query(documents))
        ).json().get('docs')
    except HTTPError as error:
        return web_error(error.response.status_code, error.response.reason, component= "DATABASE")
    return web_response(200, details = {"folders": list(map(convert_folder, found_folders)), "documents": list(map(convert_document, found_documents)) })

@APP.route("/package/folder", methods=["PUT"])
def create_folder():
    # Check incoming request for errors
    if not request.json:
        return web_error(400, "Request is missing information", component= "SERVER")
    # Get Infos from request header and body
    username = user(request)
    name = request.json.get('name')
    parent = request.json.get('parent')
    parent_type = request.json.get('parentType')
    # Create new folder object
    folder = Folder(name=name, documents=[], folders=[], owner=username)
    #Persist folder
    try:
        folder_created = post(Databases.FOLDERS, folder.to_json())
        print(folder.to_json())
        print(folder_created.json())
    except HTTPError as error:
        return web_error(error.response.status_code, error.response.reason, component= "DATABASE")
    except KeyError as error:
        return web_error(400, error.args[0], component= "DATABASE")
    #Update parent to include folder
    try:
        updated_package = update_parent_entity(
            folder_id = folder_created.json().get('id'),
            parent_type = parent_type,
            parent = parent
            )
    except HTTPError as error:
        # Delete new folder on error
        delete(Databases.FOLDERS, folder_created.json().get('id'))
        return web_error(error.response.status_code, error.response.reason, component= "DATABASE")
    print(updated_package.json())
    return web_response(200, 'Success', folder_created.json())




def convert_package(package_in: dict[str, Any]) -> dict[str, Any]:
    package_out: Package = Package.from_dict(package_in)
    package_out.id = package_in.get('_id')
    return package_out.to_dict()

def convert_folder(folder_in: dict[str, Any]) -> dict[str, Any]:
    folder_out: Folder = Folder.from_dict(folder_in)
    folder_out.id = folder_in.get('_id')
    return folder_out.to_dict()

def convert_document(document_in: dict[str, Any]) -> dict[str, Any]:
    document_out: Document = Document.from_dict(document_in)
    document_out.id = document_in.get('_id')
    return document_out.to_dict()

def convert_packages(packages: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return list(map(convert_package, packages))

def content_query(id_array):
    return {
        "selector": {
            "_id": {
                "$in": id_array
            }
        }
    }

def update_parent_entity(folder_id, parent_type, parent):
    if parent_type == "package":
        parent_db = Databases.PACKAGES
        now = round(time.time()*1000)
        changes = {
            "folders": {
                "method": "append",
                "value": folder_id
            },
            "last_changed": now
        }
    else:
        parent_db = Databases.FOLDERS
        changes = {
            "folders": {
                "method": "append",
                "value": folder_id
            }
        }

    return update(parent_db, parent, changes)
    
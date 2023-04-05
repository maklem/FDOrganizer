import json
import time
from flask import request
from requests import HTTPError

from .shared import delete_document, delete_folder

from .entities.package import Package
from .entities.databases import Databases

from .services.authentication import user
from .services.database import delete, find, get, post

from .util import owner, web_error, web_response
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
    return web_response(200, details = [Package.convert(x) for x in packages])

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

@APP.route("/package/<package_id>", methods=["DELETE"])
def delete_package(package_id):
    #TODO delete dependent folders + documents
    package = get(Databases.PACKAGES, package_id).json()
    if not owner(package, user(request)):
        return web_error(401, "You don't have permission to delete this content", component= "SERVER")

    failed_folders = []
    failed_documents = []

    # Delete folders, rollback for all if failed
    for folder in package.get('folders'):
        try:
            if not delete_folder(folder):
                failed_folders.append(folder)
        except HTTPError as error:
            failed_folders.append(folder)
    if len(failed_folders) > 0:
        # TODO: Rollback for deletion 
        return web_error(500, f'{len(failed_folders)} could not be deleted', component= "DATABASE")
    
    # Delete documents, rollback for all if failed
    for document in package.get('documents'):
        try:
            if not delete_document(document):
                failed_documents.append(document)
        except HTTPError as error:
            failed_documents.append(document)
    if len(failed_documents) > 0:
        # TODO: Rollback for deletion 
        return web_error(500, f'{len(failed_documents)} could not be deleted', component= "DATABASE")
    
    # Delete metadata of folder, rollback for all, if failed
    if package.get('metadata') is not None:
        try:
            delete(Databases.METADATA, package.get('metadata'))
        except HTTPError as error:
            # TODO: Rollback for deletion 
            return web_error(error.response.status_code, error.response.reason, component= "DATABASE")
        
    # Delete the folder itself
    try:
        package_deleted = delete(Databases.PACKAGES, package_id).json()
    except HTTPError as error:
        # TODO: Rollback for deletion 
        return web_error(error.response.status_code, error.response.reason, component= "DATABASE")


    return web_response(200, 'Success', package_deleted)

from hashlib import md5, sha512
import io
import json
import os
import time

from werkzeug.datastructures import FileStorage
from flask import Response, request
from requests import HTTPError #type: ignore
from server import APP
from .shared import delete_folder, persist_documents

from .entities import Folder, Databases, Document, Package

from .util import can_add_files, can_delete_files, can_read, can_read_folder, json_body, web_error, web_response, get_database_from_string
from .services.authentication import user
from .services.database import attach, delete, find, get, post, update


@APP.route("/package/<package_id>/content", methods=["GET"])
def get_package(package_id):
    # Get package from DB
    try:
        package = get(Databases.PACKAGES, package_id).json()
    except HTTPError as error:
        return web_error(error.response.status_code, error.response.reason, component= "DATABASE")
    # Check if user has rights to view the package
    if not can_read(package, request):
        return web_error(401, "You don't have permission to view this content", component= "SERVER")
    # Get package content from DB
    try:
        content = get_content(package.get('folders'), package.get('documents'))
    except HTTPError as error:
        return web_error(error.response.status_code, error.response.reason, component= "DATABASE")
    # Return package and its content
    result = {'package': Package.convert(package)} | content
    return web_response(200, details = result)

@APP.route("/folder/<folder_id>/content", methods=["GET"])
def get_folder_content(folder_id):
    # Get folder from DB
    try:
        folder = get(Databases.FOLDERS, folder_id).json()
    except HTTPError as error:
        return web_error(error.response.status_code, error.response.reason, component= "DATABASE")
    # Check if user has rights to view the folder contents
    if not can_read_folder(folder, request):
        return web_error(401, "You don't have permission to view this content", component= "SERVER")
    # Get folder content from DB
    try:
        content = get_content(folder.get('folders'), folder.get('documents'))
    except HTTPError as error:
        return web_error(error.response.status_code, error.response.reason, component= "DATABASE")
    # Return folder contents
    return web_response(200, details = content)

@APP.route("/package/folder", methods=["PUT"])
@json_body
def create_folder(name: str, parent: str, parent_type: str) -> Response:

    # Check ownership of parent, to determine if creation of subelement is valid
    package_or_folder = get(get_database_from_string(parent_type), parent).json()
    if not can_add_files(package_or_folder, request):
        return web_error(401, "You don't have permission to edit this content", component= "SERVER")
    # Create new folder object
    username = user(request)
    if parent_type == 'package':
        package_id =package_or_folder.get('_id')
    else:
        package_id = package_or_folder.get('package_id')
    if package_id is None:
        return web_error(500, "Package ID for creating the folder not found", component= "SERVER")
    folder = Folder(name=name, documents=[], folders=[], owner=username, package_id=package_id)
    #Persist folder
    try:
        folder_created = post(Databases.FOLDERS, folder.to_json()).json()
    except HTTPError as error:
        return web_error(error.response.status_code, error.response.reason, component= "DATABASE")
    except KeyError as error:
        return web_error(400, error.args[0], component= "DATABASE")
    #Update parent to include folder
    changes = {
        'folders': {
            "method": "append",
            "value": folder_created.get('id')
        }
    }
    try:
        update(get_database_from_string(parent_type), parent, changes)
        # TODO: Get package id for modify_package()
    except HTTPError as error:
        # Delete new folder on error
        delete_folder(folder_created.get('id'))
        return web_error(error.response.status_code, error.response.reason, component= "DATABASE")
    return web_response(200, 'Success', folder_created)
    
@APP.route("/package/documents", methods=["POST"])
def create_documents():
    if int(request.headers['Content-Length']) > int(APP.config['MAX_CONTENT_LENGTH']):
        return web_error(413, "File is too large to be processed", component= "SERVER")
    # Get Infos from request header and body
    username = user(request)
    parent = request.form.get('parent')
    parent_type = request.form.get('parentType')
    if parent is None or parent_type is None:
        return web_error(400, "Request is missing information", component= "SERVER")

    # Check ownership of parent, to determine if creation of subelement is valid
    package_or_folder = get(get_database_from_string(parent_type), parent).json()
    if not can_add_files(package_or_folder, request):
        return web_error(401, "You don't have permission to edit this content", component="SERVER")
    
    #Create documents for uploaded files
    file_document_pairs = []
    failed_files= []
    for file in request.files.values():
        try:
            file_document_pairs.append(create_file_document_pair(file, username))
        except HTTPError as error:
            failed_files.append({'file': file.filename, 'error': error.args[0]})

    #Persist documents and files in DB
    persisted_documents = persist_documents(file_document_pairs, parent, parent_type)
    
    persisted_documents['failed'] = failed_files
    return web_response(200, 'Success', persisted_documents)

@APP.route("/package/document/<document_id>", methods=["DELETE"])
def delete_document_from_package(document_id):
    # Check incoming request for errors
    if not request.json:
        return web_error(400, "Request is missing information", component= "SERVER")
    
    #Check ownership
    document = get(Databases.DOCUMENTS, document_id).json()
    if document is None:
        return web_error(400, f'Document with id {document_id} does not exist', component= "SERVER")
    if not can_delete_files(document, request):
        return web_error(401, "You don't have permission to delete this content", component= "SERVER")
    
    # Get Infos from request header and body
    parent = request.json.get('parent')
    parent_type = request.json.get('parentType')

    # Delete document reference from parent object first
    changes = {
        'documents': {
            'method': 'remove',
            'value': document_id
        }
    }
    try:
        update(get_database_from_string(parent_type), parent, changes)
        # TODO: Get package id for modify_package()
    except HTTPError as error:
        return web_error(error.response.status_code, error.response.reason, component= "DATABASE")

    # After the reference is sucessfully deleted, delete document itself
    try:
        delete(Databases.DOCUMENTS, document_id)
    except HTTPError as error:
        return web_error(error.response.status_code, error.response.reason, component= "DATABASE")
    return web_response(200, 'Document deleted')


@APP.route("/package/folder/<folder_id>", methods=["DELETE"])
def delete_folder_from_package(folder_id):
    # Check incoming request for errors
    if not request.json:
        return web_error(400, "Request is missing information", component= "SERVER")
    # Get Infos from request header and body
    folder = get(Databases.FOLDERS, folder_id).json()

    if folder is None: 
        return web_error(400, f'Folder with id {folder_id} does not exist', component= "SERVER")
    if not can_delete_files(folder, request):
        return web_error(401, "You don't have permission to delete this content", component= "SERVER")
    
    # Get Infos from request header and body
    parent = request.json.get('parent')
    parent_type = request.json.get('parentType')

    # Delete document reference from parent object first
    changes = {
        'folders': {
            'method': 'remove',
            'value': folder_id
        }
    }
    try:
        update(get_database_from_string(parent_type), parent, changes)
        # TODO: Get package id for modify_package()
    except HTTPError as error:
        return web_error(error.response.status_code, error.response.reason, component= "DATABASE")

    # After the reference is sucessfully deleted, delete document itself
    if not delete_folder(folder_id):
        return web_error(500, "Folder could not be deleted successfully", component= "DATABASE")
    return web_response(200, 'Folder deleted')


def create_file_document_pair(file: FileStorage, username: str):
    result = {'success': False}
    # Check uploaded file integrity
    if file is None:
        raise HTTPError('No file provided')
    if not file.filename:
        raise HTTPError('No filename available')
    
    file_data = file.read()
    hash_md5 = md5(file_data).hexdigest()
    hash_sha512 = sha512(file_data).hexdigest()
    outfile = io.BytesIO(file_data)
    outfile.seek(0)

    # Create Document from uploaded information + file
    document = Document(
        name=file.filename,
        size=file.seek(0, os.SEEK_END),
        type=file.mimetype,
        hash_md5=hash_md5,
        hash_sha512=hash_sha512,
        source="manual upload",
        owner=username)
    return {'document': document, 'file': outfile }

            
def content_query(id_array):
    return {
        "selector": {
            "_id": {
                "$in": id_array
            }
        },
        "limit": 1000
    }

def modify_package(package_id: str):
    now = round(time.time()*1000)
    changes = {
        "last_changed": now
    }
    return update(Databases.PACKAGES, package_id, changes)

def get_content(folders: list[str], documents: list[str]):
    found_folders =find(
        Databases.FOLDERS,
        json.dumps(content_query(folders))
    ).json().get('docs')
    found_documents = find(
        Databases.DOCUMENTS,
        json.dumps(content_query(documents))
    ).json().get('docs')

    return {"folders": [Folder.convert(x) for x in found_folders], "documents": [Document.convert(x) for x in found_documents] }

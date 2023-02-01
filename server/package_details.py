import json
import os
import time
from typing import Any
from flask import request
from requests import HTTPError, Response
from server import APP

from server.entities.folder import Folder
from server.entities.databases import Databases
from server.entities.couch_document import CouchDocument
from server.entities.document import Document
from server.entities.package import Package

from server.util import web_error, web_response
from server.services.authentication import user
from server.services.database import attach, delete, find, get, post, update


@APP.route("/package/<package_id>/content", methods=["GET"])
def get_package(package_id):
    # Get package from DB
    try:
        package = get(Databases.PACKAGES, package_id).json()
    except HTTPError as error:
        return web_error(error.response.status_code, error.response.reason, component= "DATABASE")
    # Check if user has rights to view the package
    username = user(request)
    if package.get('owner') != username:
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
    username = user(request)
    if folder.get('owner') != username:
        return web_error(401, "You don't have permission to view this content", component= "SERVER")
    # Get folder content from DB
    try:
        content = get_content(folder.get('folders'), folder.get('documents'))
    except HTTPError as error:
        return web_error(error.response.status_code, error.response.reason, component= "DATABASE")
    # Return folder contents
    return web_response(200, details = content)

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
    except HTTPError as error:
        return web_error(error.response.status_code, error.response.reason, component= "DATABASE")
    except KeyError as error:
        return web_error(400, error.args[0], component= "DATABASE")
    #Update parent to include folder
    changes = {
        'folders': {
            "method": "append",
            "value": folder_created.json().get('id')
        }
    }
    try:
        update(get_parent_database(parent_type), parent, changes)
        # TODO: Get package id for modify_package()
    except HTTPError as error:
        # Delete new folder on error
        delete(Databases.FOLDERS, folder_created.json().get('id'))
        return web_error(error.response.status_code, error.response.reason, component= "DATABASE")
    return web_response(200, 'Success', folder_created.json())
    
@APP.route("/package/documents", methods=["POST"])
def create_documents():
    # Get Infos from request header and body
    username = user(request)
    parent = request.form.get('parent')
    parent_type = request.form.get('parentType')
    documents = {
        'failed': [],
        'success': []
    }
    for file in request.files.values():
        result = create_document(file, username)
        if not result.get('success'):
            documents['failed'].append({'file': file.filename, 'error': result.get('error')})
        else:
            documents['success'].append({'file': file.filename, 'document_id': result.get('document_id')})

    #Update parent to include documents
    changes = {
        "documents": {
            "method": 'extend',
            "value": list(map(lambda doc: doc.get('document_id'), documents['success']))
        }
    }
    try:
        update(get_parent_database(parent_type), parent, changes)
        # TODO: Get package id for modify_package()
    except HTTPError as error:
        # Delete new document on error
        # delete(Databases.DOCUMENTS, document_created.json().get('id'))
        return web_error(error.response.status_code, error.response.reason, component= "DATABASE")
    return web_response(200, 'Success', documents)

@APP.route("/package/document/<document_id>", methods=["DELETE"])
def delete_document(document_id):
    # Check incoming request for errors
    if not request.json:
        return web_error(400, "Request is missing information", component= "SERVER")
    # Get Infos from request header and body
    username = user(request)
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
        update(get_parent_database(parent_type), parent, changes)
        # TODO: Get package id for modify_package()
    except HTTPError as error:
        return web_error(error.response.status_code, error.response.reason, component= "DATABASE")

    # After the reference is sucessfully deleted, delete document itself
    try:
        print(parent, parent_type, username)
        delete(Databases.DOCUMENTS, document_id)
    except HTTPError as error:
        return web_error(error.response.status_code, error.response.reason, component= "DATABASE")
    return web_response(200, 'Document deleted')


def create_document(file, username):
    result = {'success': False}
    # Check uploaded file integrity
    if file is None:
        return result | {
            'error': web_error(400, 'No file content detected')
        }
    if not file.filename:
        return result | {
            'error': web_error(400, 'No filename available')
        }   
    # Create Document from uploaded information + file
    document = Document(
        name=file.filename,
        size=file.seek(0, os.SEEK_END),
        type=file.mimetype,
        source="manual upload",
        is_stored=True,
        owner=username)
    document_created = create_document_with_attachement(file, document)

    return {
        'success': True,
        'document_id': document_created.json().get('id')
    }
            

def create_document_with_attachement(file, document: Document) -> Response:
    # Create initial document in DB
    document_created = post(Databases.DOCUMENTS,document.to_json())  # type: ignore
    # Attach uploaded file to created document
    response_document = CouchDocument(document_created.json())
    attachment_response = attach(Databases.DOCUMENTS, response_document, file)

    return attachment_response

def content_query(id_array):
    return {
        "selector": {
            "_id": {
                "$in": id_array
            },
            "owner": 'test'
        }
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

    return {"folders": list(map(Folder.convert, found_folders)), "documents": list(map(Document.convert, found_documents)) }

def get_parent_database(parent_type) -> Databases:
    # Only valid code starting with Python 3.10.
    # match parent_type:
    #     case 'folder':
    #         return Databases.FOLDERS
    #     case 'package':
    #         return Databases.PACKAGES
    #     case _:
    #         return Databases.PACKAGES
    if parent_type == 'folder':
        return Databases.FOLDERS
    else:
        return Databases.PACKAGES
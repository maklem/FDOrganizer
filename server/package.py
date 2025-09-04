import io
import json
import os
import pathlib
import time
import zipfile
from dataclasses import dataclass
from zipfile import ZipFile

from flask import Response, request
from requests import HTTPError #type: ignore
from werkzeug.datastructures import FileStorage


from .package_details import create_file_document_pair

from .shared import create_document_with_attachement, delete_document, delete_folder

from .entities import Package, Databases, Folder

from .services.authentication import user, organisation
from .services.database import delete, find, get, post, update

from .util import can_delete_packages, can_edit_name, json_body, web_error, web_response
from server import APP


@dataclass
class Directory:
    name: str
    folders: list["Directory"]
    files: list[zipfile.Path]


@APP.route("/package/all", methods=["GET"])
def get_packages():

    query = {
        "selector": {
            "owner": user(request),
            "status": "active",
            "organisation": organisation(request)
        },
        "limit": 1000
    }

    try:
        packages = find(Databases.PACKAGES, json.dumps(query)).json().get('docs')
    except HTTPError as error:
        return web_error(error.response.status_code, error.response.reason, component= "DATABASE")
    return web_response(200, details = [Package.convert(x) for x in packages])

@APP.route("/package", methods=["PUT"])
@json_body
def create_package(name: str) -> Response:
    username = user(request)
    organisation_name = organisation(request)
    now = round(time.time()*1000)
    package = Package(name=name, status='active', documents=[], folders=[], owner=username, organisation=organisation_name, created=now, last_changed=now)
    try:
        package_created = post(Databases.PACKAGES, package.to_json())
    except HTTPError as error:
        return web_error(error.response.status_code, error.response.reason, component= "DATABASE")
    return web_response(200, 'Success', package_created.json())

@APP.route("/package/<package_id>", methods=["DELETE"])
def delete_package(package_id):
    #TODO delete dependent folders + documents
    package = get(Databases.PACKAGES, package_id).json()
    if not can_delete_packages(package, request):
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

@APP.route("/package/<package_id>/rename", methods=["PATCH"])
@json_body
def rename_package(package_id: str, name: str) -> Response:
    package = get(Databases.PACKAGES, package_id).json()
    if not can_edit_name(package, request):
        return web_error(401, "You don't have permission to change the name of this package", component= "SERVER")
    changes = {
        "name": name
    }
    try:
        update(Databases.PACKAGES, package_id, changes)
    except HTTPError as error:
        return web_error(error.response.status_code, error.response.reason, component= "DATABASE")
    return web_response(200, 'Success')

@APP.route("/package/zip", methods=["PUT"])
def create_package_from_zip() -> Response:
    print(request.form.to_dict())
    zip_temp_path = './TEMP/TEMP.zip'
    project_zip: FileStorage = next(request.files.values())
    project_zip.save(zip_temp_path)
    with ZipFile(zip_temp_path, 'r') as zip_ref:
        zip_path = zipfile.Path(zip_ref)
        # Recursively build directory structure tree
        directory = recurse_directory(zip_path)
        # Build new package for zip content
        username = user(request)
        package_id = create_package_in_db(pathlib.Path(project_zip.filename).stem, username, organisation(request))
        # Create folders and documents
        folder_ids = [create_folder_from_zip(folder_entry, zip_ref, username, package_id) for folder_entry in directory.folders]
        doc_ids = [create_document_from_zip(file_entry, username) for file_entry in directory.files]
        # Update package with new folder and document ids
        update(Databases.PACKAGES, package_id, {'folders': folder_ids, 'documents': doc_ids})
    os.remove(zip_temp_path)
    return web_response(200, 'Success')


def recurse_directory(path: zipfile.Path) -> Directory:
    directory = Directory(path.name, [], [])
    for obj in path.iterdir():
        if obj.is_dir():
            new_directory = recurse_directory(obj)
            directory.folders.append(new_directory)
        else:
            directory.files.append(obj)
    return directory

def create_folder_from_zip(directory: Directory, zipfile: ZipFile, username: str, package_id: str):
    
    folder_ids = [create_folder_from_zip(folder_entry, zipfile, username, package_id) for folder_entry in directory.folders]
    doc_ids = [create_document_from_zip(file_entry, username) for file_entry in directory.files]
    
    # Differentiate between top level (package) and nested levels (folder)
    folder = Folder(name=directory.name, documents=doc_ids, folders=folder_ids, owner=username, package_id=package_id)
    persisted_entity = post(Databases.FOLDERS, folder.to_json()).json()

    return persisted_entity['id']

def create_document_from_zip(file_info: zipfile.Path, username):
    file = io.BytesIO(file_info.read_bytes())
    storage = FileStorage(file)
    storage.filename = file_info.name
    file_doc_pair = create_file_document_pair(storage, username)
    return create_document_with_attachement(file_doc_pair['file'], file_doc_pair['document'])

def create_package_in_db(name:str, owner: str, organisation: str) -> str:
    now = round(time.time()*1000)
    package = Package(name=name, status='active', documents=[], folders=[], owner=owner, organisation=organisation, created=now, last_changed=now)
    package_created = post(Databases.PACKAGES, package.to_json())
    return package_created.json()['id']

import io
import json
import os
import pathlib
import tempfile
import time
import zipfile
from dataclasses import dataclass
from zipfile import ZipFile

from flask import Response, request
from requests import HTTPError
from werkzeug.datastructures import FileStorage

from server import APP

from .entities import Databases, Folder, Package
from .package_details import create_file_document_pair, file_size_of
from .services.authentication import userdata
from .services.database import delete, find, get, post, update
from .shared import (
    create_document_with_attachement,
    delete_document,
    delete_folder,
    determine_package_expiration_timestamp_ms,
)
from .util import (
    can_delete_packages,
    can_edit_name,
    can_read,
    is_owner,
    json_body,
    web_error,
    web_error_database_connection,
    web_response,
)


@dataclass
class Directory:
    name: str
    folders: list["Directory"]
    files: list[zipfile.Path]


@APP.route("/package/all", methods=["GET"])
def get_packages():

    query = {
        "selector": {
            "owner": userdata().username,
            "status": {"$in": ["active", "rework"]},
            "organisation": userdata().organisation_id
        },
        "limit": 1000
    }

    try:
        packages = find(Databases.PACKAGES, json.dumps(query)).json().get('docs')
    except HTTPError as error:
        return web_error_database_connection(error)
    return web_response(200, details = [Package.convert(x) for x in packages])


@APP.route("/package/<id>/limits", methods=["GET"])
def get_package_limits(id: str):
    package_limits = {
        "current_size": 0,
        "file": APP.config.get("MAX_CONTENT_LENGTH"),
        "package": APP.config.get("MAX_PACKAGE_SIZE"),
    }

    package_data = get(Databases.PACKAGES, id).json()
    if not can_read(package_data, request):
        return web_response(403, details = package_limits)

    try:
        package_limits["current_size"] = file_size_of(Package.from_db(package_data))
    except Exception:
        pass

    return web_response(200, details = package_limits)


@APP.route("/package", methods=["PUT"])
@json_body
def create_package(name: str) -> Response:
    user = userdata()
    username = user.username
    displayname = user.displayname
    organisation_name = user.organisation_id
    now = round(time.time()*1000)
    keep_until = determine_package_expiration_timestamp_ms("active")
    package = Package(name=name, status='active', documents=[], folders=[], owner=username, organisation=organisation_name, created=now, last_changed=now, keep_until=keep_until, owner_displayname=displayname)
    try:
        package_created = post(Databases.PACKAGES, package.to_json())
    except HTTPError as error:
        return web_error_database_connection(error)
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
        except HTTPError:
            failed_folders.append(folder)
    if len(failed_folders) > 0:
        # TODO: Rollback for deletion 
        return web_error(500, f'{len(failed_folders)} could not be deleted', component= "DATABASE")
    
    # Delete documents, rollback for all if failed
    for document in package.get('documents'):
        try:
            if not delete_document(document):
                failed_documents.append(document)
        except HTTPError:
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
            return web_error_database_connection(error)
        
    # Delete the folder itself
    try:
        package_deleted = delete(Databases.PACKAGES, package_id).json()
    except HTTPError as error:
        # TODO: Rollback for deletion 
        return web_error_database_connection(error)


    return web_response(200, 'Success', package_deleted)

@APP.route("/package/<package_id>/rename", methods=["PATCH"])
@json_body
def rename_package(package_id: str, name: str) -> Response:
    package = get(Databases.PACKAGES, package_id).json()
    if not can_edit_name(package, request):
        return web_error(401, "You don't have permission to change the name of this package", component= "SERVER")
    changes = {
        "name": name,
    }

    if is_owner(package, userdata().username):
        changes["owner_displayname"] = userdata().displayname

    try:
        update(Databases.PACKAGES, package_id, changes)
    except HTTPError as error:
        return web_error_database_connection(error)
    return web_response(200, 'Success')


def validate_zip_file(zip: ZipFile) -> str|None:
    '''
    validates zip files for extraction
    returns
    * first validation error as `str`
    * `None` on success
    '''
    MAX_PATH_LENGTH = 200
    MAX_FILE_COUNT = 1000
    MAX_ENTRY_SIZE = APP.config.get("MAX_CONTENT_LENGTH", 0)
    MAX_EXTRACTED_SIZE =  APP.config.get("MAX_PACKAGE_SIZE", 0)

    file_list = zip.namelist()
    if len(file_list) > MAX_FILE_COUNT:
        return f"Too many files in ZIP. ({len(file_list)} > {MAX_FILE_COUNT})"
    
    for name in file_list:
        if os.path.isabs(name):
            return f"Archive contains absolute path: {name}"
        
        if '..' in name or name.startswith('/'):
            return f"Archive contains path traversal: {name}"
                
        entry_info = zip.getinfo(name)
        if entry_info.file_size > MAX_ENTRY_SIZE:
            return f"Entry '{name}' too large ({entry_info.file_size} > {MAX_ENTRY_SIZE})"
                
        if len(name) > MAX_PATH_LENGTH:
            return f"Entry path too long: {name}"
            
    total_uncompressed = sum(zip.getinfo(name).file_size for name in file_list)
    if total_uncompressed > MAX_EXTRACTED_SIZE:
        return f"Total uncompressed size too large ({total_uncompressed} > {MAX_EXTRACTED_SIZE})"

    return None


@APP.route("/package/zip", methods=["PUT"])
def create_package_from_zip() -> Response:
    vals = request.form.to_dict()
    with tempfile.TemporaryDirectory() as dir:
        zip_temp_path = dir+'upload.zip'
        project_zip: FileStorage = next(request.files.values()) # type: ignore
        project_zip.save(zip_temp_path)
        with ZipFile(zip_temp_path, 'r') as zip_ref:
            if error := validate_zip_file(zip_ref) is not None:
                web_response(400, 'Validation failed!', details={"error": error})

            zip_path = zipfile.Path(zip_ref)
            # Recursively build directory structure tree
            directory = build_directory_tree(zip_path, vals['keep_empty']=='true', vals['keep_structure']=='true')
            # Build new package for zip content
            username = userdata().username
            package_id = create_package_in_db(pathlib.Path(str(project_zip.filename)).stem, username, userdata().organisation_id, owner_displayname=userdata().displayname)
            # Create folders and documents
            folder_ids = [create_folder_from_zip(folder_entry, zip_ref, username, package_id) for folder_entry in directory.folders]
            doc_ids = [create_document_from_zip(file_entry, username) for file_entry in directory.files]
            # Update package with new folder and document ids
            update(Databases.PACKAGES, package_id, {'folders': folder_ids, 'documents': doc_ids})

    return web_response(200, 'Success', details={"id": package_id})

def build_directory_tree(path: zipfile.Path, keep_empty: bool, keep_structure: bool) -> Directory:
    def recurse_directory(path: zipfile.Path, keep_empty: bool) -> Directory:
        directory = Directory(path.name, [], [])
        for obj in path.iterdir():
            if obj.is_dir():
                new_directory = recurse_directory(obj, keep_empty)
                directory.folders.append(new_directory)
            elif keep_empty or obj.read_bytes():
                directory.files.append(obj)
        return directory
    if not keep_structure:
        path_list = [path]
        while len(path_list) == 1 and path_list[0].is_dir():
            path = path_list[0]
            path_list = list(path.iterdir())
    return recurse_directory(path, keep_empty)

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

def create_package_in_db(name:str, owner: str, organisation: str, owner_displayname: str) -> str:
    now = round(time.time()*1000)
    status='active'
    keep_until = determine_package_expiration_timestamp_ms(status)
    package = Package(name=name, status=status, documents=[], folders=[], owner=owner, organisation=organisation, created=now, last_changed=now, keep_until=keep_until, owner_displayname=owner_displayname)
    package_created = post(Databases.PACKAGES, package.to_json())
    return package_created.json()['id']

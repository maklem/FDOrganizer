from typing import Any
from datetime import datetime
import shutil
from pathlib import Path
from flask import request
from xmlschema import XMLSchema11
import hashlib
import jinja2
import os

from .services.authentication import organisation

from .entities.organisation import Organisation

from .entities.errors import ExportUserError, PathError, XMLValidationError
from .util import web_error, web_response
from .entities import Folder, Document, Package, Databases, Metadata
from .services.database import get, get_attachment
from .export_utils import create_structmap, create_package_data, build_sip_metadata, add_label, add_note
from . import APP

TEMP_DIR = os.path.join('server','tmp')

@APP.route("/export/<package_id>", methods=["POST"])
def build_export_package(package_id: str):
    package = Package.from_db(get(Databases.PACKAGES, package_id).json())

    # Refuse packages that are already archived
    if package.status == 'archived':
        return web_error(400, message="Package is already archived")

    try:    
        # Get all documents and folders in hierarchical structure
        structmap = create_structmap(package)
        
        # Download files
        create_ie_directory(structmap, package.name)

        # Create data for mets generation (depends on downloaded files)
        file_list = create_file_list(structmap, package.name)

        try:
            package_data = create_package_data(package)
        except ValueError as error:
            return web_error(400, message=error.args[0])
        # ie_structure = create_ie_structure(structmap)
        ie_structure = structmap

        # Create METS-File for ingest
        try:
            mets = build_sip_metadata(package_data, file_list, ie_structure)
        except XMLValidationError as error:
            return web_error(500, message=error.args[0], stacktrace=error.args[1])

        should_place_files = get_organisation_subdirectory(organisation(request)) is not None
        if should_place_files:
            # Copy files and METS to correct dir for Rosetta Ingest
            try:
                create_sip(package, mets, organisation(request))
            except PathError as error:
                return web_error(500, message=error.args[0])
            except ExportUserError as error:
                return web_error(500, message=error.args[0])
    finally:
        delete_temp_package(package.name)

    return web_response(200, details = {'success': True})

def create_sip(package: Package, mets, organisation_id: str):
    sipname = f'{package.id}-{round(datetime.now().timestamp())}'
    source = Path(TEMP_DIR, package.name)
    if not os.path.exists(source):
        raise PathError(f'Configured source path {source} does not exist')
    
    if (export_sub_dir := get_organisation_subdirectory(organisation_id)) is None:
        raise PathError('Configured export_subdirectory is None')

    export_dir = Path.joinpath(Path(str(os.getenv("EXPORT_DIR"))), export_sub_dir)
    export_user = os.getenv("EXPORT_USER")
    if export_dir is None or export_user is None:
        raise ExportUserError('No export user for SIP transfer configured. Check server environment variables')
    target = Path(export_dir, sipname, 'content')
    linuxuser = int(export_user)
    shutil.chown(source, linuxuser)
    shutil.copytree(source, os.path.join(target, 'streams', package.name))
    Path(os.path.join(target, 'mets.xml')).write_text(mets, encoding='utf-8')

def get_organisation_subdirectory(organisation_id: str) -> str | None:
    org_response = get(Databases.ORGANISATIONS, organisation_id).json()
    org= Organisation.from_db(org_response)
    return org.export_subdirectory

def delete_temp_package(package_name: str):
    shutil.rmtree(os.path.join(TEMP_DIR, package_name))

def create_ie_directory(structmap, structpath = ""):
    for document in structmap.get('files'):
        download_file(document, structpath)
    for folder in structmap.get('folders'):
        create_ie_directory(folder, structpath=os.path.join(structpath, folder['name']))

def download_file(document: Document, structpath:str):
    try:
        file_data = get_attachment(document.id, document.name).content # type: ignore
    except Exception:
        print(f'No attachment found for document {document.name} with ID {document.id}')
    doc_file = Path(os.path.join(TEMP_DIR, structpath, document.name))
    doc_file.parent.mkdir(exist_ok=True, parents=True)
    doc_file.write_bytes(file_data)

def create_file_list(structmap, structpath = ""):
    doc_data = [document_data(document, structpath) for document in structmap.get('files')]

    nested_data = [create_file_list(folder, os.path.join(structpath, folder.get('name'))) for folder in structmap.get('folders')]
    flat_nested_data = [file_info for sublist in nested_data for file_info in sublist]

    return [*doc_data, *flat_nested_data]

def document_data(document: Document, structpath: str) -> dict[str,Any]:
    label = ""
    note = ""
    metadata: Metadata | None = None
    if document.metadata is not None:
        metadata = Metadata.from_dict(get(Databases.METADATA, document.metadata).json())
        label = add_label(metadata)
        note = add_note(metadata)
    else:
        print(f'No metadata found for document {document.name} with ID {document.id}')

    doc_file = Path(os.path.join(TEMP_DIR, structpath, document.name))
    checksum = hashlib.md5(doc_file.read_bytes())
    
    return {
        'id': document.id,
        'fileOriginalName': document.name,
        'fileOriginalPath': os.path.join(structpath, document.name),
        'MD5': checksum.hexdigest(),
        'fileSizeBytes': str(document.size),
        'fileCreationDate': datetime.now().strftime('%Y-%m-%d'),
        # TODO
        # 'fileCreationDate': metadata.metadata.get('date'),
        'fileModificationDate': datetime.now().strftime('%Y-%m-%d'),
        # TODO
        # 'fileModificationDate': document.last_modified,
        'label': label,
        'note':  note,
        'metadata': metadata if metadata is not None else None
    }

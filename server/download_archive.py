from datetime import datetime
import logging
import os
from typing import Generator, Any

from flask import request
import hashlib
from zipstream import ZipStream

from .services.authentication import organisation
from .entities.errors import XMLValidationError
from .util import can_read, web_error
from .entities import Document, Package, Databases, Metadata
from .services.database import get, get_attachment
from .export_utils import create_structmap, create_package_data, build_sip_metadata, add_label, add_note
from . import APP

TEMP_DIR = os.path.join('server','tmp')

Hashmap = dict[str,str]

@APP.route("/download/<package_id>", methods=["GET"])
def stream_exportable_package(package_id: str):
    raw_package = get(Databases.PACKAGES, package_id).json()
    package = Package.from_db(raw_package)
    organisation_id = organisation(request)

    if not can_read(raw_package, request):
        return web_error(403, message="Rejected. You do not have permission to read this package.")

    # Refuse packages that are already archived
#    if package.status == 'archived':
#        return web_error(400, message="Package is already archived")
    try:
        package_data = create_package_data(package)
    except ValueError as error:
        logging.error(error.args[0])
        return web_error(500, error.args[0])

    structmap = create_structmap(package)

    def count_files(structmap) -> int:
        here = len(structmap['files'])
        there = sum(count_files(folder) for folder in structmap['folders'])
        return here + there

    if 0 == count_files(structmap):
        error = "Can not generate download for package with no files."
        logging.error(error)
        return web_error(500, error)

    def generate() -> Generator[bytes,None,None]:
        # Get all documents and folders in hierarchical structure
        hashmap: Hashmap = {}
        zs = ZipStream()
        # Download files
        yield from stream_zipped_directory(zs, hashmap, structmap, package.name)

        # Create data for mets generation (depends on downloaded files)
        file_list = create_streamed_file_list(structmap, hashmap, package.name)

        # ie_structure = create_ie_structure(structmap)
        ie_structure = structmap

        # Create METS-File for ingest
        try:
            mets = build_sip_metadata(package_data, file_list, ie_structure)
            yield from stream_mets(zs, package, mets, organisation_id)
        except XMLValidationError as error:
            logging.error(error.args[0])
        
        yield from zs.finalize()

    # return web_response(200, details = {'success': True})
    return generate(), {"Content-Type": "application/zip"}


def stream_mets(zs: ZipStream, package: Package, mets, organisation_id: str) -> Generator[bytes,None,None]:
    zs.add(mets, 'mets.xml')
    yield from zs.all_files()

def stream_zipped_directory(zs: ZipStream, hashmap: Hashmap, structmap, structpath = "") -> Generator[bytes,None,None]:
    for document in structmap.get('files'):
        yield from stream_zipped_file(zs, hashmap, document, structpath)
    for folder in structmap.get('folders'):
        yield from stream_zipped_directory(zs, hashmap, folder, structpath=os.path.join(structpath, folder['name']))

def stream_zipped_file(zs: ZipStream, hashmap: Hashmap, document: Document, structpath:str) -> Generator[bytes,None,None]:
    if not document.id:
        return

    file_name = os.path.join(structpath, document.name)
    try:
        file_data = get_attachment(document.id, document.name).content # type: ignore
    except Exception:
        print(f'No attachment found for document {document.name} with ID {document.id}')
    hashmap[document.id] = hashlib.md5(file_data).hexdigest()
    zs.add(file_data, file_name)
    yield from zs.all_files()

def create_streamed_file_list(structmap, hashmap, structpath = ""):
    doc_data = [streamed_document_data(document, hashmap, structpath) for document in structmap.get('files')]

    nested_data = [create_streamed_file_list(folder, hashmap, os.path.join(structpath, folder.get('name'))) for folder in structmap.get('folders')]
    flat_nested_data = [file_info for sublist in nested_data for file_info in sublist]

    return [*doc_data, *flat_nested_data]

def streamed_document_data(document: Document, hashmap: Hashmap, structpath: str) -> dict[str,Any]:
    label = ""
    note = ""
    metadata: Metadata | None = None
    if document.metadata is not None:
        metadata = Metadata.from_dict(get(Databases.METADATA, document.metadata).json())
        label = add_label(metadata)
        note = add_note(metadata)
    else:
        print(f'No metadata found for document {document.name} with ID {document.id}')
    
    return {
        'id': document.id,
        'fileOriginalName': document.name,
        'fileOriginalPath': os.path.join(structpath, document.name),
        'fileSizeBytes': str(document.size),
        'fileCreationDate': datetime.now().strftime('%Y-%m-%d'),
        # TODO
        # 'fileCreationDate': metadata.metadata.get('date'),
        'fileModificationDate': datetime.now().strftime('%Y-%m-%d'),
        # TODO
        # 'fileModificationDate': document.last_modified,
        'MD5': hashmap[document.id] if document.id and hashmap[document.id] else "missing",
        'label': label,
        'note':  note,
        'metadata': metadata if metadata is not None else None
    }

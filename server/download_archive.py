import logging
import os
from typing import Generator

from flask import request
import hashlib
from jinja2.exceptions import UndefinedError
from zipstream import ZipStream

from .services.authentication import organisation
from .entities.errors import XMLValidationError
from .util import can_read, error_page
from .entities import Document, Package, Databases
from .services.database import get, get_attachment
from .export_utils import create_structmap, create_package_data, build_sip_metadata, check_structmap, create_file_list
from . import APP

TEMP_DIR = os.path.join('server','tmp')

Hashmap = dict[str,str]

@APP.route("/download/<package_id>", methods=["GET"])
def stream_exportable_package(package_id: str):
    raw_package = get(Databases.PACKAGES, package_id).json()
    package = Package.from_db(raw_package)
    organisation_id = organisation(request)

    if not can_read(raw_package, request):
        return error_page(403,["Rejected. You do not have permission to read this package."])

    try:
        package_data = create_package_data(package)
    except ValueError as error:
        logging.error(error.args[0])
        return error_page(500, [error.args[0]])

    structmap = create_structmap(package)

    errors = check_structmap("", structmap)
    if errors:
        logging.error("Failed to generate download. Errors:")
        for e in errors:
            logging.error(f" - {e}")
        return error_page(500, errors)


    def generate() -> Generator[bytes,None,None]:
        # Get all documents and folders in hierarchical structure
        hashmap: Hashmap = {}
        zs = ZipStream()
        errors: list[str] = []
        # Download files
        yield from stream_zipped_directory(zs, hashmap, structmap, package.name)

        # Create data for mets generation (depends on downloaded files)
        file_list = create_file_list(structmap, package.name)

        # Create METS-File for ingest
        try:
            mets = build_sip_metadata(package_data, file_list, structmap)
            yield from stream_mets(zs, package, mets, organisation_id)
        except UndefinedError as error:
            errors.append(error.args[0])
            logging.error(error.args[0])
        except XMLValidationError as error:
            errors.append(error.args[0])
            logging.error(error.args[0])

        if errors:
            zs.add("\n\n".join(errors), "generator-errors.log")
            yield from zs.all_files()
            
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
        file_data = get_attachment(document.id, document.name).content
    except Exception:
        print(f'No attachment found for document {document.name} with ID {document.id}')
    hashmap[document.id] = hashlib.md5(file_data).hexdigest()
    zs.add(file_data, file_name)
    yield from zs.all_files()

import json
from requests import HTTPError
from flask import request

from . import APP

from .entities.databases import Databases
from .entities.document import Document
from .entities.metadata import Metadata

from .services.authentication import user
from .services.database import get, post, update

from .util import web_error, web_response


@APP.route("/document/<document_id>/metadata", methods=["GET"])
def get_document_metadata(document_id):
    # Get document from DB
    try:
        document = get(Databases.DOCUMENTS, document_id).json()
    except HTTPError as error:
        return web_error(error.response.status_code, error.response.reason, component= "DATABASE")      
    # Check ownership
    username = user(request)
    if document.get('owner') != username:
        return web_error(401, "You don't have permission to view this content", component= "SERVER")
    # Init return value with document info
    result = {'document': Document.convert(document)}
    # Check if document already has metadata
    metadata_id = document.get('metadata')
    print(document.get('metadata'))
    if metadata_id is None:
        return web_response(206, details = result)
    # Get metadata from DB
    try:
        metadata = get(Databases.METADATA, metadata_id).json()
        print(metadata)
    except HTTPError as error:
        return web_error(error.response.status_code, error.response.reason, component= "DATABASE")    
    # Return metadata
    result = result | {"metadata": Metadata.convert(metadata)}
    return web_response(200, details = result)

@APP.route("/document/<document_id>/metadata", methods=["PUT"])
def update_document_metadata(document_id):
    # Get document from DB
    try:
        document = get(Databases.DOCUMENTS, document_id).json()
    except HTTPError as error:
        return web_error(error.response.status_code, error.response.reason, component= "DATABASE")      
    # Check ownership
    username = user(request)
    if document.get('owner') != username:
        return web_error(401, "You don't have permission to change this content", component= "SERVER")
    # Get metadata from request body
    new_metadata = request.json
    # Check if document already has metadata
    metadata_id = document.get('metadata')
    print(document.get('metadata'), new_metadata)
    if metadata_id is None:
        try:
            metadata = post(Databases.METADATA, payload = json.dumps(new_metadata)).json()
            print(metadata)
        except HTTPError as error:
            return web_error(error.response.status_code, error.response.reason, component= "DATABASE")
        document_changes = {'metadata': metadata.get('id')}
        try:
            document = update(Databases.DOCUMENTS, document.get('_id'), document_changes).json()
            print(document)
        except HTTPError as error:
            return web_error(error.response.status_code, error.response.reason, component= "DATABASE")
    else:
        try:
            metadata = update(Databases.METADATA, metadata_id, new_metadata, replace=True).json()
        except HTTPError as error:
            return web_error(error.response.status_code, error.response.reason, component= "DATABASE")    
    # Return metadata
    return web_response(200, details = metadata)
import json
from requests import HTTPError
from flask import request

from . import APP

from .entities.databases import Databases
from .entities.document import Document
from .entities.folder import Folder
from .entities.package import Package
from .entities.metadata import Metadata

from .services.authentication import user
from .services.database import get, post, update

from .util import get_database_from_string, owner, web_error, web_response


@APP.route("/<entity_type>/<entity_id>/metadata", methods=["GET"])
def get_entity_with_metadata(entity_type, entity_id):
    # Get entity from DB
    try:
        entity = get(get_database_from_string(entity_type), entity_id).json()
    except HTTPError as error:
        return web_error(error.response.status_code, error.response.reason, component= "DATABASE")      
    # Check ownership
    username = user(request)
    if entity.get('owner') != username:
        return web_error(401, "You don't have permission to view this content", component= "SERVER")
    # Init return value with document info
    result = convert_entity(entity_type, entity)
    # Check if document already has metadata
    metadata_id = entity.get('metadata')
    if metadata_id is None:
        return web_response(206, details = result)
    # Get metadata from DB
    try:
        metadata = get(Databases.METADATA, metadata_id).json()
    except HTTPError as error:
        return web_error(error.response.status_code, error.response.reason, component= "DATABASE")    
    # Return metadata
    result = result | {"metadata": Metadata.convert(metadata)}
    return web_response(200, details = result)

@APP.route("/<entity_type>/<entity_id>/metadata", methods=["PUT"])
def update_entity_metadata(entity_type, entity_id):
    # Get document from DB
    try:
        entity = get(get_database_from_string(entity_type), entity_id).json()
    except HTTPError as error:
        return web_error(error.response.status_code, error.response.reason, component= "DATABASE")      
    # Check ownership
    if not owner(entity, user(request)):
        return web_error(401, "You don't have permission to change this content", component= "SERVER")
    # Get metadata from request body
    new_metadata = request.json
    # Check if document already has metadata
    metadata_id = entity.get('metadata')
    if metadata_id is None:
        try:
            metadata = post(Databases.METADATA, payload = json.dumps(new_metadata)).json()
        except HTTPError as error:
            return web_error(error.response.status_code, error.response.reason, component= "DATABASE")
        changes = {'metadata': metadata.get('id')}
        try:
            entity = update(get_database_from_string(entity_type), entity.get('_id'), changes).json()
        except HTTPError as error:
            return web_error(error.response.status_code, error.response.reason, component= "DATABASE")
    else:
        try:
            metadata = update(Databases.METADATA, metadata_id, new_metadata, replace=True).json()
        except HTTPError as error:
            return web_error(error.response.status_code, error.response.reason, component= "DATABASE")    
    # Return metadata
    return web_response(200, details = metadata)

def convert_entity(entity_type, entity) -> dict[str, dict[str, any]]:
    if entity_type == 'document':
        return {'document': Document.convert(entity)}
    if entity_type == 'package':
        return {'package': Package.convert(entity)}
    if entity_type == 'folder':
        return {'folder': Folder.convert(entity)}
    raise ValueError(f'Entity type {entity_type} is unknown')

import json
from typing import Any
from requests import HTTPError
from flask import request

from . import APP

from .entities import Databases, Document, Folder, Package, Metadata

from .services.database import get, post, update

from .util import can_read_metadata, can_update_metadata, get_database_from_string, web_error, web_error_database_connection, web_response


@APP.route("/<entity_type>/<entity_id>/metadata", methods=["GET"])
def get_entity_with_metadata(entity_type, entity_id):
    # Get entity from DB
    try:
        entity = get(get_database_from_string(entity_type), entity_id).json()
    except HTTPError as error:
        return web_error_database_connection(error)
    # Check permissions
    if not can_read_metadata(entity, request):
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
        return web_error_database_connection(error)
    # Return metadata
    result = result | {"metadata": Metadata.convert(metadata)}
    return web_response(200, details = result)

@APP.route("/<entity_type>/<entity_id>/metadata", methods=["PUT"])
def update_entity_metadata(entity_type, entity_id):
    # Get document from DB
    try:
        entity = get(get_database_from_string(entity_type), entity_id).json()
    except HTTPError as error:
        return web_error_database_connection(error)
    # Check ownership
    if not can_update_metadata(entity, request):
        return web_error(401, "You don't have permission to change this content", component= "SERVER")
    # Get metadata from request body
    new_metadata = request.json
    if new_metadata is None:
        return web_error(400, "Request is missing updated metadata", component= "SERVER")
    # Update document in DB
    # Check if document already has metadata
    metadata_id = entity.get('metadata')
    if metadata_id is None:
        try:
            metadata = post(Databases.METADATA, payload = json.dumps(new_metadata)).json()
        except HTTPError as error:
            return web_error_database_connection(error)
        changes = {'metadata': metadata.get('id')}
        try:
            entity = update(get_database_from_string(entity_type), entity.get('_id'), changes).json()
        except HTTPError as error:
            return web_error_database_connection(error)
    else:
        try:
            metadata = update(Databases.METADATA, metadata_id, new_metadata, replace=True).json()
        except HTTPError as error:
            return web_error_database_connection(error)
    # Return metadata
    return web_response(200, details = metadata)

def convert_entity(entity_type: str, entity: dict[str, Any]) -> dict[str, dict[str, Any]]:
    if entity_type == 'document':
        return {'document': Document.convert(entity)}
    if entity_type == 'package':
        return {'package': Package.convert(entity)}
    if entity_type == 'folder':
        return {'folder': Folder.convert(entity)}
    raise ValueError(f'Entity type {entity_type} is unknown')

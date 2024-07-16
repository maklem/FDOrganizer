import importlib
import json
from functools import wraps
from pathlib import Path
from typing import List, Literal, Union
from flask import request, Response
from importlib_resources import files

from server import APP
from .shared import persist_documents
from .services.database import get
from .entities import Document, Folder
from .util import can_add_files, get_database_from_string, web_error, web_response
from .services.authentication import add_payload, payload, user

SERVERNAME = __name__.split('.')[0]

def needs_authentication(api_method):
    @wraps(api_method)

    def check_plugin_auth(*args, **kwargs):
        # Identify plugin and auth token from request params
        auth_token = payload(request.cookies['token'])
        source = str(kwargs.get('source'))
        # Get correct plugin subtoken from auth token
        if kwargs.get('source') is None:
            return web_error(400, f'Path parameter <source> is needed for this route', component="SERVER")
        plugin_token = auth_token.get(source)
        if plugin_token is None:
            return web_error(401, f'{source} not authorized', component=source)
        # Proceed with API request method
        return api_method(*args, **kwargs)

    return check_plugin_auth

@APP.route('/import/<source>', methods=['GET'])
@needs_authentication
def get_toplevel(source: str):
    plugin = get_plugin(source)
    auth = get_plugin_auth(source)
    result = plugin.get_toplevel(request, auth)
    if isinstance(result, Response):
        return result
    return web_response(200, details = serialize(result))

@APP.route('/import/<source>', methods=['POST'])
@needs_authentication
def import_documents_from(source: str):
    # Get data from request body
    if request.json is None:
        return web_error(400, f'Request does not contain data', component="SERVER")
    source_ids = request.json.get('sourceIds')
    parent = request.json.get('parent')
    parent_type = request.json.get('parentType')
    if source_ids is None or parent is None or parent_type is None:
        return web_error(400, f'Request does not contain correct data in body', component="SERVER")
    
    # Get selected files and their metadata from the plugin source
    plugin = get_plugin(source)
    auth = get_plugin_auth(source)
    result = plugin.get_files_with_metadata(source_ids, request, auth)
    if isinstance(result, Response):
        return result
    
    # Import the files and metadata into the selected FDO package
    persisted_documents =  import_files(result, parent, parent_type)
    if isinstance(persisted_documents, Response):
        return persisted_documents
    for document in persisted_documents['success']:
        #TODO Add metadata to DB
        pass
    return web_response(200, details=persisted_documents)

@APP.route('/import/<source>/<collection>', methods=['GET'])
@needs_authentication
def get_collection(source: str, collection: str):
    if collection is None:
        return web_error(400, 'No valid Collection ID provided', component="SERVER")
    plugin = get_plugin(source)
    auth = get_plugin_auth(source)
    result = plugin.get_collection(collection, request, auth)
    if isinstance(result, Response):
        return result
    return web_response(200, details = serialize(result))

@APP.route('/import/<source>/login', methods=['POST'])
def login_source(source: str):
    auth_token = request.cookies['token']
    plugin = importlib.import_module(f'.plugins.{source}.import', 'server')

    # Get plugin authentication
    response = plugin.login(request)
    if response.status_code > 399:
        return response
    plugin_token = json.loads(response.get_data())

    # Add plugin auth to existing JWT
    new_token = add_payload(auth_token, source, plugin_token)
    return web_response(200, details={"token": new_token})


@APP.route('/import/sources')
def list_import_sources():
    info = [plugin_info(x) for x in get_plugins()]
    return web_response(200, details = info)


def plugin_info(plugin_path: Path):
    # try:
    config = get_config(plugin_path)
    # except Exception:
        # return {
        #     "id": plugin,
        #     "error": f'{plugin}: Config file not found'
        # }
    plugin_id = str(plugin_path).split('/')[-1]
    return {
        "id": plugin_id,
        "name": config.get("displayName"),
        "needsAuthentication": config.get("needsAuthentication"),
        "authenticationType": config.get('authenticationType')
    }

def get_config(plugin_path: Path) -> dict:
    config_filepath = plugin_path.joinpath('config.json')
    with open(config_filepath, encoding="utf-8") as file:
        return json.load(file)

def get_plugins() -> list[Path]:
    plugins = files(f'{SERVERNAME}.plugins').iterdir()
    paths = [Path(f'{SERVERNAME}', 'plugins', str(plugin)) for plugin in plugins]
    return [path for path in paths if path.is_dir()]


def get_plugin_auth(source: str):
    auth_token = payload(request.cookies['token'])
    return auth_token.get(source)

def get_plugin(source: str):
    return importlib.import_module(f'.plugins.{source}.import', 'server')

def serialize(content: dict[Literal["folders","documents"], List[Union[Folder, Document]]]) -> dict[str, List]:
    folders = [Folder.to_dict(x) for x in content['folders']] # type: ignore
    documents = [Document.to_dict(x) for x in content['documents']] # type: ignore
    return {'folders':folders, 'documents': documents}

def import_files(import_documents: List[dict], parent: str, parent_type: str):
    # Check ownership of parent, to determine if creation of subelement is valid
    package_or_folder = get(get_database_from_string(parent_type), parent).json()
    if not can_add_files(package_or_folder, request):
        return web_error(401, "You don't have permission to edit this content", component="SERVER")

    return persist_documents(import_documents, parent, parent_type)

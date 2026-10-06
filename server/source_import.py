import importlib
import json
import os.path
from functools import wraps
from pathlib import Path
from typing import Literal

from flask import Response, request, session
from importlib_resources import files

from server import APP

from .entities import Document, Folder
from .entities.databases import Databases
from .entities.errors import PluginError
from .entities.organisation import Organisation
from .services.authentication import (
    add_plugin,
    userdata,
    remove_plugin,
)
from .services.database import get
from .shared import persist_documents
from .util import (
    can_add_files,
    get_database_from_string,
    json_body,
    web_error,
    web_response,
)

SERVERNAME = __name__.split('.')[0]

def needs_plugin_authentication(api_method):
    @wraps(api_method)

    def check_plugin_auth(*args, **kwargs):
        if "user" not in session:
            return web_error(401, 'User not logged in.')

        # Identify plugin and auth token from request params
        auth_token = session["user"].plugins
        source = str(kwargs.get('source'))

        # Get correct plugin subtoken from auth token
        if kwargs.get('source') is None:
            return web_error(400, 'Path parameter <source> is needed for this route', component="SERVER")
        plugin_token = auth_token.get(source)
        if plugin_token is None:
            return web_error(401, f'{source} not authorized', component=source)

        # Proceed with API request method
        return api_method(*args, **kwargs)

    return check_plugin_auth

@APP.route('/import/<source>', methods=['GET'])
@needs_plugin_authentication
def get_toplevel(source: str):
    plugin = get_plugin(source)
    auth = get_plugin_auth(source)
    try:
        result = plugin.get_toplevel(request, auth)
    except PluginError as e:
        return web_error(e.status_code, message=e.message, component=source)
    return web_response(200, details = serialize(result))

@APP.route('/import/<source>', methods=['POST'])
@needs_plugin_authentication
@json_body
def import_documents_from(source: str, source_ids: list[str], parent: str, parent_type: Literal['folder', 'document']):
    # Get selected files and their metadata from the plugin source
    plugin = get_plugin(source)
    auth = get_plugin_auth(source)
    try:
        result = plugin.get_files_with_metadata(source_ids, request, auth)
    except PluginError as e:
        return web_error(e.status_code, message=e.message, component=source)
    # Import the files and metadata into the selected FDO package
    persisted_documents =  import_files_and_metadata(result, parent, parent_type)
    if isinstance(persisted_documents, Response):
        return persisted_documents
    for document in persisted_documents['success']:
        #TODO Add metadata to DB
        pass
    return web_response(200, details=persisted_documents)

@APP.route('/import/<source>/<collection>', methods=['GET'])
@needs_plugin_authentication
def get_collection(source: str, collection: str):
    if collection is None:
        return web_error(400, 'No valid Collection ID provided', component="SERVER")
    plugin = get_plugin(source)
    auth = get_plugin_auth(source)
    try:
        result = plugin.get_collection(collection, request, auth)
    except PluginError as e:
        return web_error(e.status_code, message=e.message, component=source)
    return web_response(200, details = serialize(result))

@APP.route('/import/<source>/login', methods=['POST'])
def login_source(source: str):
    auth_token = request.cookies['token']
    plugin = importlib.import_module(f'.plugins.{source}.import', 'server')

    # Get plugin authentication
    try:
        response = plugin.login(request)
    except PluginError as e:
        return web_error(e.status_code, message=e.message, component=source)
    plugin_token = json.loads(response.get_data())

    add_plugin(source, plugin_token)

    return web_response(200, details={ 'status': 'OK' })

@APP.route('/import/<source>/logout', methods=['POST'])
def logout_source(source: str):
    remove_plugin(source)

    return web_response(200, details={ 'status': 'OK' })

@APP.route('/import/sources')
def list_import_sources():
    info = [plugin_info(x) for x in get_plugins()]
    info = [plugin for plugin in info if plugin["id"] in get_organisation_plugins(userdata().organisation_id)]
    return web_response(200, details = info)


def plugin_info(plugin_path: Path):
    # try:
    config = get_config(plugin_path)
    # except Exception:
        # return {
        #     "id": plugin,
        #     "error": f'{plugin}: Config file not found'
        # }
    #plugin_id = str(plugin_path).split('/')[-1]
    plugin_id = os.path.basename(plugin_path)
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
    auth_token = payload(request.cookies['token']).get('plugins', {})
    return auth_token.get(source)

def get_plugin(source: str):
    return importlib.import_module(f'.plugins.{source}.import', 'server')

def serialize(content: dict[Literal["folders","documents"], list]) -> dict[str, list]:
    folders = [Folder.to_dict(x) for x in content['folders']]
    documents = [Document.to_dict(x) for x in content['documents']]
    return {'folders':folders, 'documents': documents}

def import_files_and_metadata(import_triples: list[dict], parent: str, parent_type: str):
    # Check ownership of parent, to determine if creation of subelement is valid
    package_or_folder = get(get_database_from_string(parent_type), parent).json()
    if not can_add_files(package_or_folder, request):
        return web_error(401, "You don't have permission to edit this content", component="SERVER")
    import_triples = [add_owner(x, userdata().username) for x in import_triples]
    return persist_documents(import_triples, parent, parent_type)

def add_owner(import_triple: dict, username: str):
    import_triple['document'].owner = username
    return import_triple

def get_organisation_plugins(organisation_id: str) -> list[str]:
    org_response = get(Databases.ORGANISATIONS, organisation_id).json()
    org= Organisation.from_db(org_response)
    return org.plugins
import importlib
import json
from functools import wraps
from flask import request
from pkg_resources import resource_listdir, resource_isdir, resource_filename

from server import APP
from server.util import web_error, web_response
from server.services.authentication import add_payload, payload

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
    return plugin.get_toplevel(request, auth)

@APP.route('/import/<source>/<collection>', methods=['GET'])
@needs_authentication
def get_collection(source: str, collection: str):
    plugin = get_plugin(source)
    auth = get_plugin_auth(source)
    return plugin.get_collection(request, auth)


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
    info = list(
        map(
            plugin_info,
            get_plugins()
        )
    )
    return web_response(200, details = info)


def plugin_info(plugin: str):
    try:
        config = get_config(plugin)
    except Exception:
        return {
            "id": plugin,
            "error": f'{plugin}: Config file not found'
        }
    return {
        "id": plugin,
        "name": config.get("displayName"),
        "needsAuthentication": config.get("needsAuthentication"),
        "authenticationType": config.get('authenticationType')
    }

def get_config(plugin: str):
    config_filepath = resource_filename(__name__, f'plugins/{plugin}/config.json')
    with open(config_filepath, encoding="utf-8") as file:
        return json.load(file)

def get_plugins() -> list[str]:
    plugins = resource_listdir(__name__, "plugins")
    return list(
        filter(
            lambda plugin: resource_isdir(__name__, f'plugins/{plugin}'),
            plugins
        )
    )

def get_plugin_auth(source: str):
    auth_token = payload(request.cookies['token'])
    return auth_token.get(source)

def get_plugin(source: str):
    return importlib.import_module(f'.plugins.{source}.import', 'server')

'''
    Module for easydb integration. Implements the api call to access easydb repository
'''


from ast import List
import io
import json
import mimetypes
from typing import Literal, Union

import requests
from flask.wrappers import Request, Response
from pkg_resources import resource_filename

from .plugin_document import PluginDocument

from ...services.authentication import user
from .plugin_folder import PluginFolder
from ...entities.folder import Folder
from ...entities.document import Document
from ...util import web_error, web_response

def get_config():
    config_filepath = resource_filename(__name__, f'config.json')
    with open(config_filepath, encoding="utf-8") as file:
        return json.load(file)


def login(request: Request) -> Response:
    '''
        authenticate to easydb. first get a session token, then authenticate this session token via
        user login
    '''
    # Get session token from easydb
    url = f'{get_config()["baseUrl"]}/session'
    response = requests.get(url ,timeout=10)
    try:
        token = response.json()['token']
    except (json.JSONDecodeError, KeyError):
        return web_error(500, "Failed to receive token from easydb", component="Easy DB")

    # Authorize session via token and username&password
    auth_url = f'{url}/authenticate'
    request_data = json.loads(request.get_data())
    payload = {
        "token" : token,
        "login": request_data["username"],
        "password": request_data["password"]
    }
    response = requests.post(auth_url, payload, timeout=10)
    if response is None:
        return web_error(500, "Failed to authenticate token with easydb", component="Easy DB")
    if response.status_code > 399:
        return web_error(response.status_code, response.text, component="Easy DB")

    # Get user id for adding it to auth token
    response = requests.get(f'{url}?token={token}', timeout=10)
    user = response.json().get('user').get('user').get('_id')
    return web_response(200, "Authentication with Easy DB successful", {'token': token, 'user': user})

def get_toplevel(request: Request, auth) -> Union[Response, dict[Union[Literal['folders'], Literal['documents']], List]]:
    '''
        querys the easydb server for collections. returns the collections either as string or json array
    '''

    search_query = {
        "type" : "collection",
        "search" : [
            {
                "type" : "in",
                "bool" : "must",
                "fields" : [
                    "_owner.user._id"
                ],
                "in" : [
                    auth.get('user')
                ]

            },
            {
                "type" : "in",
                "bool" : "must",
                "fields" : [
                    "collection.is_system_collection"
                ],
                "in" : [
                    False
                ]

            },
        ]
    }

    url = f'{get_config()["baseUrl"]}/search?token={auth.get("token")}'
    response = requests.post(url, json= search_query, timeout=10)
    if response.status_code > 399:
        return web_error(response.status_code, response.text, component="Easy DB")
    result_list = response.json()
    collections = result_list.get('objects')
    folders = [convert_collection(x, user(request)) for x in collections]
    return {'folders': folders, 'documents': []}

def get_collection(collection_id: str, request: Request, auth):
    '''
        get information about the content of an collection. number of items, type of items,.
        required collection_id as arg.
    '''

    search_query = {
        "type" : "object",
        "search" : [
            {
                "type" : "in",
                "bool" : "must",
                "fields" : [
                    "_collections._id"
                ],
                "in" : [
                    int(collection_id)
                ]

            }
        ]
    }

    url = f'{get_config()["baseUrl"]}/search?token={auth.get("token")}'

    response = requests.post(url, json=search_query, timeout=10)
    if response.status_code > 399:
        return web_error(response.status_code, response.text, component="Easy DB")

    # Convert files for Frontend
    result_list = response.json()
    files = result_list.get('objects')
    files = [convert_file(x, user(request)) for x in files if x.get('object').get('file')]
    return {'documents': files, 'folders': []}

def get_files_with_metadata(file_ids, request, auth):
    search_query = {
        "type" : "object",
        "search" : [
            {
                "type" : "in",
                "bool" : "must",
                "fields" : [
                    "_system_object_id"
                ],
                "in" : file_ids
            }
        ]
    }
    url = f'{get_config()["baseUrl"]}/search?token={auth.get("token")}'

    response = requests.post(url, json=search_query, timeout=10)
    if response.status_code > 399:
        return web_error(response.status_code, response.text, component="Easy DB")

    # Convert files for Frontend
    result_list = response.json()
    objects = result_list.get('objects')
    files = [extract_file(x) for x in objects]
    documents = [convert_file(x, user(request), is_stored=True) for x in objects]
    metadata = [extract_metadata(x) for x in objects]
    
    results = []
    for index in range(len(files)):
        results.append({'document': documents[index], 'file': files[index], 'metadata': metadata[index]})
    return results

def convert_collection(collection: dict, username: str) -> Folder:
    outer_collection = PluginFolder.from_dict(collection) # type: ignore
    inner_collection = outer_collection.collection
    displayname = inner_collection.displayname.get('de-DE')
    collection_id = inner_collection._id
    return Folder(name = displayname, id = collection_id, owner = username, documents=[], folders=[])


def convert_file(easydb_object: dict, username: str, is_stored: bool = False) -> Document:
    obj: PluginDocument = PluginDocument.from_dict(easydb_object) # type: ignore
    inner_object = obj.object
    file_id = obj._system_object_id

    file = inner_object.file[0]

    displayname = file.original_filename
    mimetype = mimetypes.guess_type(file.original_filename)[0] or 'application/octet-stream'
    size = file.filesize

    return Document(name = displayname, size = size, type = mimetype, is_stored = is_stored, owner = username, source_id= file_id, source="easy DB")

def extract_file(easydb_object: dict):
    obj: PluginDocument = PluginDocument.from_dict(easydb_object) # type: ignore
    download_url = obj.object.file[0].versions['original']['download_url']
    if not obj.object.file[0].versions['original']['_download_allowed']:
        return None
    file_content = requests.get(download_url).content
    if file_content is None:
        return None
    file = io.BytesIO(file_content)
    return file

def extract_metadata(easydb_object: dict):
    #TODO: Funktion schreiben als Beispiel zur Extraktion von metadaten und Überführung ins neue Schema
    return None
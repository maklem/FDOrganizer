import urllib.parse
from base64 import b64encode

import requests

from server.entities.databases import Databases
from server.entities.document import CouchDocument
from server.lzv_util import get_config


def auth_header() -> dict[str, str]:
    username = get_config()["couchDBAdmin"]
    password = get_config()["couchDBPassword"]
    return {"Authorization": f'Basic {encode_credentials(username, password)}'}


def base_url():
    return get_config()["couchDBBaseURL"]


def query_params(parameters: dict[str, str]) -> str:
    params = ''
    for key, value in parameters.items():
        params = f'{params}{key}={value}&'
    return params


def db_url(database: Databases, parameters: dict[str, str] | None = None) -> str:
    if not parameters:
        return f'{base_url()}/{database.value}'
    return f'{db_url(database)}?{query_params(parameters)}'


def doc_url(database: Databases, document: str, parameters: dict[str, str] | None = None) -> str:
    if not parameters:
        return f'{base_url()}/{database.value}/{document}'
    return f'{doc_url(database, document)}?{query_params(parameters)}'


def encode_credentials(username, password) -> str:
    string = (f'{username}:{password}').encode('utf-8')
    return str(b64encode(string), 'utf-8')


def attach(database: Databases, document: CouchDocument, file, parameters: dict[str, str] | None = None):
    headers = auth_header() | {
        'Content-Type': file.mimetype,
        'If-Match': document.rev
    }
    return requests.put(f'{doc_url(database, document.id, parameters)}/{urllib.parse.quote(file.filename)}', headers=headers, data=file, timeout=20)


def post(database: Databases, payload: str, parameters: dict[str, str] | None = None) -> requests.Response:
    headers = auth_header() | {
        "Content-Type": "application/json",
        "Accept": "application/json"
    }
    return requests.post(db_url(database, parameters), headers=headers, data=payload, timeout=20)


def get(database: Databases, query: str, parameters: dict[str, str] | None = None) -> requests.Response:
    headers = auth_header() | {
        "Accept": "application/json",
        "Content-Type": "application/json"
    }
    return requests.post(db_url(database, parameters), headers=headers, data=query, timeout=20)

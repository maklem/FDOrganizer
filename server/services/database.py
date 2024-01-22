import json
import os
from typing import Any, Literal, Optional
import urllib.parse
from base64 import b64encode

import requests

from ..entities.databases import Databases
from ..entities.couch_document import CouchDocument


def auth_header() -> dict[str, str]:
    username = os.getenv('COUCHDB_USER')
    password = os.getenv('COUCHDB_PASSWORD')
    return {"Authorization": f'Basic {encode_credentials(username, password)}'}


def base_url():
    return f'http://{os.getenv("COUCHDB_HOST")}:{os.getenv("COUCHDB_PORT")}'


def query_params(parameters: dict[str, str]) -> str:
    params = ''
    for key, value in parameters.items():
        params = f'{params}{key}={value}&'
    return params


def db_url(database: Databases, parameters: Optional[dict[str, str]] = None) -> str:
    if not parameters:
        return f'{base_url()}/{database.value}'
    return f'{db_url(database)}?{query_params(parameters)}'


def doc_url(database: Databases, document: str, parameters: Optional[dict[str, str]] = None) -> str:
    if not parameters:
        return f'{base_url()}/{database.value}/{document}'
    return f'{doc_url(database, document)}?{query_params(parameters)}'


def encode_credentials(username, password) -> str:
    string = (f'{username}:{password}').encode('utf-8')
    return str(b64encode(string), 'utf-8')





def attach(database: Databases, document: CouchDocument, file_content, filename, mimetype: Optional[str] = None, parameters: Optional[dict[str, str]] = None):
    headers = auth_header() | {'If-Match': document.rev}
    if mimetype is not None:
        headers = headers | {'Content-Type': mimetype}

    return requests.put(f'{doc_url(database, document.id, parameters)}/{urllib.parse.quote(filename)}', headers=headers, data=file_content, timeout=20)

def get_attachment(document_id: str, document_name: str):
    headers = auth_header()
    return requests.get(f'{doc_url(Databases.DOCUMENTS, document=document_id)}/{document_name}', headers=headers)

def post(database: Databases, payload: str, parameters: Optional[dict[str, str]] = None) -> requests.Response:
    headers = auth_header() | {
        "Content-Type": "application/json",
        "Accept": "application/json"
    }
    return requests.post(db_url(database, parameters), headers=headers, data=payload, timeout=20)


def find(database: Databases, query: str, parameters: Optional[dict[str, str]] = None) -> requests.Response:
    url = f'{db_url(database)}/_find'
    
    headers = auth_header() | {
        "Accept": "application/json",
        "Content-Type": "application/json"
    }
    return requests.post(url, headers=headers, data=query, timeout=20)


def getall(database: Databases) -> requests.Response:
    url = f'{db_url(database)}/_all_docs?include_docs=true'
    
    headers = auth_header() | {
        "Accept": "application/json",
        "Content-Type": "application/json"
    }
    results = requests.get(url, headers=headers, timeout=20).json().get('rows')
    return [result.get('doc') for result in results]


def get(database: Databases, id: str) -> requests.Response:
    url = f'{db_url(database)}/{id}'
    
    headers = auth_header() | {
        "Accept": "application/json",
        "Content-Type": "application/json"
    }
    return requests.get(url, headers=headers, timeout=20)


def update(database: Databases, doc_id, changes: dict[str, Any], replace: bool = False) -> requests.Response:
    current_document = get(database, doc_id).json()

    new_document = changes if replace else patch(current_document, changes)
    headers = auth_header() | {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "If-Match": current_document.get('_rev')
    }

    return requests.put(doc_url(database, doc_id), headers=headers, data=json.dumps(new_document), timeout=20)


def delete(database: Databases, doc_id: str) -> requests.Response:
    revision = requests.head(doc_url(database, doc_id), headers=auth_header(), timeout=10).headers.get('etag')
    headers = auth_header() | {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "If-Match": revision
    }

    return requests.delete(doc_url(database, doc_id), headers=headers, timeout=20)


def patch(obj: dict[str, Any], changes: dict[str, Any]):
    for key, value in changes.items():
        if key not in obj:
            obj[key] = value
        elif not isinstance(obj.get(key), list):
            obj[key] = value
        else:
            obj[key] = patch_array(obj[key], value)
    return obj

def patch_array(list_property: list, change: dict[Literal["method","value"], Any]):
    value = change.get('value')
    # Only valid code starting with Python 3.10.
    # match change.get('method'):
    #     case "replace":
    #         return value
    #     case "append":
    #         return list_property + [value]
    #     case "remove":
    #         return [x for x in list_property if x != value]
    #     case "extend":
    #         return list_property + value # type: ignore
    method = change.get('method')
    if method == "replace":
        return value
    elif method == "append":
        return list_property + [value]
    elif method == "remove":
        return [x for x in list_property if x != value]
    elif method == "extend":
        return list_property + value # type: ignore

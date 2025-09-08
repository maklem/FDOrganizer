"""Dummy plugin."""


import io
import json

from typing import Literal, Union

from flask.wrappers import Request, Response

from server.entities.errors import PluginError
from ...entities.folder import Folder
from ...entities.document import Document
from ...util import web_response

def login(request: Request) -> Response:
    """Authenticates with remote APIs. Tokens/usernames/passwords/API keys should be returned in the web response in place of None."""
    request_data = json.loads(request.get_data())
    try:
        # setup required APIs here
        pass
    except:
        raise PluginError(500, 'Example plugin error')
    return web_response(200, "Authentication successful", None)

def get_toplevel(request: Request, auth) -> Union[Response, dict[Literal['folders', 'documents'], list]]:
    """Queries the remote server for package contents."""
    # Setup API again, then query toplevel contents.
    # Example contents:
    return {'folders': [Folder(name = str(i), id = str(i) + "_toplevel", owner = '', documents=[], folders=[], package_id="") for i in range(10)], 'documents': []}
    # id needs to be unique.

def get_collection(collection_id: str, request: Request, auth):
    """Retrieves information about the content of a folder, i.e. number, types and properties of items.
    collection_id is a unique identifier for a folder."""
    # Setup API again.
    if collection_id.endswith('_toplevel'):
        return {
            'folders': [Folder(name='0'+str(i), id=collection_id + "_" + str(i) + "_folder", owner='', documents=[], folders=[], package_id="")
                        for i in range(10)], 'documents': []}
    elif collection_id.endswith('_folder'):
        return {'documents': [Document(name=str(i), size=len(str(i)), type='txt', is_stored=True, owner='', source_id=collection_id+'_'+str(i),
                 source="Dummy") for i in range(10)], 'folders': []}
    # IDs must be unique.


def get_files_with_metadata(ids, request, auth):
    """Retrieves uploaded files together with their corresponding documents."""
    # Setup API again.
    # Prepare file content as BytesIO stream.
    files = [io.BytesIO(id_.split("_")[-1].encode('utf-8')) for id_ in ids]
    documents = [Document(name=id_.split("_")[-1], size=len(id_.split("_")[-1]), type='txt', is_stored=True, owner='', source_id=id_,
                 source="Dummy") for id_ in ids]
    return [{'document': d, 'file': f, 'metadata': None} for d, f in zip(documents, files)]
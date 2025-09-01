'''
    Module for eLabFTW integration. Implements the api call to access eLabFTW.
'''


import io
import json

import elabapi_python
from typing import Literal, Union

import requests #type: ignore
from flask.wrappers import Request, Response
import pathlib

from ...entities.folder import Folder
from ...entities.document import Document
from ...util import web_error, web_response

def get_config():
    config_filepath = pathlib.Path(__file__).parent.resolve().joinpath('config.json')
    with open(config_filepath, encoding="utf-8") as file:
        return json.load(file)


def login(request: Request) -> Response:
    request_data = json.loads(request.get_data())
    api = setup_api(request_data["APIKey"])
    upl = setup_uploads_api(request_data["APIKey"])

    if not (api and upl):
        return web_error(500, "Failed to authenticate with eLabFTW", component="eLabFTW")
    return web_response(200, "Authentication with eLabFTW successful", request_data["APIKey"])


def setup_api(auth):
    try:
        config = elabapi_python.Configuration()
        config.host = get_config()["baseUrl"]
        client = elabapi_python.ApiClient(config)
        client.set_default_header('Authorization', auth)
        exp = elabapi_python.ExperimentsApi(client)
        return exp
    except:
        return None

def setup_uploads_api(auth):
    try:
        config = elabapi_python.Configuration()
        config.host = get_config()["baseUrl"]
        client = elabapi_python.ApiClient(config)
        client.set_default_header('Authorization', auth)
        upl = elabapi_python.UploadsApi(client)
        return upl
    except:
        return None

def get_toplevel(request: Request, auth) -> Union[Response, dict[Literal['folders', 'documents'], list]]:
    '''
        querys the eLabFTW server for collections. returns the collections either as string or json array
    '''
    exp = setup_api(auth)
    experiments = exp.read_experiments()
    folders = list({experiment.modified_at[:4] for experiment in experiments})
    folders.sort(reverse=True)
    return {'folders': [Folder(name = folder, id = folder+"_year", owner = '', documents=[], folders=[], package_id="") for folder in folders], 'documents': []}


def get_filetype(name):
    l = name.split('.')
    if len(l) > 1:
        return l[-1]
    else:
        return ''

def get_collection(collection_id: str, request: Request, auth):
    '''
        get information about the content of an collection. number of items, type of items,.
        required collection_id as arg.
    '''


    exp = setup_api(auth)
    experiments = exp.read_experiments()
    upl = setup_uploads_api(auth)
    if collection_id.endswith("_year"):
        experiments.sort(key=lambda experiment: experiment.title)
        return {'folders': [Folder(name = experiment.title, id = str(experiment.id)+"_experiment", owner = '', documents=[], folders=[], package_id="") for experiment in experiments], 'documents': []}
    elif collection_id.endswith("_experiment"):
        eid = int(collection_id.removesuffix("_experiment"))
        uploads = upl.read_uploads('experiments', eid)
        uploads.sort(key=lambda upload: upload.real_name)
        return {'documents': [Document(name=upload.real_name, size=upload.filesize, type=get_filetype(upload.real_name), is_stored=False, owner='', source_id=str(upload.item_id)+"_"+str(upload.id),
                 source="eLabFTW") for upload in uploads], 'folders': []}


def get_file_id(file_id):
    l = file_id.split("_")
    return [int(i) for i in l]

def get_files_with_metadata(file_ids, request, auth):
    upl = setup_uploads_api(auth)
    uploads = [upl.read_upload('experiments', *get_file_id(file_id)) for file_id in file_ids]
    files = [extract_file(upl,x) for x in uploads]
    documents = [Document(name=upload.real_name, size=upload.filesize, type=get_filetype(upload.real_name), is_stored=True, owner='', source_id=str(upload.item_id)+"_"+str(upload.id),
                 source="eLabFTW") for upload in uploads]
    return [{'document': d, 'file': f, 'metadata': None} for d, f in zip(documents, files)]

def extract_file(api, upload):
    return io.BytesIO(api.read_upload('experiments', upload.item_id, upload.id, format='binary', _preload_content=False).data)
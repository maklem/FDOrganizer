"""Plugin for eLabFTW integration. Implements the API calls required in order to access eLabFTW."""


import io
import json

import elabapi_python
from typing import Literal, Union

import requests #type: ignore
from flask.wrappers import Request, Response
import pathlib

from server.entities.errors import PluginError
from ...entities.folder import Folder
from ...entities.document import Document
from ...util import web_response

def get_config():
    """Loads the config file."""
    config_filepath = pathlib.Path(__file__).parent.resolve().joinpath('config.json')
    with open(config_filepath, encoding="utf-8") as file:
        return json.load(file)


def login(request: Request) -> Response:
    """Authenticates with eLabFTW experiments and uploads APIs."""
    request_data = json.loads(request.get_data())
    setup_experiments_api(request_data["APIKey"])
    setup_uploads_api(request_data["APIKey"])
    return web_response(200, "Authentication with eLabFTW successful", request_data["APIKey"])


def setup_experiments_api(auth):
    """Sets up the experiments API."""
    try:
        config = elabapi_python.Configuration()
        config.host = get_config()["baseUrl"]
        client = elabapi_python.ApiClient(config)
        client.set_default_header('Authorization', auth)
        exp = elabapi_python.ExperimentsApi(client)
        return exp
    except:
        raise PluginError(500, "Failed to authenticate with eLabFTW experiments API")

def setup_uploads_api(auth):
    """Sets up the uploads API."""
    try:
        config = elabapi_python.Configuration()
        config.host = get_config()["baseUrl"]
        client = elabapi_python.ApiClient(config)
        client.set_default_header('Authorization', auth)
        upl = elabapi_python.UploadsApi(client)
        return upl
    except:
        raise PluginError(500, "Failed to authenticate with eLabFTW uploads API")

def get_toplevel(request: Request, auth) -> Union[Response, dict[Literal['folders', 'documents'], list]]:
    """Queries the eLabFTW server for package contents."""
    exp = setup_experiments_api(auth)
    experiments = exp.read_experiments()
    # Retrieves a list of years that experiments were last modified in.
    # This could be optimized using BucketSort/CountingSort if necessary.
    folders = list({experiment.modified_at[:4] for experiment in experiments})
    folders.sort(reverse=True)
    return {'folders': [Folder(name = folder, id = folder+"_year", owner = '', documents=[], folders=[], package_id="") for folder in folders], 'documents': []}


def get_filetype(name):
    return pathlib.Path(name).suffix

def get_collection(collection_id: str, request: Request, auth):
    """Retrieves information about the content of a folder, i.e. number, types and properties of items.
    collection_id is a unique identifier for a folder."""
    exp = setup_experiments_api(auth)
    experiments = exp.read_experiments()
    upl = setup_uploads_api(auth)
    if collection_id.endswith("_year"):
        # A year folder was opened.
        experiments.sort(key=lambda experiment: experiment.title)
        return {'folders': [Folder(name = experiment.title, id = str(experiment.id)+"_experiment", owner = '', documents=[], folders=[], package_id="") for experiment in experiments], 'documents': []}
    elif collection_id.endswith("_experiment"):
        # An experiment folder was opened.
        eid = int(collection_id.removesuffix("_experiment"))
        uploads = upl.read_uploads('experiments', eid)
        uploads.sort(key=lambda upload: upload.real_name)
        experiment = exp.get_experiment(eid)
        # This also creates the metadata.json document.
        return {'documents': [Document(name=upload.real_name, size=upload.filesize, type=get_filetype(upload.real_name), is_stored=False, owner='', source_id=str(upload.item_id)+"_"+str(upload.id),
                 source="eLabFTW") for upload in uploads]+[create_metadata(experiment)[0]], 'folders': []}


def get_file_id(file_id):
    """Deconstructs file_id into constituent integer IDs."""
    l = file_id.split("_")
    return [int(i) for i in l]

def get_files_with_metadata(ids, request, auth):
    """Retrieves uploaded files and constructs metadata."""
    upl = setup_uploads_api(auth)
    exp = setup_experiments_api(auth)
    # This filters out metadata.json from the files because it does not exist on eLabFTW.
    file_ids = list(filter(lambda x: len(get_file_id(x)) == 2, ids))
    # The star expression inputs experiment and upload IDs as parameters.
    uploads = [upl.read_upload('experiments', *get_file_id(file_id)) for file_id in file_ids]
    files = [extract_file(upl, x) for x in uploads]
    documents = [Document(name=upload.real_name, size=upload.filesize, type=get_filetype(upload.real_name), is_stored=True, owner='', source_id=str(upload.item_id)+"_"+str(upload.id),
                 source="eLabFTW") for upload in uploads]
    # This retrieves the experiment from the ID of its corresponding metadata.json file.
    metadata = create_metadata(exp.get_experiment(get_file_id(ids[0])[0]))
    documents.append(metadata[0])
    files.append(metadata[1])
    return [{'document': d, 'file': f, 'metadata': None} for d, f in zip(documents, files)]

def extract_file(api, upload):
    """Extracts a file from an eLabFTW upload."""
    return io.BytesIO(api.read_upload('experiments', upload.item_id, upload.id, format='binary', _preload_content=False).data)

def get_attributes(experiment):
    """Retrieves and filters attributes from an eLabFTW experiment."""
    selected_keys = {'body', 'category', 'category_title', 'comments', 'compounds', 'created_at', 'experiments_links',
                                               'fullname', 'locked_at', 'metadata', 'modified_at', 'page', 'related_experiments_links', 'related_items_links',
                                               'sharelink', 'status_title', 'steps', 'tags', 'timestamped_at', 'title', 'type'}
    return {key:value for key, value in experiment.to_dict().items() if key in selected_keys and value}

def create_metadata(experiment):
    """Creates metadata from an eLabFTW experiment."""
    b = json.dumps(get_attributes(experiment)).encode('utf-8')
    bio = io.BytesIO(b)
    return Document(name="metadata.json", size=len(b), type="json", is_stored=True, owner='', source_id=str(experiment.id), source="eLabFTW"), bio

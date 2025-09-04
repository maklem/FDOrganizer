
###################################
###              import stuff ####
###################################
from ast import List
import io
import json
import mimetypes
from typing import Literal, Union

import requests #type: ignore
from flask.wrappers import Request, Response
import pathlib

from server.entities.errors import PluginError
# from .plugin_document import PluginDocument

from ...services.authentication import user
# from .plugin_folder import PluginFolder
from ...entities.folder import Folder
from ...entities.document import Document
from ...util import web_error, web_response



############################################################
##########  hier sind die Funktionen für Plugins ###########
############################################################

BASEURL = "https://open.fau.de/server/api/"


def login(request: Request) -> Response:
    '''
        authenticate to DSPACE. first get a session token, then authenticate this session token via
        user login
    '''
    # Get session token from Dspace7
    url = BASEURL

    request_data = json.loads(request.get_data())

    response = requests.get(url ,timeout=10)

    try:
        if "DSPACE-XSRF-COOKIE" in response.cookies.get_dict():  # Note if DSPACE calls the Cookie differently this will not work
            token = response.cookies.get_dict()["DSPACE-XSRF-COOKIE"]
            # print(token)
    except (json.JSONDecodeError, KeyError):
        raise PluginError(500, "Failed to receive token from DSpace")

    auth_url = f'{url}authn/login'
    # request_data = json.loads(request.get_data())
    headers = {
               'X-XSRF-TOKEN': token
              }
    # make the cookies dict
    cookies = {
               'DSPACE-XSRF-COOKIE': token
              }  # NOTE: cookie and token are the same @ FAU (otherwise need to extract both)


        # Authorize session via token and username&password

    data = {
            "user": request_data["username"],
            "password": request_data["password"]
           }



    response = requests.post(auth_url, data = data , headers = headers, cookies = cookies, timeout=10)
    if response is None:
        raise PluginError(500, "Failed to authenticate token with DSpace7")
    if response.status_code > 399:
        raise PluginError(response.status_code, response.text)

    # print(response.headers)
    bearer_token = response.headers['Authorization']
    token = response.cookies.get_dict()["DSPACE-XSRF-COOKIE"]
    headers["Authorization"] = bearer_token

    # checkLoginStatus(headers)
    status_response = requests.get(url+"authn/status", headers=headers)
    uuid = status_response.json()['_links']["eperson"]["href"].replace(url +"eperson/epersons/","")
    return  web_response(200, "Authentication with DSpace successful", {'X-XSRF-TOKEN': token, 'Authorization': bearer_token,  "uuid" : uuid})
    # return {'X-XSRF-TOKEN': token, 'Authorization': bearer_token, "uuid" : uuid}



def get_toplevel(request: Request, auth) -> Union[Response, dict[Literal['folders', 'documents'], list]]:
    url = BASEURL

    # hier suchen wir nach allen vom User hochgeladenen Items in DSPACE

    response  = requests.get(url + "submission/workspaceitems/search/findBySubmitter?uuid=" + str(auth["uuid"]),
                   headers={'Authorization': auth["Authorization"]})
    # print(response.json())

    # alle gefundenen Workspaceitems
    itemlist = response.json()["_embedded"]["workspaceitems"]

    # print(itemList)
    folders = []

    for item in itemlist:
        id = item["id"] #die Item ID ist nicht die uuid des Items
        try:
            displayname = item['sections']["traditionalpageone"]["dc.title"][0]["value"] # dirty way zum names des items
        except KeyError:
            displayname = item["sections"]["identifiers"]["doi"]
        username = user(request) # auth["uuid"]  # wäre uuid des Users aus Login
        # bundles = item["_embedded"]["item"]["_links"]["bundles"]["href"]
        folders.append(Folder(name=displayname, id=id, owner=username, documents=[], folders=[], package_id=""))

    if response.status_code > 399:
        raise PluginError(response.status_code, response.text)

    return {'folders': folders, 'documents': []}



def get_collection(collection_id: str, request: Request, auth):
    '''
        get information about the content of a collection. number of items, type of items,.
        required collection_id as arg.
    '''

    url = BASEURL

    headers = {
        'X-XSRF-TOKEN': auth["X-XSRF-TOKEN"],
        'Authorization': auth["Authorization"]
    }
    # make the cookies dict
    cookies = {
        "DSPACE-XSRF-COOKIE": auth["X-XSRF-TOKEN"]}  # NOTE: cookie and token are the same @ FAU (otherwise need to extract both in InitialToken function)

    # holen der Itemsdaten nach item-ID
    itemGet =  requests.get(url + "submission/workspaceitems/" + str(collection_id) + "/item", headers=headers)
    if itemGet.status_code > 399:
        raise PluginError(itemGet.status_code, itemGet.text)
    # jetzt daraus die uuid des Items
    itemuuid = itemGet.json()["id"]
    # bundle des workspacceitems
    bundleGet = requests.get(url + "core/items/" + str(itemuuid) + "/bundles", headers=headers)
    if bundleGet.status_code > 399:
        raise PluginError(bundleGet.status_code, bundleGet.text)
    # uuid des Bundels
    bundleUUID = bundleGet.json()["_embedded"]["bundles"][0]["uuid"]

    # die bitstreams der Files in dem bundle
    bitstreamGet = requests.get(url + "core/bundles/" + str(bundleUUID) + "/bitstreams", headers=headers)
    if bitstreamGet.status_code > 399:
        raise PluginError(bitstreamGet.status_code, bitstreamGet.text)

    bitstream = bitstreamGet.json()
    # Convert files for Frontend
    files = [convert_file(stream , user(request)) for stream in bitstream["_embedded"]["bitstreams"]]
    return {'documents': files, 'folders': []}


def convert_file(stream: dict, user: str, is_stored: bool = False) -> Document:
    # print(stream)
    displayname = str(stream["name"])
    mimetype = mimetypes.guess_type(displayname)[0] or 'application/octet-stream' # could also be extracted directly via API call for format
    size = stream["sizeBytes"]
    username =  user
    file_id = str(stream["uuid"])
    return Document(name = displayname, size = size, type = mimetype, is_stored = is_stored, owner = username, source_id= file_id, source="DSpace")


def get_files_with_metadata(file_ids, request, auth):
    # print(file_ids)

    url = BASEURL
    bearer_token = auth["Authorization"]
    xsrf_token = auth["X-XSRF-TOKEN"]

    headers = {
        'X-XSRF-TOKEN': xsrf_token,
        'Authorization': bearer_token
    }
    # make the cookies dict
    cookies = {
        "DSPACE-XSRF-COOKIE": xsrf_token}

    # 'href': 'https://open.fau.de/server/api/core/bitstreams/11821720-fb67-40f2-a132-dd395b1b49b4/format'
    files = []
    documents = []
    metadata = []
    for id in file_ids:
        response = requests.get(url+"core/bitstreams/" + str(id) + "/content", headers=headers, timeout=10) # https://open.fau.de/server/api/core/bitstreams/{uuid}/content'
        # print(response.content)
        if response.status_code > 399:
            raise PluginError(response.status_code, response.text)
        file_content = response.content
        file = io.BytesIO(file_content)
        files.append(file)
        response2 = requests.get(url + "core/bitstreams/" + str(id), headers=headers, timeout=10)
        documents.append(convert_file(response2.json(), user(request), is_stored=True))
        metadata.append(extract_metadata(response2.json()))
            # Convert files for Frontend


    # metadata = [extract_metadata(x) for x in objects]

    results = []
    for index in range(len(files)):
        results.append({'document': documents[index], 'file': files[index], 'metadata': metadata[index]})
    # print(documents)
    return results
'''
def checkLoginStatus(header):
    status_response = requests.get("https://open.fau.de/server/api/authn/status", headers=header)
    # print("Dummy")
    # print("Dummy")
    # print(status_response.json())
    return status_response
'''

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


###################################################
#####################################################
#######################################################
#########################################################
###########################################################



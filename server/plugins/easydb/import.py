'''
    Module for easydb integration. Implements the api call to access easydb repository
'''


import json
import mimetypes
import time
import uuid

import requests
from flask.wrappers import Request, Response
from pkg_resources import resource_filename

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


# def deauthenticate_easydb():
#     '''
#         deauthenticate from easydb. get token from header and then deauthenticate it. expects a "token" parameter
#     '''
#     token = request.headers["Token"]
#     if not token:
#         return json.dumps({"Error": "Missing token parameter"}), \
#                 500,{"Content-Type": "application/json"}
#     url = lzv_util.CONFIGPARAMS["easydbBaseUrl"] + "/session/deauthenticate?token=" + token

#     response = requests.post(url)
#     if not response:
#         return json.dumps({"Error": "Failed to deauthenticate token to easydb"}), \
#                 500,{"Content-Type": "application/json"}
#     return response.text


def get_toplevel(request: Request, auth):
    '''
        querys the easydb server for collections. returns the collections either as string or json array
    '''
    # search_query = {
    #     "type" : "object",
    #     "offset": 8300,
    #     "search" : [
            # {
            #     "type" : "in",
            #     "objecttype": "object",
            #     "bool" : "must",
            #     "fields" : [
            #         "_owner.user._id"
            #     ],
            #     "in" : [
            #         auth.get('user')
            #     ]

            # },
            # {
            #     "type" : "in",
            #     "bool" : "must",
            #     "fields" : [
            #         "collection.is_system_collection"
            #     ],
            #     "in" : [
            #         False
            #     ]

            # },
    #     ]
    # }
    # url = f'{get_config()["baseUrl"]}/search?token={auth.get("token")}'
    # response = requests.post(url, json= search_query, timeout=10)
    # if response.status_code > 399:
    #     print('didnt work')
    #     print(response.text)
    # result_list = json.loads(response.text)
    # with open('debug_objects.json', 'w', encoding='utf-8') as debug:
    #     debug.write(response.text)
    #     debug.close()
    # filtered_list = list(filter(lambda o: o.get('_owner') is not None, result_list.get('objects')))
    # print(filtered_list)
    # print(list(map(convert_file, result_list.get('objects'))))
    # objects = result_list.get('objects')
    # objects = list(map(convert_file, objects))

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
    result_list = json.loads(response.text)
    collections = result_list.get('objects')
    collections = list(map(convert_collection, collections))
    # if len(collections) == 0:
    #     return web_response(201, "No collections found")
    return web_response(200, details=collections)

def convert_collection(collection) -> Folder:
    count = collection.get('_count')
    collection = collection.get('collection')
    displayname = collection.get('displayname').get('de-DE')
    collection_id = collection.get('_id')
    return {'count': count, 'displayname': displayname, 'id': collection_id}


def convert_file(obj) -> Document:
    inner_object = obj.get('object')
    file_id = obj.get('_uuid')

    file = inner_object.get('file')[0]

    displayname = f'{file.get("original_filename")}'
    extension = f'{file.get("extension")}'
    size = file.get('filesize')
    url = file.get('versions').get('original').get('download_url')

    return {'displayname': displayname, 'id': file_id, 'size': size, 'url': url, 'type': extension}

def get_collection(request: Request, auth):
    '''
        get information about the content of an collection. number of items, type of items,.
        required collection_id as arg.
        Returns:
    '''
    collection_id = request.view_args.get("collection")
    if collection_id is None:
        return web_error(400, 'No valid Collection ID provided', component="Easy DB")

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
    result_list = json.loads(response.text)
    files = result_list.get('objects')
    files = list(filter(lambda file: file.get('object').get('file'), files))
    files = list(map(convert_file, files))

    return web_response(200, details=files)


# def get_collection_info_by_id(token, collection_id):
#     '''
#         Calls get_colleciton_info and filters the resulting collection_information info. Returns only
#         the collection with ['collection']['_id'] == id as json
#     '''
    collections = get_collections_from_easydb(token, return_as_string=False)
    filtered = [coll for coll in collections if coll['collection']['_id'] == int(collection_id)]
    # for coll in collections:
    #     print(coll['collection']['_id'])
    #     print(_id)
    #     if coll['collection']['_id'] == int(_id):
    #         print("!")
    #         filtered.append(coll)
    # if len(filtered) > 0:
    #     return filtered[0] #should always be only one element
    # return False

def download_collection():
    '''
        Method for downloading all files in a collection from easydb. expects an argument id, with
        the collection_id. All files are downloaded to the local file_server and storage entries are
        created. also creates a package, containing all files from the collection.
    '''
    user_id = request.cookies["session_user"]
    token = request.headers["Token"]
    if not token or token == "":
        return json.dumps({"Error": "Missing or no valid token parameter"}), \
                500,{"Content-Type": "application/json"}
    collection_id = request.args.get("collection_id")
    collection_info = get_collection_info_by_id(token,collection_id)
    collection_objects = query_for_collection_object_info(token, collection_id, return_as_string=False)
    if not collection_info:
        return json.dumps({"Error": "Finding Collection with ID in easydb"}), \
                500,{"Content-Type": "application/json"}
    storage_files = []
    mimetypes.init()
    couch_token = lzv_util.authenticate_couchdb()
    couch_header = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "Cookie": couch_token,
        }
    if collection_info:
        collection_package = create_package_for_collection(user_id, collection_info)
        for obj in collection_objects['objects']:
            if obj['object']['file'][0]['versions']['original']['_download_allowed']:
                storage_file = create_storage_data_structure_from_easydb(user_id, obj)
                response = requests.get(obj['object']['file'][0]['versions']['original']['download_url'])
                if not response:
                    break
                file_data = response.content
                couchdb_url = (
                    lzv_util.CONFIGPARAMS["couchDBBaseURL"]
                    + "/"
                    + lzv_util.CONFIGPARAMS["couchDBDocumentDatabaseName"]
                    )
                json_answer = json.loads(
                    requests.post(couchdb_url, headers=couch_header, data=json.dumps({})).text
                    )
                print("coudchdb:")
                print(json.dumps(json_answer))
                couch_header["If-Match"] = json_answer["rev"]
                file_mimetype = mimetypes.types_map['.' + obj['object']['file'][0]['extension']]
                print(file_mimetype)
                couch_header["Content-Type"] = file_mimetype
                couchdb_url = couchdb_url + "/" + json_answer["id"] + "/" + json_answer["id"]
                att_create_response = requests.put(
                couchdb_url, headers=couch_header, data=file_data
                )
                storage_file["data_object_metadata"]["is_stored"] = bool(att_create_response)
                storage_file["data_object_metadata"]["doc_id"] = json_answer["id"]
                storage_file["data_object_metadata"]["filename"] = obj['object']['file'][0]['original_filename']
                storage_file["data_object_metadata"]["db_filename"] = json_answer["id"]
                storage_file["data_object_metadata"]["file_type"] = file_mimetype
                storage_files.append(storage_file)
        # for storage_file in storage_files:
        print("+++")
        collection_package['child_data_objects'] = [x['package_id'] for x in storage_files]
        print(json.dumps(collection_package))
        storage_files.append(collection_package)
        print("---")
        print(json.dumps(storage_files))
        lzv_util.add_to_storage(storage_files)
        return json.dumps({"Success": "All good"}), \
                200,{"Content-Type": "application/json"}
    return json.dumps({"Error": "Failed to get collection info from easydb"}), \
                400,{"Content-Type": "application/json"}


def create_package_for_collection(user_id, collection):
    '''
        created the storage generic:data_scructure for each file. expects a single file from easydb
    '''
    # print("+++++++++++++++")
    # print(json.dumps(collection))
    # print(json.dumps(collection['collection']['displayname']))
    # print(collection['collection']['displayname'][list(collection['collection']['displayname'])[0]])
    # print("++++++++++++++++")
    return {
                "package_id": str(uuid.uuid4()),
                "type": "PACKAGE",
                "owner": user_id,
                "name": collection['collection']['displayname'][list(collection['collection']['displayname'])[0]],#displayname at fist position is german, if not available english, and so on. so taking the first element should take German, then English
                "package_object_metadata": {
                    "creation_date": time.strftime("%Y-%m-%dT%T.000+0000"),
                    "last_change": time.strftime("%Y-%m-%dT%T.000+0000"),
                    "creator": user_id,
                    "modifiable": False,
                },
                "child_data_objects": [],
    }

def create_storage_data_structure_from_easydb(user_id, file_info):
    '''
        created the storage generic:data_scructure for each file. expects a single file from easydb
    '''
    print(json.dumps(file_info))
    return {
        "package_id": str(uuid.uuid4()),
        "type": "DATA",
        "owner": user_id,
        "name": file_info['object']['file'][0]['original_filename'],
        "data_object_metadata": {
            "content_origin": "easydb",
            "origin_uuid": file_info["_uuid"],
            "export_date": time.strftime("%Y-%m-%dT%T.000+0000"),
            "export_user": user_id,
            "is_stored": False,
            "checksums" : [{
                "type" : "SHA224",
                "hash" : file_info["object"]["file"][0]["technical_metadata"]["file_sha224_checksum"]
            }]
        },
        "origin_metadata": file_info#TODO define the origin_metadata for easydb. This needs to be analyzed from available metadata
    }


def get_easydb_storage_data():
    """
    Routed from /easydb/storage
    Requests the storage file, containg metadata about stored files for the requesting user
    """
    user_id = request.cookies["session_user"]
    out = get_easydb_data(user_id, return_as_string=False)
    return json.dumps(out["docs"])


def get_easydb_data(user_id, return_as_string=False):
    """
    Returns the easydb data for @user_id either as (json)string or object.
    """
    query = {
        "selector": {
            "owner": user_id,
            "type": "DATA",
            "data_object_metadata.content_origin": "easydb",
        }
    }
    response = query_db(query, lzv_util.CONFIGPARAMS["couchDBStorageDatabaseName"])
    return response if return_as_string else json.loads(response)

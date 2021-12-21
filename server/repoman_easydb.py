'''
    Module for easydb integration. Implements the api call to access easydb repository
'''


import json
import time
import uuid
import requests
import urllib.request
from flask import Blueprint, request
import lzv_util
import mimetypes
from pathlib import Path


rep_easydb = Blueprint('easydb', __name__)


@rep_easydb.route("/auth/login" , methods=["POST"])
def authenticate_easydb():
    '''
        authenticate to easydb. first get a session token, then authenticate this session token via
        user login
    '''
    result = lzv_util.validate_user_session(request)
    if not result["success"]:
        return result["return_error"]
    url = lzv_util.CONFIGPARAMS["easydbBaseUrl"] + "/session"
    response = requests.get(url)
    if not response:
        return json.dumps({"Error": "Failed to receive token from easydb"}), \
                500,{"Content-Type": "application/json"}
    token = json.loads(response.text)['token']

    url = url + "/authenticate"
    request_data = json.loads(request.get_data())
    payload = { "token" : token,\
                "login": request_data["user"],\
                "password": request_data["password"] }
    response = requests.post(url, payload)
    if not response:
        return json.dumps({"Error": "Failed to authenticate token with easydb"}), \
                500,{"Content-Type": "application/json"}
    return response.text


@rep_easydb.route("/auth/logout" , methods=["POST"])
def deauthenticate_easydb():
    '''
        deauthenticate from easydb. get token from header and then deauthenticate it. expects a "token" parameter
    '''
    result = lzv_util.validate_user_session(request)
    if not result["success"]:
        return result["return_error"]
    token = request.headers["Token"]
    if not token:
        return json.dumps({"Error": "Missing token parameter"}), \
                500,{"Content-Type": "application/json"}
    url = lzv_util.CONFIGPARAMS["easydbBaseUrl"] + "/session/deauthenticate?token=" + token

    response = requests.post(url)
    if not response:
        return json.dumps({"Error": "Failed to deauthenticate token to easydb"}), \
                500,{"Content-Type": "application/json"}
    return response.text


@rep_easydb.route("/collections", methods=["GET"])
def get_collections():
    '''
        Get all collections for the authenticated user. Only deliver collections which are owned by
        the user. Expects token for easydb to be part of the request header
    '''
    result = lzv_util.validate_user_session(request)
    if not result:
        return result["return_error"]
    token = request.headers["Token"]
    if not token or token == "":
        return json.dumps({"Error": "Missing or no valid token parameter"}), \
                500,{"Content-Type": "application/json"}
    response = get_collections_from_easydb(token, return_as_string=True)
    return response

def get_collections_from_easydb(token, return_as_string=True):
    '''
        querys the easydb server for collections. returns the collections either as string or json array
    '''
    url = lzv_util.CONFIGPARAMS["easydbBaseUrl"] + '/collection/list?token=' + token
    response = requests.get(url)
    arr = json.loads(response.text)
    #first element is always the technical root collection
    arr.pop(0)
    if return_as_string:
        return json.dumps(arr)
    return arr

@rep_easydb.route("/collections/info", methods=["GET"])
def get_collection_info():
    '''
        get information about the content of an collection. number of items, type of items,.
        required collection_id as arg.
        Returns:
    '''
    result = lzv_util.validate_user_session(request)
    if not result:
        return result["return_error"]
    token = request.headers["Token"]
    if not token or token == "":
        return json.dumps({"Error": "Missing or no valid token parameter"}), \
                500,{"Content-Type": "application/json"}
    collection_id = request.args.get("collection_id")
    response = query_for_collection_object_info(token, collection_id)
    print("after search query:")
    print(response)
    if response:
        return response
    return rep_easydb.response_class(
        response=json.dumps({"Error": "Failed to get collection info from easydb"}),
        status=400,
        mimetype='application/json')

def query_for_collection_object_info(token, collection_id, return_as_string=True):
    '''
        requests info for als objects in a collection with collection_id from easydb instance.
        returns text file with json structure with collection info.
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
    url = lzv_util.CONFIGPARAMS["easydbBaseUrl"] + "/search?token=" + token
    response = requests.post(url, json.dumps(search_query))
    if response:
        if return_as_string:
            return response.text
        return json.loads(response.text)

    return False


def get_collection_info_by_id(token, collection_id):
    '''
        Calls get_colleciton_info and filters the resulting collection_information info. Returns only
        the collection with ['collection']['_id'] == id as json
    '''
    collections = get_collections_from_easydb(token, return_as_string=False)
    filtered = [coll for coll in collections if coll['collection']['_id'] == int(collection_id)]
    # for coll in collections:
    #     print(coll['collection']['_id'])
    #     print(_id)
    #     if coll['collection']['_id'] == int(_id):
    #         print("!")
    #         filtered.append(coll)
    if len(filtered) > 0:
        return filtered[0] #should always be only one element
    return False

@rep_easydb.route("/collections/download", methods=["GET"])
def download_collection():
    '''
        Method for downloading all files in a collection from easydb. expects an argument id, with
        the collection_id. All files are downloaded to the local file_server and storage entries are
        created. also creates a package, containing all files from the collection.
    '''
    result = lzv_util.validate_user_session(request)
    if not result["success"]:
        return result["return_error"]
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
                couchdb_url = couchdb_url + "/" + json_answer["id"] + "/"
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
    return {
        "package_id": str(uuid.uuid4()),
        "type": "DATA",
        "owner": user_id,
        "name": file_info['object']['file'][0]['original_filename'],
        "data_object_metadata": {
            "content_origin": "easydb",
            "export_date": time.strftime("%Y-%m-%dT%T.000+0000"),
            "export_user": user_id,
            "is_stored": False,
        },
        "origin_metadata": file_info#TODO define the origin_metadata for easydb. This needs to be analyzed from available metadata
    }
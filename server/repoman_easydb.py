'''
    Module for easydb integration. Implements the api call to access easydb repository
'''


import json
import time
import uuid
import requests
from flask import Blueprint, request
import lzv_util


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
        deauthenticate from easydb. get token form args and then deauthenticate it. expects a "token" parameter
    '''
    result = lzv_util.validate_user_session(request)
    if not result["success"]:
        return result["return_error"]
    token = request.args.get("token")
    if not token:
        return json.dumps({"Error": "Missing token parameter"}), \
                500,{"Content-Type": "application/json"}
    url = lzv_util.CONFIGPARAMS["easydbBaseUrl"] + "/session/deauthenticate?token=" + token

    response = request.post(url)
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
    url = lzv_util.CONFIGPARAMS["easydbBaseUrl"] + '/collection/list?token=' + token
    response = requests.get(url)
    arr = json.loads(response.text)
    arr.pop(0)
    print(json.dumps(arr))
    return json.dumps(arr)


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
    print("after search query:")
    print(response.text)
    if response:
        return response.text
    return "Error"
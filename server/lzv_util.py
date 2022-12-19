'''
LZVUTIL module. general functions for usage in lzv application. no anchors are handled in this file
'''

# With Review Process:
# TODO: Put permissions for users into Database
# TODO: Create Admin-Panel to manage user permissions

import hashlib
import json
from typing import Any, Optional, Union
from flask import make_response

import requests
from pkg_resources import resource_filename

CONFIGPARAMS = {}
with open(resource_filename(__name__, "./conf/config.json"), encoding='utf-8') as f:
    CONFIGPARAMS = json.load(f)


def get_config() -> dict[str, Union[str, list[str]]]:
    with open(resource_filename(__name__, "./conf/config.json"), encoding="utf-8") as config:
        return json.load(config)


def check_user_permission_review(user_id):
    """
    Check if user_id is in config file named under REVIEW_PERMITTED_USERS
    """
    for val in CONFIGPARAMS["REVIEW_PERMITTED_USERS"]:
        if val == user_id:
            return True
    return False

def authenticate_couchdb():
    """
    Authenticate to CouchDB and return login token
    """
    url = CONFIGPARAMS["couchDBBaseURL"] + "/_session"
    data = (
        "name="
        + CONFIGPARAMS["couchDBAdmin"]
        + "&password="
        + CONFIGPARAMS["couchDBPassword"]
    )
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    response = requests.post(url, data=data, headers=headers)
    if response.status_code == 200:
        cookie = response.headers["Set-Cookie"]
        couchdb_token = cookie[: cookie.find(";")]
        return couchdb_token
    return False


def query_db(query, db_url_suffix):
    """
    Query the storage Couch db with given query json object and return the result.
    Retrns output of couchdb query as text, needs to be parsed by json parser to sue as object
    """
    token = authenticate_couchdb()
    if not token:
        return (
            json.dumps({"Result": "Internal Server Error"}),
            500,
            {"Content-Type": "application/json"},
        )
    couchdb_url = CONFIGPARAMS["couchDBBaseURL"] + \
        "/" + db_url_suffix + "/_find"
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "Cookie": token,
    }
    response = requests.post(
        couchdb_url, headers=headers, data=json.dumps(query))
    return response.text


def add_to_storage(add_elements):
    """
    adds new elements to storage database. does not check for integrity, or if files already
    exist. if files could already exist use updata_storage()
    """

    print("in add elements")
    url = (
        CONFIGPARAMS["couchDBBaseURL"]
        + "/"
        + CONFIGPARAMS["couchDBStorageDatabaseName"]
    )
    token = authenticate_couchdb()
    if not token:
        return
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "Cookie": token,
    }

    for item in add_elements:
        print("adding item:")
        print(json.dumps(item))
        response = requests.post(url, headers=headers, data=json.dumps(item))
        print(response.text)


def update_storage(add_elements):
    """
    updates documents in the storage database. If a package already exists with the id, it is
    updated to the new revision. if it does not exist yet, it is only added to db.
    """
    url = (
        CONFIGPARAMS["couchDBBaseURL"]
        + "/"
        + CONFIGPARAMS["couchDBStorageDatabaseName"]
    )
    token = authenticate_couchdb()
    if not token:
        return
    for item in add_elements:
        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "Cookie": token,
        }
        query = {"selector": {
            "owner": item["owner"], "package_id": item["package_id"]}}
        response = json.loads(
            query_db(
                query, CONFIGPARAMS["couchDBStorageDatabaseName"])
        )
        if len(response["docs"]) >= 0:
            headers["If-Match"] = response["docs"][0]["_rev"]
            t_url = url + "/" + response["docs"][0]["_id"]
            requests.put(t_url, headers=headers, data=json.dumps(item))
        else:
            requests.post(url, headers=headers, data=json.dumps(item))


def calculate_sha224_from_file(filename):
    '''
    calculate the sha224 of a file in a memory-efficient way. returns hexdigest of hash
    '''
    BLOCK_SIZE = 65536  # 64kB

    sha224 = hashlib.sha224()

    with open(filename, 'rb') as f:
        while True:
            data = f.read(BLOCK_SIZE)
            if not data:
                break
            sha224.update(data)
    return sha224.hexdigest()


def calculate_sha224_from_data(data):
    '''
    calculate the sha224 of binary data. returns hexdigest of hash
    '''
    sha224 = hashlib.sha224()
    sha224.update(data)
    return sha224.hexdigest()


def calculate_md5_from_file(filename):
    '''
    calculate the md5 of a file in a memory-efficient way. returns hexdigest of hash
    '''
    BLOCK_SIZE = 65536  # 64kB

    md5 = hashlib.md5()

    with open(filename, 'rb') as f:
        while True:
            data = f.read(BLOCK_SIZE)
            if not data:
                break
            md5.update(data)
    return md5.hexdigest()


def calculate_md5_from_data(data):
    '''
    calculate the md5 of binary data. returns hexdigest of hash
    '''
    md5 = hashlib.md5()
    md5.update(data)
    return md5.hexdigest()

def web_error(code: int, message:str, stacktrace: Optional[str | list[str]] = None, component = "SERVER"):
    error_data: dict[str, str | list[str]] = {
        'message': message,
        'component': component
    }
    if stacktrace is not None:
        error_data['stacktrace'] = stacktrace
    return make_response(json.dumps(error_data), code)

def web_response(code: int, message:Optional[str] = None, details: Optional[Union[dict[str, Any],list]] = None):
    if message is None and details is None:
        return make_response(code)
    if details is None:
        return make_response(json.dumps(
            {
                'message': message,
            }
        ), code)
    return make_response(json.dumps(details), code)
    
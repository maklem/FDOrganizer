'''
LZVUTIL module. general functions for usage in lzv application. no anchors are handled in this file
'''

import json
import requests
from flask import session
import secrets
import ldap
import hashlib

DEBUG = 1

FAILED_AUTHENTICATION = "Failed Authentication, please login to use this service!"

CONFIGPARAMS = {}
with open("/server/lzv/server/conf/config.json") as f:
    CONFIGPARAMS = json.load(f)

def check_user_permission_review(user_id):
    """
    Check if user_id is in config file named under REVIEW_PERMITTED_USERS
    """
    for val in CONFIGPARAMS["REVIEW_PERMITTED_USERS"]:
        if val == user_id:
            return True
    return False


def secure_username(user_id):
    """
    This should verify that the user_id is a secure string. This needs to be adapted dependent
    on the possible user_ids that exist in the system. Prevent malicious usernames, since this
    is user regularly to query the db. f.e. user_id = '{ "selector" : ...}' could be harmfull!
    """
    # TODO fill this function and every appearance of user_id which if taken from a cookies needs to be secured


def create_sessionid():
    """
    Creates a cryptographically-secure, URL-safe string
    """
    return secrets.token_urlsafe(64)


def create_user_session(userid):
    """
    create new session for user. check if correct credentials to ad if true, create new session
    """
    session[userid] = create_sessionid()


def check_session(userid, sessionid):
    """
    check if provided session id is valid
    """
    return session.get(userid) == sessionid


def get_sessionid(userid):
    """
    return the session id for userid
    """
    return session.get(userid)


def logout_session(userid):
    """
    deletes the session object for user userid
    """
    session.pop(userid)


def authenticate_ldap(uname, pword):
    """
    Authenticate against LDAP Server, return true if uname,pword is correct, false else
    """
    ldap_server = "ldaps://proxy-ubtrz.uni-bayreuth.de:636"
    ldap_base = "ou=users,ou=rz-ad,o=uni-bayreuth"
    user_dn = "cn=" + uname + "," + ldap_base
    try:
        connect = ldap.initialize(ldap_server)
        connect.bind_s(user_dn, pword)
        connect.unbind_s()
        return True
    except ldap.LDAPError:
        connect.unbind_s()
        return False


def validate_user_session(request):
    '''
        checks request for session_user and session_auth object. validates these against local
        session files. returns {"success": TRUE/FALSE, "return_error": {
            {"Error": FAILED_AUTHENTICATION},
            401,
            {"Content-Type": "application/json"}
        }}
    '''
    if "session_user" in request.cookies and "session_auth" in request.cookies:
        if check_session(request.cookies["session_user"], request.cookies["session_auth"]):
            return {"success" : True}
    return {
        "success" : False,
        "return_error" :{
            "Error": FAILED_AUTHENTICATION,
            "code" : "401",
            "Content-Type": "application/json"
        }
    }


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
    couchdb_url = CONFIGPARAMS["couchDBBaseURL"] + "/" + db_url_suffix + "/_find"
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "Cookie": token,
    }
    response = requests.post(couchdb_url, headers=headers, data=json.dumps(query))
    return response.text


def add_to_storage(add_elements):
    """
    adds new elements to storage database. does not check for integrity, or if files already
    exist. if files could already exist use updata_storage()
    """
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
        response = requests.post(url, headers=headers, data=json.dumps(item))


def update_storage(add_elements):
    """
    updates documents in the storage database. If a package already exists with the id, it is
    updated to the new revision. if it does not exist yet, it is only added to db.
    """
    url = (
        lzv_util.CONFIGPARAMS["couchDBBaseURL"]
        + "/"
        + lzv_util.CONFIGPARAMS["couchDBStorageDatabaseName"]
    )
    token = lzv_util.authenticate_couchdb()
    if not token:
        return
    for item in add_elements:
        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "Cookie": token,
        }
        query = {"selector": {"owner": item["owner"], "package_id": item["package_id"]}}
        response = json.loads(
            lzv_util.query_db(query, lzv_util.CONFIGPARAMS["couchDBStorageDatabaseName"])
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
    BLOCK_SIZE = 65536  #64kB

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
    BLOCK_SIZE = 65536  #64kB

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
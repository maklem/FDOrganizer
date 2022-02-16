"""
Software for LZV Server.
"""
import time
from pathlib import Path
import shutil
import os
import uuid
import json
import secrets
import ldap
import requests
import mets
import sys

# from flask import Flask, session
from flask import Flask, request, render_template
from flask_session import Session
from flask_cors import CORS
from werkzeug.utils import secure_filename
from repoman_labfolder import rep_labfolder
from repoman_easydb import rep_easydb
import lzv_util

DEBUG = 1
# ----------------------initialization------------------------------------------

APP = Flask(__name__)
APP.secret_key = "any random string"
APP.config["SESSION_TYPE"] = "filesystem"
APP.config["PERMANENT_SESSION_LIFETIME"] = 43200
APP.config["SESSION_PERMANENT"] = False
APP.config["UPLOAD_FOLDER"] = lzv_util.CONFIGPARAMS["USR_UPLOAD_TMP_FOLDER"]
CORS(APP)
Session(APP)
APP.register_blueprint(rep_labfolder, url_prefix='/labfolder')
APP.register_blueprint(rep_easydb, url_prefix='/easydb')
# print(APP.url_map)

# ----------------------Page Navigation-----------------------------------------
@APP.route("/")
def navhome():
    """
    Navigation to site Home
    """
    if not "session_user" in request.cookies or not "session_auth" in request.cookies:
        return render_template("login.html")
    if not lzv_util.check_session(
            request.cookies["session_user"], request.cookies["session_auth"]
    ):
        return render_template("login.html")
    return render_template("index.html")


@APP.route("/impressum")
def navimpressum():
    """
    Navigation to site Impressum
    """
    if not "session_user" in request.cookies or not "session_auth" in request.cookies:
        return render_template("login.html")
    if not lzv_util.check_session(
            request.cookies["session_user"], request.cookies["session_auth"]
    ):
        return render_template("login.html")
    return render_template("impressum.html")


@APP.route("/history")
def navhistory():
    """
    Navigation to site History
    """
    if not "session_user" in request.cookies or not "session_auth" in request.cookies:
        return render_template("login.html")
    if not lzv_util.check_session(
            request.cookies["session_user"], request.cookies["session_auth"]
    ):
        return render_template("login.html")
    return render_template("history.html")


@APP.route("/labfolder")
def navlabfolder():
    """
    Navigation to site Labfolder
    """
    if not "session_user" in request.cookies or not "session_auth" in request.cookies:
        return render_template("login.html")
    if not lzv_util.check_session(
            request.cookies["session_user"], request.cookies["session_auth"]
    ):
        return render_template("login.html")
    return render_template("labfolder.html")


@APP.route("/easydb")
def naveasydb():
    """
    Navigation to site easyDB
    """
    if not "session_user" in request.cookies or not "session_auth" in request.cookies:
        return render_template("login.html")
    if not lzv_util.check_session(
            request.cookies["session_user"], request.cookies["session_auth"]
    ):
        return render_template("login.html")
    return render_template("easydb.html")


@APP.route("/metadata")
def navmetadata():
    """
    Navigation to site metadata
    """
    if not "session_user" in request.cookies or not "session_auth" in request.cookies:
        return render_template("login.html")
    if not lzv_util.check_session(
            request.cookies["session_user"], request.cookies["session_auth"]
    ):
        return render_template("login.html")
    return render_template("metadata.html")


@APP.route("/lzv")
def navlzvingest():
    """
    Navigation to site ingest
    """
    if not "session_user" in request.cookies or not "session_auth" in request.cookies:
        return render_template("login.html")
    if not lzv_util.check_session(
            request.cookies["session_user"], request.cookies["session_auth"]
    ):
        return render_template("login.html")
    return render_template("lzvingest.html")


@APP.route("/package")
def navlzvpackage():
    """
    Navigation to site ingest
    """
    if not "session_user" in request.cookies or not "session_auth" in request.cookies:
        return render_template("login.html")
    if not lzv_util.check_session(
            request.cookies["session_user"], request.cookies["session_auth"]
    ):
        return render_template("login.html")
    return render_template("lzvpackage.html")


@APP.route("/upload")
def navupload():
    """
    Navigation to site ingest
    """
    if not "session_user" in request.cookies or not "session_auth" in request.cookies:
        return render_template("login.html")
    if not lzv_util.check_session(
            request.cookies["session_user"], request.cookies["session_auth"]
    ):
        return render_template("login.html")
    return render_template("upload.html")


@APP.route("/review")
def navlzvreview():
    """
    Navigation to site review. Need to check auth for reviewer
    """
    if not "session_user" in request.cookies or not "session_auth" in request.cookies:
        return render_template("login.html")
    if not lzv_util.check_session(
            request.cookies["session_user"], request.cookies["session_auth"]
    ):
        return render_template("login.html")
    if not lzv_util.check_user_permission_review(request.cookies["session_user"]):
        return render_template("index.html")
    return render_template("lzvreview.html")


@APP.route("/login", methods=["GET"])
def navlogin():
    """
    Navigation to login site
    """
    return render_template("login.html")


@APP.route("/login", methods=["POST"])
def login_lzv():
    """
    Login to lzv site. Performs a lookup to ldap server to verify credentials.
    Returns a session token to user, to authenticate your session against.
    """
    if "session_user" in request.cookies and "session_auth" in request.cookies:
        if lzv_util.check_session(
                request.cookies["session_user"], request.cookies["session_auth"]
        ):
            return (
                json.dumps(
                    {
                        "session_id": request.cookies["session_auth"],
                        "username": request.cookies["session_user"],
                    }
                ),
                200,
                {"Content-Type": "application/json"},
            )
    data = json.loads(request.get_data())
    if lzv_util.authenticate_ldap(data["username"], data["password"]):
        lzv_util.create_user_session(data["username"])
        return (
            json.dumps(
                {
                    "session_id": lzv_util.get_sessionid(data["username"]),
                    "username": data["username"],
                }
            ),
            200,
            {"Content-Type": "application/json"},
        )
    return {"Error": "invalid credentials"}, 401, {"Content-Type": "application/json"}


@APP.route("/logout", methods=["POST"])
def logout_lzv():
    """
    Logout User from lzv System. Deletes local stored session id.
    """
    result = lzv_util.validate_user_session(request)
    if not result["success"]:
        return result["return_error"]
    lzv_util.logout_session(request.cookies["session_user"])
    return (
        json.dumps({"Message": "All good!"}),
        200,
        {"Content-Type": "application/json"},
    )



def create_storage_data_structure_from_upload(user_id, _file):
    """
    creates the storage generic:data_structure for metadata. expects a input file from upload
    metadata:
    {
        entry_id
        entry_title
        project_id
        element_id
        element_type
        element_version_id
        entry_version_id
        version_date
        project_title
    }
    """
    return {
        "package_id": str(uuid.uuid4()),
        "type": "DATA",
        "owner": user_id,
        "name": secure_filename(_file.filename),
        "data_object_metadata": {
            "content_origin": "upload",
            "export_date": time.strftime("%Y-%m-%dT%T.000+0000"),
            "export_user": user_id,
            "is_stored": False,
        },
        "origin_metadata": {
            # TODO think about metadata useful for upload data (IP? -> DSGVO?)
        },
    }


@APP.route("/data/packages", methods=["GET"])
def get_data_packages():
    """
    Routed from /data/packages
    Requests all data packages for user from database, which can then be added to a
    """
    result = lzv_util.validate_user_session(request)
    if not result["success"]:
        return result["return_error"]
    user_id = request.cookies["session_user"]
    query = {"selector": {"owner": user_id, "type": "PACKAGE"}}
    response = json.loads(lzv_util.query_db(query,\
                lzv_util.CONFIGPARAMS["couchDBStorageDatabaseName"]))
    return json.dumps(response["docs"])


@APP.route("/storage/packages", methods=["GET"])
def get_package_objects():
    """
    Routed from /storage/packages
    Requests all docs from storage with type package for user
    """
    result = lzv_util.validate_user_session(request)
    if not result["success"]:
        return result["return_error"]
    user_id = request.cookies["session_user"]
    out = get_packages(user_id, return_as_string=False)
    return json.dumps(out["docs"])


def get_packages(user_id, return_as_string=False):
    """
    Returns the package docs for @user_id either as (json)string or json-object.
    """
    query = {"selector": {"owner": user_id, "type": "PACKAGE"}}
    response = lzv_util.query_db(query, lzv_util.CONFIGPARAMS["couchDBStorageDatabaseName"])
    return response if return_as_string else json.loads(response)


@APP.route("/storage/all", methods=["GET"])
def get_storage_objects():
    """
    Routed from /storage/all
    Requests all docs from storage for user
    """
    result = lzv_util.validate_user_session(request)
    if not result["success"]:
        return result["return_error"]
    user_id = request.cookies["session_user"]
    out = get_storage_for_user(user_id, return_as_string=False)
    return json.dumps(out)


def get_storage_for_user(user_id, return_as_string=False):
    """
    Returns the package and data docs for @user_id either as (json)string or json-object.
    """
    query = {"selector": {"owner": user_id}}
    response = json.loads(lzv_util.query_db(query,\
                lzv_util.CONFIGPARAMS["couchDBStorageDatabaseName"]))[
        "docs"
    ]
    return json.dumps(response) if return_as_string else response


@APP.route("/storage/packages", methods=["PUT"])
def set_package_object():
    """
    Routed from /storage/packages
    Updates or creates a new package. Metadata is set by this function serverside to prevent mani-
    pulation.
    """
    result = lzv_util.validate_user_session(request)
    if not result["success"]:
        return result["return_error"]
    user_id = request.cookies["session_user"]
    token = lzv_util.authenticate_couchdb()
    if not token:
        return ""
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "Cookie": token,
    }
    data = json.loads(request.get_data())
    query = {"selector": {"owner": user_id, "package_id": data["package_id"]}}
    check_response = json.loads(
        lzv_util.query_db(query, lzv_util.CONFIGPARAMS["couchDBStorageDatabaseName"])
    )
    url = (
        lzv_util.CONFIGPARAMS["couchDBBaseURL"]
        + "/"
        + lzv_util.CONFIGPARAMS["couchDBStorageDatabaseName"]
        + "/"
        + data["package_id"]
    )
    # prepare date to be written to db. if it is an update we only need to change some
    if check_response["docs"]:  # only one entry with same id should exist at the same time
        headers["If-Match"] = check_response["docs"][0]["_rev"]
        data["package_object_metadata"] = check_response["docs"][0][
            "package_object_metadata"
        ]
        data["package_object_metadata"]["last_change"] = time.strftime(
            "%Y-%m-%dT%T.000+0000"
        )
    else:  # when this is a new package, some additional fields need to be changed
        data["type"] = "PACKAGE"
        data["owner"] = user_id
        now = time.strftime("%Y-%m-%dT%T.000+0000")
        data["package_object_metadata"] = {
            "creation_date": now,
            "last_change": now,
            "modifiable": True,
            "origin": "USER",
            "creator": user_id,
        }
    response = requests.put(url, headers=headers, data=json.dumps(data))
    if response:
        return (
            json.dumps({"Result": "All good"}),
            200,
            {"Content-Type": "application/json"},
        )
    return (
        json.dumps({"Result": "Error Puting file to database."}),
        500,
        {"Content-Type": "application/json"},
    )


# TODO TEST
@APP.route("/storage/packages/delete", methods=["PUT"])
def delete_package_object():
    """
    Routed from /storage/packages/delete PUT
    Delete the package provided in data from database
    """
    result = lzv_util.validate_user_session(request)
    if not result["success"]:
        return result["return_error"]
    user_id = request.cookies["session_user"]
    token = lzv_util.authenticate_couchdb()
    if not token:
        return ""
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "Cookie": token,
    }
    data = json.loads(request.get_data())
    query = {"selector": {"owner": user_id, "package_id": data["package_id"]}}
    check_response = json.loads(
        lzv_util.query_db(query, lzv_util.CONFIGPARAMS["couchDBMetaDataDatabaseName"])
    )
    if check_response["docs"]:  # found the entry to delete
        url = (
            lzv_util.CONFIGPARAMS["couchDBBaseURL"]
            + "/"
            + lzv_util.CONFIGPARAMS["couchDBMetaDataDatabaseName"]
            + "/"
            + data["package_id"]
        )
        headers["If-Match"] = check_response["docs"][0]["_rev"]
        response = requests.delete(url, headers=headers, data=data)
        if response:
            return (
                json.dumps({"Result": "All good"}),
                200,
                {"Content-Type": "application/json"},
            )
    return (
        json.dumps({"Result": "Error deleting package"}),
        500,
        {"Content-Type": "application/json"},
    )


@APP.route("/metadata/structures", methods=["GET"])
def get_metadata():
    """
    Return Metadata structure file from server, providing information about supported meta data
    """
    result = lzv_util.validate_user_session(request)
    if not result["success"]:
        return result["return_error"]
    data = ""
    with open(lzv_util.CONFIGPARAMS["METADATA_INFO_FILE"]) as f:
        data = f.read()
    return json.dumps(data)


@APP.route("/metadata/export_definitions", methods=["GET"])
def get_export_definitions():
    """
    Return Metadata exports file from server, defining exports how it will be exported
    """
    result = lzv_util.validate_user_session(request)
    if not result["success"]:
        return result["return_error"]
    data = ""
    with open(lzv_util.CONFIGPARAMS["METADATA_EXPORT_DEFINITIONS"]) as f:
        data = f.read()
    return json.dumps(data)


@APP.route("/metadata/export_mappings", methods=["GET"])
def get_export_mappings():
    """
    Return Metadata structure file from server, providing mapping between schemes and exports
    """
    result = lzv_util.validate_user_session(request)
    if not result["success"]:
        return result["return_error"]
    data = ""
    with open(lzv_util.CONFIGPARAMS["METADATA_EXPORT_MAPPINGS"]) as f:
        data = f.read()
    return json.dumps(data)


@APP.route("/metadata/user", methods=["GET"])
def get_user_stored_metadata():
    """
    Routed from /metadata/user GET
    Gets the stored metadata sets for the requesting user
    """
    result = lzv_util.validate_user_session(request)
    if not result["success"]:
        return result["return_error"]
    user_id = request.cookies["session_user"]
    query = {"selector": {"owner": user_id}}
    response = json.loads(lzv_util.query_db(query,\
                lzv_util.CONFIGPARAMS["couchDBMetaDataDatabaseName"]))
    return json.dumps(response["docs"])


# TODO TEST
@APP.route("/metadata/user/delete", methods=["PUT"])
def delete_user_metadata_set():
    """
    Routed from /metadata/user/delete PUT
    Delete the meta_set provided in data from database
    """
    result = lzv_util.validate_user_session(request)
    if not result["success"]:
        return result["return_error"]
    user_id = request.cookies["session_user"]
    token = lzv_util.authenticate_couchdb()
    if not token:
        return ""
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "Cookie": token,
    }
    data = json.loads(request.get_data())
    query = {"selector": {"owner": user_id, "set_id": data["set_id"]}}
    check_response = json.loads(
        lzv_util.query_db(query, lzv_util.CONFIGPARAMS["couchDBMetaDataDatabaseName"])
    )
    if check_response["docs"]:  # found the entry to delete
        url = (
            lzv_util.CONFIGPARAMS["couchDBBaseURL"]
            + "/"
            + lzv_util.CONFIGPARAMS["couchDBMetaDataDatabaseName"]
            + "/"
            + data["set_id"]
        )
        headers["If-Match"] = check_response["docs"][0]["_rev"]
        response = requests.delete(url, headers=headers, data=data)
        if response:
            return (
                json.dumps({"Result": "All good"}),
                200,
                {"Content-Type": "application/json"},
            )
    return (
        json.dumps({"Result": "Error Deleting metaset"}),
        500,
        {"Content-Type": "application/json"},
    )


@APP.route("/metadata/user", methods=["PUT"])
def store_user_metadata():
    """
    Routed from /metadata/user PUT
    Stores the provided metadata entry for user. if en entry with same set_id exists it will be
    """
    result = lzv_util.validate_user_session(request)
    if not result["success"]:
        return result["return_error"]
    user_id = request.cookies["session_user"]
    token = lzv_util.authenticate_couchdb()
    if not token:
        return ""
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "Cookie": token,
    }
    data = json.loads(request.get_data())
    data["owner"] = user_id
    query = {"selector": {"owner": user_id, "set_id": data["set_id"]}}
    check_response = json.loads(
        lzv_util.query_db(query, lzv_util.CONFIGPARAMS["couchDBMetaDataDatabaseName"])
    )
    url = (
        lzv_util.CONFIGPARAMS["couchDBBaseURL"]
        + "/"
        + lzv_util.CONFIGPARAMS["couchDBMetaDataDatabaseName"]
        + "/"
        + data["set_id"]
    )
    if check_response["docs"]:  # only one entry with same id should exist at the same time
        headers["If-Match"] = check_response["docs"][0]["_rev"]
    response = requests.put(url, headers=headers, data=json.dumps(data))
    if response:
        return (
            json.dumps({"Result": "All good"}),
            200,
            {"Content-Type": "application/json"},
        )
    return (
        json.dumps({"Result": "Error Storing file"}),
        500,
        {"Content-Type": "application/json"},
    )


@APP.route("/ingest/user", methods=["GET"])
def get_user_stored_ingests():
    """
    Routed from /ingest/user GET
    Gets the stored ingests for the requesting user
    """
    result = lzv_util.validate_user_session(request)
    if not result["success"]:
        return result["return_error"]
    user_id = request.cookies["session_user"]
    query = {"selector": {"owner": user_id}}
    response = json.loads(lzv_util.query_db(query,\
                lzv_util.CONFIGPARAMS["couchDBIngestsDatabaseName"]))
    return json.dumps(response["docs"])


def get_ingest_by_user_and_id_in_review_db(user_id, ingest_id):
    """
    returns the ingest for ingest_id and user_id as json object
    """
    query = {"selector": {"owner": user_id, "ingest_id": ingest_id}}
    # query = {"selector": {"owner": user_id}}
    response = json.loads(
        lzv_util.query_db(query, lzv_util.CONFIGPARAMS["couchDBIngestReviewDatabaseName"])
    )
    return response["docs"]


def get_ingest_by_user_and_id_in_ingest_db(user_id, ingest_id):
    """
    returns the ingest for ingest_id and user_id as json object
    """
    query = {"selector": {"owner": user_id, "ingest_id": ingest_id}}
    # query = {"selector": {"owner": user_id}}
    response = json.loads(lzv_util.query_db(query,\
                lzv_util.CONFIGPARAMS["couchDBIngestsDatabaseName"]))
    return response["docs"]


@APP.route("/ingest/user", methods=["PUT"])
def store_user_ingest():
    """
    Routed from /ingest/user PUT
    Stores an updated ingests for the user, version managing is done on client side
    """
    result = lzv_util.validate_user_session(request)
    if not result["success"]:
        return result["return_error"]
    user_id = request.cookies["session_user"]
    data = json.loads(request.get_data())
    data["owner"] = user_id
    return update_or_create_user_ingest(user_id, data)


def update_or_create_user_ingest(user_id, ingest):
    """
    send the ingest for user_id to database. updates existing or creates a new one if none with same
    id is found in db
    """
    query = {"selector": {"owner": user_id, "ingest_id": ingest["ingest_id"]}}
    check_response = json.loads(
        lzv_util.query_db(query, lzv_util.CONFIGPARAMS["couchDBIngestsDatabaseName"])
    )
    url = (
        lzv_util.CONFIGPARAMS["couchDBBaseURL"]
        + "/"
        + lzv_util.CONFIGPARAMS["couchDBIngestsDatabaseName"]
        + "/"
        + ingest["ingest_id"]
    )
    token = lzv_util.authenticate_couchdb()
    if not token:
        return (
            {"Result": "Error Authenticating couchDB"},
            500,
            {"Content-Type": "application/json"},
        )
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "Cookie": token,
    }
    if check_response["docs"]:  # only one entry with same id should exist at the same time
        headers["If-Match"] = check_response["docs"][0]["_rev"]
        if "_id" in ingest:
            del ingest["_id"]
        if "_rev" in ingest:
            del ingest["_rev"]
    response = requests.put(url, headers=headers, data=json.dumps(ingest))
    if response:
        return (
            {"Result": "All good"},
            200,
            {"Content-Type": "application/json"},
        )
    return (
        {"Result": "Error Storing file"},
        500,
        {"Content-Type": "application/json"},
    )


def remove_user_ingest(user_id, ingest):
    """
    send the ingest for user_id to database. updates existing or creates a new one if none with same
    id is found in db
    """
    query = {"selector": {"owner": user_id, "ingest_id": ingest["ingest_id"]}}
    check_response = json.loads(
        lzv_util.query_db(query, lzv_util.CONFIGPARAMS["couchDBIngestsDatabaseName"])
    )
    url = (
        lzv_util.CONFIGPARAMS["couchDBBaseURL"]
        + "/"
        + lzv_util.CONFIGPARAMS["couchDBIngestsDatabaseName"]
        + "/"
        + ingest["ingest_id"]
    )
    token = lzv_util.authenticate_couchdb()
    if not token:
        return (
            {"Result": "Error Authenticating couchDB"},
            500,
            {"Content-Type": "application/json"},
        )
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "Cookie": token,
    }
    if check_response["docs"]:  # only one entry with same id should exist at the same time
        headers["If-Match"] = check_response["docs"][0]["_rev"]
        response = requests.delete(url, headers=headers, data=json.dumps(ingest))
        if response:
            return (
                {"Result": "All good"},
                200,
                {"Content-Type": "application/json"},
            )
    return (
        {"Result": "Error Deleting Ingest in User Ingests DB"},
        500,
        {"Content-Type": "application/json"},
    )


def update_or_create_reviewdb_ingest(user_id, ingest):
    """
    send the ingest for user_id to database. updates existing or creates a new one if none with same
    id is found in db
    """
    query = {"selector": {"owner": user_id, "ingest_id": ingest["ingest_id"]}}
    check_response = json.loads(
        lzv_util.query_db(query, lzv_util.CONFIGPARAMS["couchDBIngestReviewDatabaseName"])
    )
    url = (
        lzv_util.CONFIGPARAMS["couchDBBaseURL"]
        + "/"
        + lzv_util.CONFIGPARAMS["couchDBIngestReviewDatabaseName"]
        + "/"
        + ingest["ingest_id"]
    )
    token = lzv_util.authenticate_couchdb()
    if not token:
        return (
            {"Result": "Error Authenticating couchDB"},
            500,
            {"Content-Type": "application/json"},
        )
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "Cookie": token,
    }
    if check_response["docs"]:  # only one entry with same id should exist at the same time
        headers["If-Match"] = check_response["docs"][0]["_rev"]
    del ingest["_id"]
    del ingest["_rev"]
    response = requests.put(url, headers=headers, data=json.dumps(ingest))
    if response:
        return (
            {"Result": "All good"},
            200,
            {"Content-Type": "application/json"},
        )
    return (
        {"Result": "Error Storing file"},
        500,
        {"Content-Type": "application/json"},
    )


@APP.route("/ingest/submit", methods=["PUT"])
def submit_user_ingest_to_review():
    """
    User Ingest provided in data is submitted to the lzv process. We need to safe the submitted
    ingest in a seperate db so it cant be deleted since we need to verify to always have access
    to the provided data. Ingests are first stored in a review database. after review
    """
    result = lzv_util.validate_user_session(request)
    if not result["success"]:
        return result["return_error"]
    token = lzv_util.authenticate_couchdb()
    if not token:
        return (
            {"Result": "Internal Server Error"},
            500,
            {"Content-Type": "application/json"},
        )
    user_id = request.cookies["session_user"]
    ingest = json.loads(request.get_data())
    ingest["owner"] = user_id
    ingest["state"] = 'REVIEW'
    ingest["ingest_metadata"]["submit_date"] = time.strftime("%Y-%m-%dT%T.000+0000")
    success = create_ingest_on_filesystem(
        user_id, ingest["ingest_id"], lzv_util.CONFIGPARAMS["LZV_REVIEW"], search_in_review_db=False
    )
    print(success)
    if not success:
        return (
            json.dumps({"Result": "Error dumping ingest on filesystem"}),
            500,
            {"Content-Type": "application/json"},
        )
    couchdb_url = (
        lzv_util.CONFIGPARAMS["couchDBBaseURL"]
        + "/"
        + lzv_util.CONFIGPARAMS["couchDBIngestReviewDatabaseName"]
        + "/"
        + ingest["ingest_id"]
    )
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "Cookie": token,
    }
    response = requests.put(couchdb_url, headers=headers, data=json.dumps(ingest))
    print(response.text)
    if response:
        return (
            json.dumps({"Result": "All good"}),
            200,
            {"Content-Type": " application/json"},
        )
    #if not successfull, review data is deleted form file system since input to review database was
    #not successfull
    review_path = lzv_util.CONFIGPARAMS["LZV_REVIEW"] + ingest["ingest_id"]
    shutil.rmtree(review_path)
    return (
        json.dumps({"Result": "Error Storing ingest"}),
        500,
        {"Content-Type": "application/json"},
        )


@APP.route("/ingest/revoke", methods=["PUT"])
def revoke_ingest():
    """
    triggered when the reviewer revokes an ingest. either ingest is revoked completely or is
    returned to sender with a note what need to be changes.
    """
    result = lzv_util.validate_user_session(request)
    if not result["success"]:
        return result["return_error"]
    if not lzv_util.check_user_permission_review(request.cookies["session_user"]):
        return ({"Error": "NOT PERMITTED"},401,{"Content-Type": "application/json"})
    # token = authenticate_couchdb()
    user_id = request.cookies["session_user"]
    ingest_id = request.args.get("ingest_id")
    ingest = get_ingest_by_user_and_id_in_review_db(user_id, ingest_id)[0]
    ingest["state"] = "REJECTED"
    ingest["ingest_metadata"]["reject_data"] = time.strftime("%Y-%m-%dT%T.000+0000")
    resp = update_or_create_reviewdb_ingest(user_id, ingest)
    if resp:
        return (
            json.dumps({"Result": "All good"}),
            200,
            {"Content-Type": " application/json"},
        )
    return (
        json.dumps({"Result": "Error Storing ingest"}),
        500,
        {"Content-Type": "application/json"},
        )


@APP.route("/ingest/approve", methods=["PUT"])
def approve_ingest():
    """
    called when the reviewer approves the ingest. the process of deploying the ingest to rosetta is
    then started.
    """
    result = lzv_util.validate_user_session(request)
    if not result["success"]:
        return result["return_error"]
    if not lzv_util.check_user_permission_review(request.cookies["session_user"]):
        return (
            {"Error": "NOT AUTHORIZED FOR REVIEW"},
            401,
            {"Content-Type": "application/json"},
        )
    user_id = request.cookies["session_user"]
    ingest_id = request.args.get("ingest_id")
    success = create_ingest_on_filesystem(
        user_id, ingest_id, lzv_util.CONFIGPARAMS["LZV_HOTFOLDER"]
    )
    if success:
        ingest = get_ingest_by_user_and_id_in_review_db(user_id, ingest_id)[0]
        ingest["state"] = "APPROVED"
        ingest["ingest_metadata"]["approve_date"] = time.strftime(
            "%Y-%m-%dT%T.000+0000"
        )
        # TODO check here what happens if ingest cant be stored in database. eventually the data will
        # be corrupted. this needs to be checked what the behaviour should be.
        resp = update_or_create_reviewdb_ingest(user_id, ingest)
        if resp:
            # remove the review files from file system
            review_path = lzv_util.CONFIGPARAMS["LZV_REVIEW"] + ingest["ingest_id"]
            shutil.rmtree(review_path)
            return remove_user_ingest(user_id, ingest)
    return (
        json.dumps({"Result": "Error Approving and Moving Ingest"}),
        500,
        {"Content-Type": "application/json"},
    )
    # ingest is set to approved by this method if the write on hot_folder is successfull. if this is
    # not the case, it need to be redone.
    # store the modified ingst in database.


def create_ingest_on_filesystem(user_id, ingest_id, base_folder, search_in_review_db=True):
    """
    create the files for the ingest on the defined folder. folder should be hotfolder to rosetta
    system. also created the mets files basedo n the data provided in the ingest.
    """
    ingest = {}
    if search_in_review_db:
        ingest = get_ingest_by_user_and_id_in_review_db(user_id, ingest_id)
    else:
        ingest = get_ingest_by_user_and_id_in_ingest_db(user_id, ingest_id)
    if not ingest:
        return False
    ingest = ingest[0]
    storage_file = get_storage_for_user(user_id)
    path = base_folder
    if not Path(path).is_dir():
        return False
    path += ingest["ingest_id"] + "/content/"

    mets_xml = mets.generate_mets_xml(ingest, storage_file)
    ingest_hotfolder_path = Path(path)
    ingest_hotfolder_path.mkdir(mode=0o777, parents=True, exist_ok=True)
    try:
        mets_file = Path(path + "ie1.xml")
        mets_file.touch(mode=0o770, exist_ok=True)
        mets_file.write_text(mets_xml)
    except:
        return False

    flat_data = mets.get_ingest_data_files(ingest)
    success = True
    path += "streams/"
    ingest_hotfolder_path = Path(path)
    ingest_hotfolder_path.mkdir(mode=0o777, parents=True, exist_ok=True)
    for item in flat_data:
        for f in item["flat_data"]:
            cdb_doc_url = (
                lzv_util.CONFIGPARAMS["couchDBBaseURL"]
                + "/"
                + lzv_util.CONFIGPARAMS["couchDBDocumentDatabaseName"]
                + "/"
                + f["data_object_metadata"]["doc_id"]
                + "/"
                + f["data_object_metadata"]["doc_id"]
            )
            token = lzv_util.authenticate_couchdb()
            if not token:
                return False
            headers = {
                "Accept": "application/json",
                "Content-Type": "application/json",
                "Cookie": token,
            }
            response = requests.get(cdb_doc_url, headers=headers)
            print(response.text)
            if response:
                try:
                    tmp_path = path + f["data_object_metadata"]["filename"]
                    test = f["data_object_metadata"]["filename"]
                    tmp_json_path = (
                        path + f["data_object_metadata"]["filename"] + ".json"
                    )
                    tmp_file = Path(tmp_path)
                    tmp_json_file = Path(tmp_json_path)
                    tmp_file.touch(mode=0o770, exist_ok=True)
                    tmp_json_file.touch(mode=0o770, exist_ok=True)
                    tmp_file.write_bytes(response.content)
                    tmp = [item for item in storage_file \
                            if f["package_id"] == item["package_id"]][0]
                    tmp_json_file.write_text(
                        json.dumps([item for item in storage_file \
                            if f["package_id"] == item["package_id"]][0])
                    )
                except:
                    success = False
            else:
                print("3")
                success = False
    if not success:  # remove all files eventually created bythe method
        shutil.rmtree(ingest_hotfolder_path)
    return success


# TODO function which checks state of ingest after




@APP.route("/ingest/toreview", methods=["GET"])
def get_toreview_ingests():
    """
    get Ingests which need to be reviewed. Review permission is checked before returning
     information. if no permission is available for review 401 is returned.
    """
    result = lzv_util.validate_user_session(request)
    if not result["success"]:
        return result["return_error"]
    if not lzv_util.check_user_permission_review(request.cookies["session_user"]):
        sys.stderr.write("get_toreview_ingests: Error user not authorized for review.\n")
        return (
            {"Error": "NOT AUTHORIZED FOR REVIEW"},
            401,
            {"Content-Type": "application/json"},
        )
    query = {"selector": {"state": "REVIEW"}}
    response = lzv_util.query_db(query, lzv_util.CONFIGPARAMS["couchDBIngestReviewDatabaseName"])
    return response


@APP.route("/ingest/submitted", methods=["GET"])
def get_submitted_ingests():
    """
    Get the submitted ingests for user from database
    """
    result = lzv_util.validate_user_session(request)
    if not result["success"]:
        return result["return_error"]
    query = {"selector": {"owner": request.cookies["session_user"]}}
    response = lzv_util.query_db(query, lzv_util.CONFIGPARAMS["couchDBIngestReviewDatabaseName"])
    if response:
        return response
    sys.stderr.write("get_submitted_ingests: Error requesting submitted ingests\n")
    return (
        json.dumps({"Result": "Error requesting submitted ingests"}),
        500,
        {"Content-Type": "application/json"},
    )


@APP.route("/upload/file", methods=["POST"])
def receive_file():
    """
    Receive files belonging to a package. This is definied by package_id in parameteres. It
    needs to check if the package is manually created AND belonging to the right user.
    """
    result = lzv_util.validate_user_session(request)
    if not result["success"]:
        return result["return_error"]
    package_id = request.args.get("package_id")
    user_id = request.cookies["session_user"]
    query = {"selector": {"package_id": package_id, "owner": user_id}}
    check_response = json.loads(
        lzv_util.query_db(query, lzv_util.CONFIGPARAMS["couchDBStorageDatabaseName"])
    )["docs"]
    if not check_response:
        sys.stderr.write("receive_file: Error: Invalid Package ID oder Package does not belong\
                         to user\n")
        return (
            json.dumps(
                {
                    "Result": "Error: Invalid Package ID oder Package does not belong\
                         to user"
                }
            ),
            500,
            {"Content-Type": "application/json"},
        )
    # check if the post request has the file part
    if "uploaded_file" not in request.files:
        sys.stderr.write("receive_file: Error No files provided.\n")
        return (
            json.dumps({"Result": "Error: No files provided"}),
            500,
            {"Content-Type": "application/json"},
        )
    files = request.files.getlist("uploaded_file")
    # if user does not select file, browser also
    # submit an empty part without filename
    storage_metadata = []
    for f in files:
        if f.filename == "":
            continue
        if f:
            # filename = file.filename
            # file.save(os.path.join(APP.config['UPLOAD_FOLDER'], filename))
            # print("Succesfully saved files")
            metadata_obj = create_storage_data_structure_from_upload(user_id, f)
            response = upload_file_to_couchdb_document_db(f, metadata_obj)
            if response:
                storage_metadata.append(metadata_obj)
    if storage_metadata:
        lzv_util.add_to_storage(storage_metadata)
        package_response = append_children_to_package(
            user_id, package_id, storage_metadata
        )
        if package_response:  # should be true, else there is a inconsistency in db.
            return (
                json.dumps({"Result": "Succesfully saved files"}),
                200,
                {"Content-Type": "application/json"},
            )
        sys.stderr.write("receive_file: Error: Saving Package File.\n")
        return (
            json.dumps({"Result": "Error: Saving Package File"}),
            500,
            {"Content-Type": "application/json"},
        )
    sys.stderr.write("receive_file: Error: No files provided.\n")
    return (
        json.dumps({"Result": "Error: No files provided"}),
        500,
        {"Content-Type": "application/json"},
    )


def append_children_to_package(user_id, package_id, append_children):
    """
    adds the uploaded files to the package which has previously created by the user. Also
    uploads the modifies package to the database.
    """
    token = lzv_util.authenticate_couchdb()
    if not token:
        sys.stderr.write("append_children_to_package: Error Authenticating couch DB.\n")
        return (
            json.dumps({"Result": "Error Authenticating couch DB"}),
            500,
            {"Content-Type": "application/json"},
        )
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "Cookie": token,
    }
    query = {"selector": {"owner": user_id, "package_id": package_id}}
    check_response = json.loads(
        lzv_util.query_db(query, lzv_util.CONFIGPARAMS["couchDBStorageDatabaseName"])
    )
    url = (
        lzv_util.CONFIGPARAMS["couchDBBaseURL"]
        + "/"
        + lzv_util.CONFIGPARAMS["couchDBStorageDatabaseName"]
        + "/"
        + package_id
    )
    # prepare date to be written to db. if it is an update we only need to change some
    if check_response["docs"]:  # only one entry with same id should exist at the same time
        data = check_response["docs"][0]
        headers["If-Match"] = check_response["docs"][0]["_rev"]
        data["package_object_metadata"]["last_change"] = time.strftime(
            "%Y-%m-%dT%T.000+0000"
        )
        if not hasattr(data, "child_data_objects"):
            data["child_data_objects"] = []
        for item in append_children:
            data["child_data_objects"].append(item["package_id"])
    else:  # when this is a new package, some additional fields need to be changed
        sys.stderr.write("append_children_to_package: Error adding children to package. \
            No Package found  with package_id.\n")
        return (
            json.dumps(
                {
                    "Result": "Error adding children to package. No Package found  with\
                            package_id"
                }
            ),
            500,
            {"Content-Type": "application/json"},
        )
    response = requests.put(url, headers=headers, data=json.dumps(data))
    if response:
        return (
            json.dumps({"Result": "All good"}),
            200,
            {"Content-Type": "application/json"},
        )
    sys.stderr.write("append_children_to_package: Error updating file to database.\n")
    return (
        json.dumps({"Result": "Error updating file to database."}),
        500,
        {"Content-Type": "application/json"},
    )


def upload_file_to_couchdb_document_db(f, metadata_obj):
    """
    Uploads a file to the document db. Also updated the metadata_obj with the doc_id, file_type,
    filename and is_stored flag
    """
    token = lzv_util.authenticate_couchdb()
    if not token:
        return (
            json.dumps({"Result": "Error Authenticating couch DB"}),
            500,
            {"Content-Type": "application/json"},
        )
    couch_header = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "Cookie": token,
    }
    couchdb_url = (
        lzv_util.CONFIGPARAMS["couchDBBaseURL"]
        + "/"
        + lzv_util.CONFIGPARAMS["couchDBDocumentDatabaseName"]
    )
    json_answer = json.loads(
        requests.post(couchdb_url, headers=couch_header, data=json.dumps({})).text
    )
    couch_header["If-Match"] = json_answer["rev"]
    couchdb_url = couchdb_url + "/" + json_answer["id"] + "/"
    filename = secure_filename(f.filename)
    couch_header["Content-Type"] = f.mimetype
    file_data = f.read()
    couchdb_url = couchdb_url + json_answer["id"]
    att_create_response = requests.put(
        couchdb_url, headers=couch_header, data=file_data
    )
    if att_create_response:
        metadata_obj["data_object_metadata"]["file_type"] = f.mimetype
        metadata_obj["data_object_metadata"]["is_stored"] = bool(att_create_response)
        metadata_obj["data_object_metadata"]["filename"] = filename
        metadata_obj["data_object_metadata"]["doc_id"] = json_answer["id"]
    else:
        sys.stderr.write("upload_file_to_couchdb_document_db: Error Uploading File to Database.\n")
        return (
            json.dumps({"Result": "Error Uploading File to Database."}),
            500,
            {"Content-Type": "application/json"},
        )
    return (
        json.dumps({"Result": "Successfully uploaded file to doc DB."}),
        200,
        {"Content-Type": "application/json"},
    )


@APP.route("/upload/package", methods=["GET"])
def receive_package():
    """
        Receive a package from Client. Packge id is created on server and returned to sender. He \
        then can send fiels to this package with the package_id. The metadata for package creation
        is only the name of package, everything else is set serverside
    """
    result = lzv_util.validate_user_session(request)
    if not result["success"]:
        return result["return_error"]
    user_id = request.cookies["session_user"]
    data = {}
    data["package_id"] = str(uuid.uuid4())
    data["name"] = request.args.get("name")
    token = lzv_util.authenticate_couchdb()
    if not token:
        return ""
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "Cookie": token,
    }
    url = (
        lzv_util.CONFIGPARAMS["couchDBBaseURL"]
        + "/"
        + lzv_util.CONFIGPARAMS["couchDBStorageDatabaseName"]
        + "/"
        + data["package_id"]
    )
    data["type"] = "PACKAGE"
    data["owner"] = user_id
    now = time.strftime("%Y-%m-%dT%T.000+0000")
    data["package_object_metadata"] = {
        "creation_date": now,
        "last_change": now,
        "modifiable": False,
        "origin": "UPLOAD",
        "creator": user_id,
    }
    response = requests.put(url, headers=headers, data=json.dumps(data))
    if response:
        return (
            json.dumps(
                {"Result": "Succesfully saved files", "package_id": data["package_id"]}
            ),
            200,
            {"Content-Type": "application/json"},
        )
    sys.stderr.write("receive_package: Error saving new package file.\n")
    return (
        json.dumps(
            {
                "Result": "Error saving new package file",
                "package_id": data["package_id"],
            }
        ),
        500,
        {"Content-Type": "application/json"},
    )


if __name__ == "__main__":
    # print(get_storage_for_user("bt303343", return_as_string=True))
    # authenticate_couchdb()
    APP.run(debug=True)

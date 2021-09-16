"""
Software for LZV Server.
"""
import time
from pathlib import Path
from zipfile import ZipFile
import shutil
import os
import uuid
import json
import secrets
import requests
import mets

# from flask import Flask, session
from flask import Flask, request, render_template, send_from_directory, session
from flask_session import Session
from flask_cors import CORS
from werkzeug.utils import secure_filename

import ldap

# from flask import send_from_directory
# from flask import render_template
# from flask import Response
# from flask import make_response
# from flask import send_file
# from flask import *
# from zipfile import *

DEBUG = 1

# ----------------------global Parameters-------------------------------------------

CONFIGPARAMS = {}
FAILED_AUTHENTICATION = "Failed Authentication, please login to use this service!"


# ----------------------initialization------------------------------------------

APP = Flask(__name__)
with open("/server/lzv/server/conf/config.json") as f:
    CONFIGPARAMS = json.load(f)
APP.secret_key = "any random string"
APP.config["SESSION_TYPE"] = "filesystem"
APP.config["PERMANENT_SESSION_LIFETIME"] = 43200
APP.config["SESSION_PERMANENT"] = False
APP.config["UPLOAD_FOLDER"] = CONFIGPARAMS["USR_UPLOAD_TMP_FOLDER"]
CORS(APP)
Session(APP)


# ----------------------Page Navigation-----------------------------------------
@APP.route("/")
def navhome():
    """
    Navigation to site Home
    """
    if not "session_user" in request.cookies or not "session_auth" in request.cookies:
        return render_template("login.html")
    if not check_session(
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
    if not check_session(
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
    if not check_session(
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
    if not check_session(
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
    if not check_session(
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
    if not check_session(
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
    if not check_session(
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
    if not check_session(
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
    if not check_session(
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
    if not check_session(
        request.cookies["session_user"], request.cookies["session_auth"]
    ):
        return render_template("login.html")
    if not check_user_permission_review(request.cookies["session_user"]):
        return render_template("index.html")
    return render_template("lzvreview.html")


@APP.route("/login", methods=["GET"])
def navlogin():
    """
    Navigation to login site
    """
    return render_template("login.html")


# ----------------------Authenticate LDAP --------------------------------------
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


@APP.route("/login", methods=["POST"])
def login_lzv():
    """
    Login to lzv site. Performs a lookup to ldap server to verify credentials.
    Returns a session token to user, to authenticate your session against.
    """
    if "session_user" in request.cookies and "session_auth" in request.cookies:
        if check_session(
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
    if authenticate_ldap(data["username"], data["password"]):
        create_user_session(data["username"])
        return (
            json.dumps(
                {
                    "session_id": get_sessionid(data["username"]),
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
    if not "session_user" in request.cookies or not "session_auth" in request.cookies:
        return (
            {"Error": FAILED_AUTHENTICATION},
            401,
            {"Content-Type": "application/json"},
        )
    if not check_session(
        request.cookies["session_user"], request.cookies["session_auth"]
    ):
        return (
            {"Error": FAILED_AUTHENTICATION},
            401,
            {"Content-Type": "application/json"},
        )
    logout_session(request.cookies["session_user"])
    return (
        json.dumps({"Message": "All good!"}),
        200,
        {"Content-Type": "application/json"},
    )


# ----------------------Authentification LabFolder------------------------------
@APP.route("/labfolder/auth/login", methods=["POST"])
def authenticate_labfolder():
    """
    Authenticate to LabFolder and returns the login answer
    """
    if not "session_user" in request.cookies or not "session_auth" in request.cookies:
        return (
            {"Error": FAILED_AUTHENTICATION},
            401,
            {"Content-Type": "application/json"},
        )
    if not check_session(
        request.cookies["session_user"], request.cookies["session_auth"]
    ):
        return (
            {"Error": FAILED_AUTHENTICATION},
            401,
            {"Content-Type": "application/json"},
        )
    url = CONFIGPARAMS["labFolderBaseURL"] + "/auth/login"
    data = request.get_data()
    headers = {"Content-Type": "application/json"}
    response = requests.post(url, data=data, headers=headers)
    return response.text


@APP.route("/labfolder/auth/logout", methods=["POST"])
def logout_labfolder():
    """
    Kills the Session associated to the provided token
    """
    if not "session_user" in request.cookies or not "session_auth" in request.cookies:
        return (
            {"Error": FAILED_AUTHENTICATION},
            401,
            {"Content-Type": "application/json"},
        )
    if not check_session(
        request.cookies["session_user"], request.cookies["session_auth"]
    ):
        return (
            {"Error": FAILED_AUTHENTICATION},
            401,
            {"Content-Type": "application/json"},
        )
    url = CONFIGPARAMS["labFolderBaseURL"] + "/auth/logout"
    headers = {
        "Content-Type": "application/json",
        "Authorization": "Token " + request.headers["Token"],
        "User-Agent": CONFIGPARAMS["labFolderDefaultUserAgentHeader"],
    }

    response = requests.post(url, headers=headers)
    return response.text


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
    # data =  {"name":  CONFIGPARAMS["couchDBAdmin"], "password": CONFIGPARAMS["couchDBPassword"]}
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    response = requests.post(url, data=data, headers=headers)
    if response.status_code == 200:
        cookie = response.headers["Set-Cookie"]
        couchdb_token = cookie[: cookie.find(";")]
        return couchdb_token
    if DEBUG:
        print("Error logging into couchDB. Wrong Username or Password!")
        print(response.text)
    return False


# ----------------------Projects------------------------------------------------


@APP.route("/labfolder/projects", methods=["GET"])
def get_projects():
    """
    Accesses LabFolder by Token and retreives the Projects from User. Answer is returned by REST.
    """
    if not "session_user" in request.cookies or not "session_auth" in request.cookies:
        return (
            {"Error": FAILED_AUTHENTICATION},
            401,
            {"Content-Type": "application/json"},
        )
    if not check_session(
        request.cookies["session_user"], request.cookies["session_auth"]
    ):
        return (
            {"Error": FAILED_AUTHENTICATION},
            401,
            {"Content-Type": "application/json"},
        )
    url = CONFIGPARAMS["labFolderBaseURL"] + "/projects"
    headers = {
        "Content-Type": "application/json",
        "Authorization": "Token " + request.headers["Token"],
        "User-Agent": CONFIGPARAMS["labFolderDefaultUserAgentHeader"],
    }
    response = requests.get(url, headers=headers)
    return response.text


# -------------------Notebook---------------------------------------------------


@APP.route("/labfolder/entries", methods=["GET"])
def get_notebook_entries():
    """
    Accesses LabFolder by Token and retreives the Entries from User. Answer is returned by REST.
    """
    if not "session_user" in request.cookies or not "session_auth" in request.cookies:
        return (
            {"Error": FAILED_AUTHENTICATION},
            401,
            {"Content-Type": "application/json"},
        )
    if not check_session(
        request.cookies["session_user"], request.cookies["session_auth"]
    ):
        return (
            {"Error": FAILED_AUTHENTICATION},
            401,
            {"Content-Type": "application/json"},
        )
    url = CONFIGPARAMS["labFolderBaseURL"] + "/entries"
    headers = {
        "Content-Type": "application/json",
        "Authorization": "Token " + request.headers["Token"],
        "User-Agent": CONFIGPARAMS["labFolderDefaultUserAgentHeader"],
    }
    response = requests.get(url, headers=headers)
    return response.text


@APP.route("/labfolder/download", methods=["GET"])
def download_file_to_client():
    """
    Creates a zip File with the Entry requested by the user, and transfers the zip by HTTP.
    Receives only a list of ids of dataobjects. querys these from database
    """
    if not "session_user" in request.cookies or not "session_auth" in request.cookies:
        return (
            {"Error": FAILED_AUTHENTICATION},
            401,
            {"Content-Type": "application/json"},
        )
    if not check_session(
        request.cookies["session_user"], request.cookies["session_auth"]
    ):
        return (
            {"Error": FAILED_AUTHENTICATION},
            401,
            {"Content-Type": "application/json"},
        )
    project_id = request.args.get("project_id")
    entry_id = request.args.get("entry_id")
    entry_version_id = request.args.get("entry_version_id")

    query = {
        "selector": {
            "owner": request.cookies["session_user"],
            "data_object_metadata": {"content_origin": "labfolder"},
            "origin_metadata": {
                "project_id": project_id,
                "entry_id": entry_id,
                "entry_version_id": entry_version_id,
            },
        }
    }
    download_meta = json.loads(
        query_db(query, CONFIGPARAMS["couchDBStorageDatabaseName"])
    )["docs"]
    filename = (
        request.cookies["session_user"]
        + "-"
        + time.strftime("%d-%m-%Y")
        + "-"
        + time.strftime("%H:%M:%S")
        + ".zip"
    )
    if len(download_meta) > 0:
        create_zip_from_files(download_meta, CONFIGPARAMS["tempFolder"] + filename)
    else:
        return APP.response_class(
            json.dumps({"Error": "Missing Parameter id"}),
            status=200,
            mimetype="application/json",
        )
    return send_from_directory(CONFIGPARAMS["tempFolder"], filename, as_attachment=True)


@APP.route("/labfolder/elements/download", methods=["POST"])
def download():
    """
    Download data provided in request from labfolder. Checks if duplicates already are in db.
    Only downloads new files from labfolder. Adds documents to doc db and metadata files to
    storage db. also creates package files for entrys for all elements containing the elements.
    """
    if not "session_user" in request.cookies or not "session_auth" in request.cookies:
        return (
            {"Error": FAILED_AUTHENTICATION},
            401,
            {"Content-Type": "application/json"},
        )
    if not check_session(
        request.cookies["session_user"], request.cookies["session_auth"]
    ):
        return (
            {"Error": FAILED_AUTHENTICATION},
            401,
            {"Content-Type": "application/json"},
        )
    user_id = request.cookies["session_user"]
    data = request.get_data()
    json_data = json.loads(data)
    json_data = remove_already_existing_tupel(user_id, json_data)
    storage_metadata = []
    for item in json_data:
        storage_metadata.append(
            create_storage_data_structure_from_labfolder(user_id, item)
        )
    if len(storage_metadata) > 0:
        print("storage_metadata")
        print(storage_metadata)
        download_files_from_labfolder(storage_metadata)
        package_objects = create_package_for_downloaded_labfolder_data(
            user_id, storage_metadata
        )
        storage_metadata += package_objects
        add_to_storage(storage_metadata)
    return APP.response_class(status=200, mimetype="application/json")


def create_package_for_downloaded_labfolder_data(user_id, downloaded_sets):
    """
    finds all unique origin_metadata.entry_id in downloaded_sets. for each entry it creates one
    package generic_datastructure which contains all elements of that entry that were downlaoded
    """
    # first get the uniques entry_ids
    tmp_dict = {}
    for obj in downloaded_sets:
        tmp_dict[obj["origin_metadata"]["entry_id"]] = obj
    search_entry_ids = list(tmp_dict.keys())
    # iterate through entry_ids and create package objects
    append = []
    for search_entry_id in search_entry_ids:
        append.append(
            {
                "package_id": str(uuid.uuid4()),
                "type": "PACKAGE",
                "owner": user_id,
                "name": [
                    x["name"]
                    for x in downloaded_sets
                    if x["origin_metadata"]["entry_id"] == search_entry_id
                ][0],
                "package_object_metadata": {
                    "creation_date": time.strftime("%Y-%m-%dT%T.000+0000"),
                    "last_change": time.strftime("%Y-%m-%dT%T.000+0000"),
                    "creator": user_id,
                    "modifiable": False,
                },
                "child_data_objects": [
                    x["package_id"]
                    for x in downloaded_sets
                    if x["origin_metadata"]["entry_id"] == search_entry_id
                ],
            }
        )
    return append


def create_storage_data_structure_from_labfolder(user_id, input_set):
    """
    creates the storage generic:data_structure for metadata. expects a input set from labfolder
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
        "name": input_set["entry_title"],
        "data_object_metadata": {
            "content_origin": "labfolder",
            "export_date": time.strftime("%Y-%m-%dT%T.000+0000"),
            "export_user": user_id,
            "is_stored": False,
        },
        "origin_metadata": {
            "project_id": input_set["project_id"],
            "project_title": input_set["project_title"],
            "entry_id": input_set["entry_id"],
            "entry_title": input_set["entry_title"],
            "entry_version_id": input_set["entry_version_id"],
            "entry_version_date": input_set["entry_version_date"],
            "entry_hidden": input_set["entry_hidden"],
            "element_id": input_set["element_id"],
            "element_type": input_set["element_type"],
            "element_version_id": input_set["element_version_id"],
        },
    }


def create_storage_data_structure_from_upload(user_id, file):
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
        "name": secure_filename(file.filename),
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


# @APP.route('/elements/file' , methods=['GET'])
def download_files_from_labfolder(data_array):
    """
    Function is called for File Download from LabFolder. This Function downloads the files and
    stored it in the database.
    """
    token = authenticate_couchdb()
    if not token:
        return
    for element in data_array:
        if element["origin_metadata"]["element_type"] == "IMAGE":
            file_info_url = (
                CONFIGPARAMS["labFolderBaseURL"]
                + "/elements/file/"
                + element["origin_metadata"]["element_id"]
            )
            file_url = file_info_url + "/download"
        elif element["origin_metadata"]["element_type"] == "TABLE":
            file_url = (
                CONFIGPARAMS["labFolderBaseURL"]
                + "/elements/table/"
                + element["origin_metadata"]["element_id"]
            )
        elif element["origin_metadata"]["element_type"] == "TEXT":
            file_url = (
                CONFIGPARAMS["labFolderBaseURL"]
                + "/elements/text/"
                + element["origin_metadata"]["element_id"]
            )
        else:
            continue
        headers = {
            "Content-Type": "application/json",
            "Authorization": "Token " + request.headers["Token"],
            "User-Agent": CONFIGPARAMS["labFolderDefaultUserAgentHeader"],
        }
        couch_header = {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "Cookie": token,
        }
        print(file_url)
        print(json.dumps(headers))
        file_response = requests.get(file_url, headers=headers)
        print("file_response")
        print(file_response.text)
        couchdb_url = (
            CONFIGPARAMS["couchDBBaseURL"]
            + "/"
            + CONFIGPARAMS["couchDBDocumentDatabaseName"]
        )
        json_answer = json.loads(
            requests.post(couchdb_url, headers=couch_header, data=json.dumps({})).text
        )
        couch_header["If-Match"] = json_answer["rev"]
        element["data_object_metadata"]["doc_id"] = json_answer["id"]
        couchdb_url = couchdb_url + "/" + json_answer["id"] + "/"
        file_name = ""
        file_suffix = ""
        if element["origin_metadata"]["element_type"] == "IMAGE":
            print("file infor url")
            print(file_info_url)
            print(headers)
            file_info_reponse_jdata = json.loads(
                requests.get(file_info_url, headers=headers).text
            )
            print(json.dumps(file_info_reponse_jdata))
            file_name = file_info_reponse_jdata["file_name"]
            file_data = file_response.content
            couchdb_url = couchdb_url + json_answer["id"]
            couch_header["Content-Type"] = "image/png"
            file_suffix = ".png"
            att_create_response = requests.put(
                couchdb_url, headers=couch_header, data=file_data
            )
            element["data_object_metadata"]["is_stored"] = bool(att_create_response)
        elif (
            element["origin_metadata"]["element_type"] == "TABLE"
            or element["origin_metadata"]["element_type"] == "TEXT"
        ):
            file_data = ""
            file_info_reponse_jdata = json.loads(file_response.text)
            if element["origin_metadata"]["element_type"] == "TABLE":
                file_name = file_info_reponse_jdata["title"]
                sheets = file_info_reponse_jdata["content"]["sheets"]
                file_data = process_table_data(sheets)
                couch_header["Content-Type"] = "text/csv"
                file_suffix = ".csv"
            else:  # text TODO rework this to support richtext or html
                file_data = file_info_reponse_jdata["content"]
                file_name = json_answer["id"]
                couch_header["Content-Type"] = "text/plain"
                file_suffix = ".txt"
            couchdb_url = couchdb_url + json_answer["id"]
            att_create_response = requests.put(
                couchdb_url, headers=couch_header, data=file_data
            )
            element["data_object_metadata"]["is_stored"] = bool(att_create_response)

        element["data_object_metadata"]["filename"] = file_name + file_suffix
        element["data_object_metadata"]["db_filename"] = json_answer["id"]
        element["data_object_metadata"]["file_type"] = couch_header["Content-Type"]


def process_table_data(sheets):
    """
    Processes data from sheets to a flat csv string
    """
    file_data = ""
    for sheet_key in sheets:
        try:
            data = sheets[sheet_key]["data"]["dataTable"]
        except (AttributeError, KeyError):
            continue
        # if not sheets[sheet_key]["data"]["dataTable"]:
        #     continue
        # data = sheets[sheet_key]["data"]["dataTable"]
        file_data = file_data + sheets[sheet_key]["name"] + "\n"
        for line in data:
            for row in data[line]:
                if isinstance(data[line][row]["value"], int):
                    file_data = file_data + str(data[line][row]["value"]) + ","
                else:
                    file_data = file_data + str(data[line][row]["value"]) + ","
            file_data = file_data.rstrip(",")
            file_data = file_data + "\n"
    return file_data


@APP.route("/labfolder/mdb/categories", methods=["GET"])
def get_mdb_categories():
    """
    Routed from /mdb/categories.
    Retreives the category information about Material Databse from labfolder and returns this.
    """
    if not "session_user" in request.cookies or not "session_auth" in request.cookies:
        return (
            {"Error": FAILED_AUTHENTICATION},
            401,
            {"Content-Type": "application/json"},
        )
    if not check_session(
        request.cookies["session_user"], request.cookies["session_auth"]
    ):
        return (
            {"Error": FAILED_AUTHENTICATION},
            401,
            {"Content-Type": "application/json"},
        )
    url = CONFIGPARAMS["labFolderBaseURL"] + "/mdb/categories"
    # prepare header
    headers = {
        "Content-Type": "application/json",
        "Authorization": "Token " + request.headers["Token"],
        "User-Agent": CONFIGPARAMS["labFolderDefaultUserAgentHeader"],
    }
    if DEBUG:
        print(url)
    response = requests.get(url, headers=headers)
    return response.text


# ----does only support filtering by category_id----
@APP.route("/labfolder/mdb/items", methods=["GET"])
def download_mdb_items():
    """
    routed from /mdb/items
    Download the Material Database Items to Server.
    """
    if not "session_user" in request.cookies or not "session_auth" in request.cookies:
        return (
            {"Error": FAILED_AUTHENTICATION},
            401,
            {"Content-Type": "application/json"},
        )
    if not check_session(
        request.cookies["session_user"], request.cookies["session_auth"]
    ):
        return (
            {"Error": FAILED_AUTHENTICATION},
            401,
            {"Content-Type": "application/json"},
        )
    url_items = CONFIGPARAMS["labFolderBaseURL"] + "/mdb/items"
    url_categories = CONFIGPARAMS["labFolderBaseURL"] + "/mdb/categories"
    category_id = request.args.get("category_id", default="", type=str)
    token = request.args.get("token", default="", type=str)
    if category_id == "":
        return APP.response_class(
            json.dumps({"Error": "Missing Parameter id"}),
            status=400,
            mimetype="application/json",
        )
    if token == "":
        return APP.response_class(
            json.dumps({"Error": "Missing Labfolder Token"}),
            status=400,
            mimetype="application/json",
        )
    url_items = url_items + "?category_id=" + category_id
    url_categories = url_categories + "/" + category_id
    # prepare header
    headers = {
        "Content-Type": "application/json",
        "Authorization": "Token " + token,
        "User-Agent": CONFIGPARAMS["labFolderDefaultUserAgentHeader"],
    }
    # now we preprocess the answer to a csv
    category_response_jdata = json.loads(
        requests.get(url_categories, headers=headers).text
    )
    item_response_jdata = json.loads(requests.get(url_items, headers=headers).text)
    attributes_sorted = category_response_jdata["attributes"]
    file_data = "Name, "
    for att in attributes_sorted:
        file_data = file_data + att["title"] + ","
    file_data.rstrip(",")
    file_data = file_data + "\n"
    for item in item_response_jdata:
        file_data = file_data + item["title"] + ","
        for satt in attributes_sorted:
            # write the content of the sorted attribute field. identified by the id of the attribute
            file_data = file_data + item["custom_attributes"][satt["id"]] + ","
        file_data.rstrip(",")
        file_data = file_data + "\n"
    filename = category_response_jdata["title"] + ".csv"
    filename = filename.replace(">", "_")
    filename = filename.replace(" ", "")
    file = open(CONFIGPARAMS["tempFolder"] + filename, "w")
    file.write(file_data)
    file.close()
    return send_from_directory(CONFIGPARAMS["tempFolder"], filename, as_attachment=True)
    # return json.dumps({'Result' : 'All good'}), 200, {'Content-Type' : 'application/json'}


@APP.route("/data/packages", methods=["GET"])
def get_data_packages():
    """
    Routed from /data/packages
    Requests all data packages for user from database, which can then be added to a
    """
    if not "session_user" in request.cookies or not "session_auth" in request.cookies:
        return (
            {"Error": FAILED_AUTHENTICATION},
            401,
            {"Content-Type": "application/json"},
        )
    if not check_session(
        request.cookies["session_user"], request.cookies["session_auth"]
    ):
        return (
            {"Error": FAILED_AUTHENTICATION},
            401,
            {"Content-Type": "application/json"},
        )
    user_id = request.cookies["session_user"]
    query = {"selector": {"owner": user_id, "type": "PACKAGE"}}
    response = json.loads(query_db(query, CONFIGPARAMS["couchDBStorageDatabaseName"]))
    return json.dumps(response["docs"])


@APP.route("/labfolder/storage", methods=["GET"])
def get_labfolder_storage_data():
    """
    Routed from /labfolder/storage
    Requests the storage file, containg metadata about stored files for the requesting user
    """
    if not "session_user" in request.cookies or not "session_auth" in request.cookies:
        return (
            {"Error": FAILED_AUTHENTICATION},
            401,
            {"Content-Type": "application/json"},
        )
    if not check_session(
        request.cookies["session_user"], request.cookies["session_auth"]
    ):
        return (
            {"Error": FAILED_AUTHENTICATION},
            401,
            {"Content-Type": "application/json"},
        )
    user_id = request.cookies["session_user"]
    out = get_labfolder_data(user_id, return_as_string=False)
    return json.dumps(out["docs"])


def get_labfolder_data(user_id, return_as_string=False):
    """
    Returns the labfolder data for @user_id either as (json)string or object.
    """
    query = {
        "selector": {
            "owner": user_id,
            "type": "DATA",
            "data_object_metadata.content_origin": "labfolder",
        }
    }
    response = query_db(query, CONFIGPARAMS["couchDBStorageDatabaseName"])
    return response if return_as_string else json.loads(response)


@APP.route("/storage/packages", methods=["GET"])
def get_package_objects():
    """
    Routed from /storage/packages
    Requests all docs from storage with type package for user
    """
    if not "session_user" in request.cookies or not "session_auth" in request.cookies:
        return (
            {"Error": FAILED_AUTHENTICATION},
            401,
            {"Content-Type": "application/json"},
        )
    if not check_session(
        request.cookies["session_user"], request.cookies["session_auth"]
    ):
        return (
            {"Error": FAILED_AUTHENTICATION},
            401,
            {"Content-Type": "application/json"},
        )
    user_id = request.cookies["session_user"]
    out = get_packages(user_id, return_as_string=False)
    return json.dumps(out["docs"])


def get_packages(user_id, return_as_string=False):
    """
    Returns the package docs for @user_id either as (json)string or json-object.
    """
    query = {"selector": {"owner": user_id, "type": "PACKAGE"}}
    response = query_db(query, CONFIGPARAMS["couchDBStorageDatabaseName"])
    return response if return_as_string else json.loads(response)


@APP.route("/storage/all", methods=["GET"])
def get_storage_objects():
    """
    Routed from /storage/all
    Requests all docs from storage for user
    """
    if not "session_user" in request.cookies or not "session_auth" in request.cookies:
        return (
            {"Error": FAILED_AUTHENTICATION},
            401,
            {"Content-Type": "application/json"},
        )
    if not check_session(
        request.cookies["session_user"], request.cookies["session_auth"]
    ):
        return (
            {"Error": FAILED_AUTHENTICATION},
            401,
            {"Content-Type": "application/json"},
        )
    user_id = request.cookies["session_user"]
    out = get_storage_for_user(user_id, return_as_string=False)
    return json.dumps(out)


def get_storage_for_user(user_id, return_as_string=False):
    """
    Returns the package and data docs for @user_id either as (json)string or json-object.
    """
    query = {"selector": {"owner": user_id}}
    response = json.loads(query_db(query, CONFIGPARAMS["couchDBStorageDatabaseName"]))[
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
    if not "session_user" in request.cookies or not "session_auth" in request.cookies:
        return (
            {"Error": FAILED_AUTHENTICATION},
            401,
            {"Content-Type": "application/json"},
        )
    if not check_session(
        request.cookies["session_user"], request.cookies["session_auth"]
    ):
        return (
            {"Error": FAILED_AUTHENTICATION},
            401,
            {"Content-Type": "application/json"},
        )
    user_id = request.cookies["session_user"]
    token = authenticate_couchdb()
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
        query_db(query, CONFIGPARAMS["couchDBStorageDatabaseName"])
    )
    url = (
        CONFIGPARAMS["couchDBBaseURL"]
        + "/"
        + CONFIGPARAMS["couchDBStorageDatabaseName"]
        + "/"
        + data["package_id"]
    )
    # prepare date to be written to db. if it is an update we only need to change some
    if (
        len(check_response["docs"]) > 0
    ):  # only one entry with same id should exist at the same time
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
    if not "session_user" in request.cookies or not "session_auth" in request.cookies:
        return (
            {"Error": FAILED_AUTHENTICATION},
            401,
            {"Content-Type": "application/json"},
        )
    if not check_session(
        request.cookies["session_user"], request.cookies["session_auth"]
    ):
        return (
            {"Error": FAILED_AUTHENTICATION},
            401,
            {"Content-Type": "application/json"},
        )
    user_id = request.cookies["session_user"]
    token = authenticate_couchdb()
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
        query_db(query, CONFIGPARAMS["couchDBMetaDataDatabaseName"])
    )
    if len(check_response["docs"]) > 0:  # found the entry to delete
        print("found entryx to delete in db")
        url = (
            CONFIGPARAMS["couchDBBaseURL"]
            + "/"
            + CONFIGPARAMS["couchDBMetaDataDatabaseName"]
            + "/"
            + data["package_id"]
        )
        headers["If-Match"] = check_response["docs"][0]["_rev"]
        response = requests.delete(url, headers=headers, data=data)
        if response:
            print("suc delete")
            return (
                json.dumps({"Result": "All good"}),
                200,
                {"Content-Type": "application/json"},
            )
        print("error delete")
    return (
        json.dumps({"Result": "Error deleting package"}),
        500,
        {"Content-Type": "application/json"},
    )


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
        if DEBUG:
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
        query = {"selector": {"owner": item["owner"], "package_id": item["package_id"]}}
        response = json.loads(
            query_db(query, CONFIGPARAMS["couchDBStorageDatabaseName"])
        )
        if len(response["docs"]) >= 0:
            headers["If-Match"] = response["docs"][0]["_rev"]
            t_url = url + "/" + response["docs"][0]["_id"]
            requests.put(t_url, headers=headers, data=json.dumps(item))
        else:
            requests.post(url, headers=headers, data=json.dumps(item))


# checks if elements to download already exist in database. pops elements which are already
# existing of the checkArray. Only checks labfolder content....
# check_elements is a list of dicts: (projectID: str, entryID: str, elementID: str, versionID: str)
def remove_already_existing_tupel(user_id, check_elements):
    """
    Checks if in storage file of @user_id there are already files which are identical to
    @check_elements. @check_elements is stripped of already existing entries and returned.
    """
    output = []
    for item in check_elements:
        query = {
            "selector": {
                "owner": user_id,
                "origin_metadata": {
                    "project_id": item["project_id"],
                    "entry_id": item["entry_id"],
                    "entry_version_id": item["entry_version_id"],
                    "element_id": item["element_id"],
                    "element_version_id": item["element_version_id"],
                },
            }
        }
        # if this reponse returns more hits than 1 the database is broken and we have duplicates
        response = json.loads(
            query_db(query, CONFIGPARAMS["couchDBStorageDatabaseName"])
        )
        if len(response["docs"]) == 0:
            output.append(item)
    return output


def create_zip_from_files(download_meta, filename):
    """curl
    create zip file with name @filenmane for requested files in @download_meta.
    """
    zip_file = ZipFile(filename, "w")
    cdb_doc_url_base = (
        CONFIGPARAMS["couchDBBaseURL"]
        + "/"
        + CONFIGPARAMS["couchDBDocumentDatabaseName"]
        + "/"
    )
    for ele in download_meta:
        filename = ele["data_object_metadata"]["db_filename"]
        # each element should only have one version, so wen access the first element
        cdb_doc_url = (
            cdb_doc_url_base + ele["data_object_metadata"]["doc_id"] + "/" + filename
        )
        tmp_path_file = Path(
            CONFIGPARAMS["tempFolder"] + ele["origin_metadata"]["element_id"]
        )
        token = authenticate_couchdb()
        if not token:
            return
        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "Cookie": token,
        }
        response = requests.get(cdb_doc_url, headers=headers)
        if response:
            if (
                ele["origin_metadata"]["element_type"] == "TEXT"
                or ele["origin_metadata"]["element_type"] == "TABLE"
            ):
                tmp_path_file.write_text(response.text)
            elif ele["origin_metadata"]["element_type"] == "IMAGE":
                tmp_path_file.write_bytes(response.content)
            absname = str(tmp_path_file.resolve())
            zip_file.write(absname, arcname=filename)
            try:
                tmp_path_file.unlink()
            except FileNotFoundError:
                print("Error deleting file from filesystem: File not Found")
    zip_file.close()


@APP.route("/metadata/structures", methods=["GET"])
def get_metadata():
    """
    Return Metadata structure file from server, providing information about supported meta data
    """
    if not "session_user" in request.cookies or not "session_auth" in request.cookies:
        return (
            {"Error": FAILED_AUTHENTICATION},
            401,
            {"Content-Type": "application/json"},
        )
    if not check_session(
        request.cookies["session_user"], request.cookies["session_auth"]
    ):
        return (
            {"Error": FAILED_AUTHENTICATION},
            401,
            {"Content-Type": "application/json"},
        )
    data = ""
    with open(CONFIGPARAMS["METADATA_INFO_FILE"]) as file:
        data = file.read()
    return json.dumps(data)


@APP.route("/metadata/export_definitions", methods=["GET"])
def get_export_definitions():
    """
    Return Metadata exports file from server, defining exports how it will be exported
    """
    if not "session_user" in request.cookies or not "session_auth" in request.cookies:
        return (
            {"Error": FAILED_AUTHENTICATION},
            401,
            {"Content-Type": "application/json"},
        )
    if not check_session(
        request.cookies["session_user"], request.cookies["session_auth"]
    ):
        return (
            {"Error": FAILED_AUTHENTICATION},
            401,
            {"Content-Type": "application/json"},
        )
    data = ""
    with open(CONFIGPARAMS["METADATA_EXPORT_DEFINITIONS"]) as file:
        data = file.read()
    return json.dumps(data)


@APP.route("/metadata/export_mappings", methods=["GET"])
def get_export_mappings():
    """
    Return Metadata structure file from server, providing mapping between schemes and exports
    """
    if not "session_user" in request.cookies or not "session_auth" in request.cookies:
        return (
            {"Error": FAILED_AUTHENTICATION},
            401,
            {"Content-Type": "application/json"},
        )
    if not check_session(
        request.cookies["session_user"], request.cookies["session_auth"]
    ):
        return (
            {"Error": FAILED_AUTHENTICATION},
            401,
            {"Content-Type": "application/json"},
        )
    data = ""
    with open(CONFIGPARAMS["METADATA_EXPORT_MAPPINGS"]) as file:
        data = file.read()
    return json.dumps(data)


@APP.route("/metadata/user", methods=["GET"])
def get_user_stored_metadata():
    """
    Routed from /metadata/user GET
    Gets the stored metadata sets for the requesting user
    """
    if not "session_user" in request.cookies or not "session_auth" in request.cookies:
        return (
            {"Error": FAILED_AUTHENTICATION},
            401,
            {"Content-Type": "application/json"},
        )
    if not check_session(
        request.cookies["session_user"], request.cookies["session_auth"]
    ):
        return (
            {"Error": FAILED_AUTHENTICATION},
            401,
            {"Content-Type": "application/json"},
        )
    user_id = request.cookies["session_user"]
    query = {"selector": {"owner": user_id}}
    response = json.loads(query_db(query, CONFIGPARAMS["couchDBMetaDataDatabaseName"]))
    return json.dumps(response["docs"])


# TODO TEST
@APP.route("/metadata/user/delete", methods=["PUT"])
def delete_user_metadata_set():
    """
    Routed from /metadata/user/delete PUT
    Delete the meta_set provided in data from database
    """
    if not "session_user" in request.cookies or not "session_auth" in request.cookies:
        return (
            {"Error": FAILED_AUTHENTICATION},
            401,
            {"Content-Type": "application/json"},
        )
    if not check_session(
        request.cookies["session_user"], request.cookies["session_auth"]
    ):
        return (
            {"Error": FAILED_AUTHENTICATION},
            401,
            {"Content-Type": "application/json"},
        )
    user_id = request.cookies["session_user"]
    token = authenticate_couchdb()
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
        query_db(query, CONFIGPARAMS["couchDBMetaDataDatabaseName"])
    )
    if len(check_response["docs"]) > 0:  # found the entry to delete
        url = (
            CONFIGPARAMS["couchDBBaseURL"]
            + "/"
            + CONFIGPARAMS["couchDBMetaDataDatabaseName"]
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
    if not "session_user" in request.cookies or not "session_auth" in request.cookies:
        return (
            {"Error": FAILED_AUTHENTICATION},
            401,
            {"Content-Type": "application/json"},
        )
    if not check_session(
        request.cookies["session_user"], request.cookies["session_auth"]
    ):
        return (
            {"Error": FAILED_AUTHENTICATION},
            401,
            {"Content-Type": "application/json"},
        )
    user_id = request.cookies["session_user"]
    token = authenticate_couchdb()
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
        query_db(query, CONFIGPARAMS["couchDBMetaDataDatabaseName"])
    )
    url = (
        CONFIGPARAMS["couchDBBaseURL"]
        + "/"
        + CONFIGPARAMS["couchDBMetaDataDatabaseName"]
        + "/"
        + data["set_id"]
    )
    if (
        len(check_response["docs"]) > 0
    ):  # only one entry with same id should exist at the same time
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
    if not "session_user" in request.cookies or not "session_auth" in request.cookies:
        return (
            {"Error": FAILED_AUTHENTICATION},
            401,
            {"Content-Type": "application/json"},
        )
    if not check_session(
        request.cookies["session_user"], request.cookies["session_auth"]
    ):
        return (
            {"Error": FAILED_AUTHENTICATION},
            401,
            {"Content-Type": "application/json"},
        )
    user_id = request.cookies["session_user"]
    query = {"selector": {"owner": user_id}}
    response = json.loads(query_db(query, CONFIGPARAMS["couchDBIngestsDatabaseName"]))
    return json.dumps(response["docs"])


def get_ingest_by_user_and_id_in_review_db(user_id, ingest_id):
    """
    returns the ingest for ingest_id and user_id as json object
    """
    query = {"selector": {"owner": user_id, "ingest_id": ingest_id}}
    # query = {"selector": {"owner": user_id}}
    response = json.loads(
        query_db(query, CONFIGPARAMS["couchDBIngestReviewDatabaseName"])
    )
    return response["docs"]


def get_ingest_by_user_and_id_in_ingest_db(user_id, ingest_id):
    """
    returns the ingest for ingest_id and user_id as json object
    """
    query = {"selector": {"owner": user_id, "ingest_id": ingest_id}}
    # query = {"selector": {"owner": user_id}}
    response = json.loads(query_db(query, CONFIGPARAMS["couchDBIngestsDatabaseName"]))
    return response["docs"]


@APP.route("/ingest/user", methods=["PUT"])
def store_user_ingest():
    """
    Routed from /ingest/user PUT
    Stores an updated ingests for the user, version managing is done on client side
    """
    if not "session_user" in request.cookies or not "session_auth" in request.cookies:
        return (
            {"Error": FAILED_AUTHENTICATION},
            401,
            {"Content-Type": "application/json"},
        )
    if not check_session(
        request.cookies["session_user"], request.cookies["session_auth"]
    ):
        return (
            {"Error": FAILED_AUTHENTICATION},
            401,
            {"Content-Type": "application/json"},
        )
    user_id = request.cookies["session_user"]
    data = json.loads(request.get_data())
    data["owner"] = user_id
    return update_or_create_user_ingest(user_id, data)


def update_or_create_user_ingest(user_id, ingest):
    """
    send the ingest for user_id to database. updates existing or creates a new one if none with same
    id is found in db
    """
    print("in update or create")
    query = {"selector": {"owner": user_id, "ingest_id": ingest["ingest_id"]}}
    check_response = json.loads(
        query_db(query, CONFIGPARAMS["couchDBIngestsDatabaseName"])
    )
    url = (
        CONFIGPARAMS["couchDBBaseURL"]
        + "/"
        + CONFIGPARAMS["couchDBIngestsDatabaseName"]
        + "/"
        + ingest["ingest_id"]
    )
    token = authenticate_couchdb()
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
    if (
        len(check_response["docs"]) > 0
    ):  # only one entry with same id should exist at the same time
        print("check_response")
        print(check_response)
        headers["If-Match"] = check_response["docs"][0]["_rev"]
        if "_id" in ingest:
            del ingest["_id"]
        if "_rev" in ingest:
            del ingest["_rev"]
    print(url)
    print(headers)
    print(ingest)
    response = requests.put(url, headers=headers, data=json.dumps(ingest))
    print(response.text)
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
        query_db(query, CONFIGPARAMS["couchDBIngestsDatabaseName"])
    )
    url = (
        CONFIGPARAMS["couchDBBaseURL"]
        + "/"
        + CONFIGPARAMS["couchDBIngestsDatabaseName"]
        + "/"
        + ingest["ingest_id"]
    )
    token = authenticate_couchdb()
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
    if (
        len(check_response["docs"]) > 0
    ):  # only one entry with same id should exist at the same time
        headers["If-Match"] = check_response["docs"][0]["_rev"]
        response = requests.delete(url, headers=headers, data=json.dumps(ingest))
        print(response.text)
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
    print("in update or create")
    query = {"selector": {"owner": user_id, "ingest_id": ingest["ingest_id"]}}
    check_response = json.loads(
        query_db(query, CONFIGPARAMS["couchDBIngestReviewDatabaseName"])
    )
    url = (
        CONFIGPARAMS["couchDBBaseURL"]
        + "/"
        + CONFIGPARAMS["couchDBIngestReviewDatabaseName"]
        + "/"
        + ingest["ingest_id"]
    )
    token = authenticate_couchdb()
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
    if (
        len(check_response["docs"]) > 0
    ):  # only one entry with same id should exist at the same time
        print("check_response")
        print(check_response)
        headers["If-Match"] = check_response["docs"][0]["_rev"]
    print(url)
    print(headers)
    print(ingest)
    del ingest["_id"]
    del ingest["_rev"]
    print(ingest)
    response = requests.put(url, headers=headers, data=json.dumps(ingest))
    print(response.text)
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
    if not "session_user" in request.cookies or not "session_auth" in request.cookies:
        return (
            {"Error": FAILED_AUTHENTICATION},
            401,
            {"Content-Type": "application/json"},
        )
    if not check_session(
        request.cookies["session_user"], request.cookies["session_auth"]
    ):
        return (
            {"Error": FAILED_AUTHENTICATION},
            401,
            {"Content-Type": "application/json"},
        )
    token = authenticate_couchdb()
    if not token:
        return (
            {"Result": "Internal Server Error"},
            500,
            {"Content-Type": "application/json"},
        )
    user_id = request.cookies["session_user"]
    packages = get_packages(user_id, return_as_string=False)[
        "docs"
    ]  # returns only type == package
    ingest = json.loads(request.get_data())
    ingest_review_path = (
        CONFIGPARAMS["LZV_REVIEW"] + "/" + ingest["ingest_id"] + "/content/"
    )
    ingest["owner"] = user_id
    success = create_ingest_on_filesystem(
        user_id, ingest["ingest_id"], CONFIGPARAMS["LZV_REVIEW"], review_db=False
    )
    if not success:
        return (
            json.dumps({"Result": "Error dumping ingest on filesystem"}),
            500,
            {"Content-Type": "application/json"},
        )
    couchdb_url = (
        CONFIGPARAMS["couchDBBaseURL"]
        + "/"
        + CONFIGPARAMS["couchDBIngestReviewDatabaseName"]
        + "/"
        + ingest["ingest_id"]
    )
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "Cookie": token,
    }
    if DEBUG:
        print("trying to submit ingest for user with url: " + couchdb_url)
        print(headers)
        print("ingest:")
        print(json.dumps(ingest))
    response = requests.put(couchdb_url, headers=headers, data=json.dumps(ingest))
    print(response.text)
    if response:
        return (
            json.dumps({"Result": "All good"}),
            200,
            {"Content-Type": "application/json"},
        )
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


@APP.route("/ingest/approve", methods=["PUT"])
def approve_ingest():
    """
    called when the reviewer approves the ingest. the process of deploying the ingest to rosetta is
    then started.
    """
    if not "session_user" in request.cookies or not "session_auth" in request.cookies:
        return (
            {"Error": FAILED_AUTHENTICATION},
            401,
            {"Content-Type": "application/json"},
        )
    if not check_session(
        request.cookies["session_user"], request.cookies["session_auth"]
    ):
        return (
            {"Error": FAILED_AUTHENTICATION},
            401,
            {"Content-Type": "application/json"},
        )
    if not check_user_permission_review(request.cookies["session_user"]):
        return (
            {"Error": "NOT AUTHORIZED FOR REVIEW"},
            401,
            {"Content-Type": "application/json"},
        )
    user_id = request.cookies["session_user"]
    ingest_id = request.args.get("ingest_id")
    success = create_ingest_on_filesystem(
        user_id, ingest_id, CONFIGPARAMS["LZV_HOTFOLDER"]
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
        print("update in reviewdb after ingest:")
        print(resp)
        if resp:
            # remove the review files from file system
            review_path = CONFIGPARAMS["LZV_REVIEW"] + ingest["ingest_id"]
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


def create_ingest_on_filesystem(user_id, ingest_id, base_folder, review_db=True):
    """
    create the files for the ingest on the defined folder. folder should be hotfolder to rosetta
    system. also created the mets files basedo n the data provided in the ingest.
    """
    ingest = {}
    if review_db:
        ingest = get_ingest_by_user_and_id_in_review_db(user_id, ingest_id)
    else:
        ingest = get_ingest_by_user_and_id_in_ingest_db(user_id, ingest_id)
    if len(ingest) == 0:
        print("ERROR: cant find ingest requests to dump on filesystem")
        return False
    ingest = ingest[0]
    storage_file = get_storage_for_user(user_id)
    print("TRYING TO WRITE INGEST TO HOTFOLDER")
    path = base_folder
    folder = Path(path)
    if not folder.is_dir():
        print("Error: " + base_folder + " is not a directory")
        return False
    print(ingest)
    path += ingest["ingest_id"] + "/content/"

    mets_xml = mets.generate_mets_xml(ingest, storage_file)
    ingest_hotfolder_path = Path(path)
    ingest_hotfolder_path.mkdir(mode=0o777, parents=True, exist_ok=True)
    try:
        mets_file = Path(path + "ie1.xml")
        mets_file.touch(mode=0o770, exist_ok=True)
        mets_file.write_text(mets_xml)
    except:
        print("error creating mets file")
        return False

    flat_data = mets.get_ingest_data_files(ingest)
    success = True
    path += "streams/"
    ingest_hotfolder_path = Path(path)
    ingest_hotfolder_path.mkdir(mode=0o777, parents=True, exist_ok=True)
    for item in flat_data:
        for f in item["flat_data"]:
            cdb_doc_url = (
                CONFIGPARAMS["couchDBBaseURL"]
                + "/"
                + CONFIGPARAMS["couchDBDocumentDatabaseName"]
                + "/"
                + f["data_object_metadata"]["doc_id"]
                + "/"
                + f["data_object_metadata"]["doc_id"]
            )
            token = authenticate_couchdb()
            if not token:
                print("ERROR: authenticating couchdb")
                return False
            headers = {
                "Accept": "application/json",
                "Content-Type": "application/json",
                "Cookie": token,
            }
            response = requests.get(cdb_doc_url, headers=headers)
            if response:
                try:
                    tmp_path = path + f["data_object_metadata"]["filename"]
                    tmp_json_path = (
                        path + f["data_object_metadata"]["filename"] + ".json"
                    )
                    tmp_file = Path(tmp_path)
                    tmp_json_file = Path(tmp_json_path)
                    tmp_file.touch(mode=0o770, exist_ok=True)
                    tmp_json_file.touch(mode=0o770, exist_ok=True)
                    tmp_file.write_bytes(response.content)
                    tmp = [
                            item
                            for item in storage_file
                            if f["package_id"] == item["package_id"]
                        ][0]
                    print("tmp:")
                    print(tmp)
                    tmp_json_file.write_text(
                        json.dumps([
                            item
                            for item in storage_file
                            if f["package_id"] == item["package_id"]
                        ][0])
                    )
                except:
                    print("error printing file")
                    success = False
            else:
                print("error getting file from cdb")
                success = False
    if not success:  # remove all files eventually created bythe method
        print("error appeared, rm all files")
        shutil.rmtree(ingest_hotfolder_path)
    print(success)
    return success


# TODO function which checks state of ingest after


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


@APP.route("/ingest/toreview", methods=["GET"])
def get_toreview_ingests():
    """
    get Ingests which need to be reviewed. Review permission is checked before returning
     information. if no permission is available for review 401 is returned.
    """
    if not "session_user" in request.cookies or not "session_auth" in request.cookies:
        return (
            {"Error": FAILED_AUTHENTICATION},
            401,
            {"Content-Type": "application/json"},
        )
    if not check_session(
        request.cookies["session_user"], request.cookies["session_auth"]
    ):
        return (
            {"Error": FAILED_AUTHENTICATION},
            401,
            {"Content-Type": "application/json"},
        )
    if not check_user_permission_review(request.cookies["session_user"]):
        return (
            {"Error": "NOT AUTHORIZED FOR REVIEW"},
            401,
            {"Content-Type": "application/json"},
        )
    query = {"selector": {"state": "REVIEW"}}
    response = query_db(query, CONFIGPARAMS["couchDBIngestReviewDatabaseName"])
    return response


@APP.route("/ingest/submitted", methods=["GET"])
def get_submitted_ingests():
    """
    Get the submitted ingests for user from database
    """
    if not "session_user" in request.cookies or not "session_auth" in request.cookies:
        return (
            {"Error": FAILED_AUTHENTICATION},
            401,
            {"Content-Type": "application/json"},
        )
    if not check_session(
        request.cookies["session_user"], request.cookies["session_auth"]
    ):
        return (
            {"Error": FAILED_AUTHENTICATION},
            401,
            {"Content-Type": "application/json"},
        )
    query = {"selector": {"owner": request.cookies["session_user"]}}
    response = query_db(query, CONFIGPARAMS["couchDBIngestReviewDatabaseName"])
    if response:
        return response
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
    if not "session_user" in request.cookies or not "session_auth" in request.cookies:
        return (
            {"Error": FAILED_AUTHENTICATION},
            401,
            {"Content-Type": "application/json"},
        )
    if not check_session(
        request.cookies["session_user"], request.cookies["session_auth"]
    ):
        return (
            {"Error": FAILED_AUTHENTICATION},
            401,
            {"Content-Type": "application/json"},
        )
    package_id = request.args.get("package_id")
    user_id = request.cookies["session_user"]
    query = {"selector": {"package_id": package_id, "owner": user_id}}
    check_response = json.loads(
        query_db(query, CONFIGPARAMS["couchDBStorageDatabaseName"])
    )["docs"]
    if len(check_response) == 0:
        return (
            json.dumps(
                {
                    "Result": "Error: Invalid Package ID oder Package does not belong\
                         to user"
                }
            ),
            200,
            {"Content-Type": "application/json"},
        )
    # check if the post request has the file part
    if "uploaded_file" not in request.files:
        print("No file part")
        return (
            json.dumps({"Result": "Error: No files provided"}),
            500,
            {"Content-Type": "application/json"},
        )
    files = request.files.getlist("uploaded_file")
    print("files keys")
    # if user does not select file, browser also
    # submit an empty part without filename
    storage_metadata = []
    for file in files:
        if file.filename == "":
            print("No selected file")
            continue
        if file:
            # filename = file.filename
            print(file.filename)
            # file.save(os.path.join(APP.config['UPLOAD_FOLDER'], filename))
            # print("Succesfully saved files")
            metadata_obj = create_storage_data_structure_from_upload(user_id, file)
            print("created storage for file:")
            print("uploading to db")
            response = upload_file_to_couchdb_document_db(file, metadata_obj)
            if response:
                print("successfull")
                storage_metadata.append(metadata_obj)
    if len(storage_metadata) > 0:
        print("storage_metadata")
        print(storage_metadata)
        add_to_storage(storage_metadata)
        package_response = append_children_to_package(
            user_id, package_id, storage_metadata
        )
        if package_response:  # should be true, else there is a inconsistency in db.
            return (
                json.dumps({"Result": "Succesfully saved files"}),
                200,
                {"Content-Type": "application/json"},
            )
        return (
            json.dumps({"Result": "Error: Saving Package File"}),
            500,
            {"Content-Type": "application/json"},
        )
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
    token = authenticate_couchdb()
    if not token:
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
        query_db(query, CONFIGPARAMS["couchDBStorageDatabaseName"])
    )
    url = (
        CONFIGPARAMS["couchDBBaseURL"]
        + "/"
        + CONFIGPARAMS["couchDBStorageDatabaseName"]
        + "/"
        + package_id
    )
    # prepare date to be written to db. if it is an update we only need to change some
    if (
        len(check_response["docs"]) > 0
    ):  # only one entry with same id should exist at the same time
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
    return (
        json.dumps({"Result": "Error updating file to database."}),
        500,
        {"Content-Type": "application/json"},
    )


def upload_file_to_couchdb_document_db(file, metadata_obj):
    """
    Uploads a file to the document db. Also updated the metadata_obj with the doc_id, file_type,
    filename and is_stored flag
    """
    token = authenticate_couchdb()
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
        CONFIGPARAMS["couchDBBaseURL"]
        + "/"
        + CONFIGPARAMS["couchDBDocumentDatabaseName"]
    )
    print("touched doc")
    json_answer = json.loads(
        requests.post(couchdb_url, headers=couch_header, data=json.dumps({})).text
    )
    couch_header["If-Match"] = json_answer["rev"]
    couchdb_url = couchdb_url + "/" + json_answer["id"] + "/"
    filename = secure_filename(file.filename)
    couch_header["Content-Type"] = file.mimetype
    file_data = file.read()
    couchdb_url = couchdb_url + json_answer["id"]
    att_create_response = requests.put(
        couchdb_url, headers=couch_header, data=file_data
    )
    if att_create_response:
        metadata_obj["data_object_metadata"]["file_type"] = file.mimetype
        metadata_obj["data_object_metadata"]["is_stored"] = bool(att_create_response)
        metadata_obj["data_object_metadata"]["filename"] = filename
        metadata_obj["data_object_metadata"]["doc_id"] = json_answer["id"]
    else:
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
    if not "session_user" in request.cookies or not "session_auth" in request.cookies:
        return (
            {"Error": FAILED_AUTHENTICATION},
            401,
            {"Content-Type": "application/json"},
        )
    if not check_session(
        request.cookies["session_user"], request.cookies["session_auth"]
    ):
        return (
            {"Error": FAILED_AUTHENTICATION},
            401,
            {"Content-Type": "application/json"},
        )
    print("creating new package")
    user_id = request.cookies["session_user"]
    data = {}
    data["package_id"] = str(uuid.uuid4())
    data["name"] = request.args.get("name")
    token = authenticate_couchdb()
    if not token:
        return ""
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "Cookie": token,
    }
    print("package_name: " + data["name"])
    url = (
        CONFIGPARAMS["couchDBBaseURL"]
        + "/"
        + CONFIGPARAMS["couchDBStorageDatabaseName"]
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
    print("package to put:")
    print(json.dumps(data))
    response = requests.put(url, headers=headers, data=json.dumps(data))
    if response:
        return (
            json.dumps(
                {"Result": "Succesfully saved files", "package_id": data["package_id"]}
            ),
            200,
            {"Content-Type": "application/json"},
        )
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

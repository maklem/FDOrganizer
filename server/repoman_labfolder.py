'''
Module for labfolder integration. implements the api calls to access labfolde repository
'''

import json
import time
import uuid
from pathlib import Path
from zipfile import ZipFile

import requests
from flask import Blueprint, request, send_from_directory

import lzv_util

rep_labfolder = Blueprint('labfolder', __name__)

DEBUG = 1

# ----------------------Authentification LabFolder------------------------------
@rep_labfolder.route("/auth/login", methods=["POST"])
def authenticate_labfolder():
    """
    Authenticate to LabFolder and returns the login answer
    """
    url = lzv_util.CONFIGPARAMS["labFolderBaseURL"] + "/auth/login"
    data = request.get_data()
    headers = {"Content-Type": "application/json"}
    response = requests.post(url, data=data, headers=headers)
    return response.text


@rep_labfolder.route("/auth/logout", methods=["POST"])
def logout_labfolder():
    """
    Kills the Session associated to the provided token
    """
    url = lzv_util.CONFIGPARAMS["labFolderBaseURL"] + "/auth/logout"
    headers = {
        "Content-Type": "application/json",
        "Authorization": "Token " + request.headers["Token"],
        "User-Agent": lzv_util.CONFIGPARAMS["labFolderDefaultUserAgentHeader"],
    }

    response = requests.post(url, headers=headers)
    return response.text


@rep_labfolder.route("/projects", methods=["GET"])
def get_projects():
    """
    Accesses LabFolder by Token and retreives the Projects from User. Answer is returned by REST.
    """
    url = lzv_util.CONFIGPARAMS["labFolderBaseURL"] + "/projects"
    headers = {
        "Content-Type": "application/json",
        "Authorization": "Token " + request.headers["Token"],
        "User-Agent": lzv_util.CONFIGPARAMS["labFolderDefaultUserAgentHeader"],
    }
    response = requests.get(url, headers=headers)
    return response.text


@rep_labfolder.route("/entries", methods=["GET"])
def get_notebook_entries():
    """
    Accesses LabFolder by Token and retreives the Entries from User. Answer is returned by REST.
    """
    url = lzv_util.CONFIGPARAMS["labFolderBaseURL"] + "/entries"
    headers = {
        "Content-Type": "application/json",
        "Authorization": "Token " + request.headers["Token"],
        "User-Agent": lzv_util.CONFIGPARAMS["labFolderDefaultUserAgentHeader"],
    }
    response = requests.get(url, headers=headers)
    return response.text


@rep_labfolder.route("/download", methods=["GET"])
def download_file_to_client():
    """
    Creates a zip File with the Entry requested by the user, and transfers the zip by HTTP.
    Receives only a list of ids of dataobjects. querys these from database
    """
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
        lzv_util.query_db(query, lzv_util.CONFIGPARAMS["couchDBStorageDatabaseName"])
    )["docs"]
    filename = (
        request.cookies["session_user"]
        + "-"
        + time.strftime("%d-%m-%Y")
        + "-"
        + time.strftime("%H:%M:%S")
        + ".zip"
    )
    if download_meta:
        create_zip_from_files(download_meta, lzv_util.CONFIGPARAMS["tempFolder"] + filename)
    else:
        return (json.dumps({"Error": "Missing Parameter id"}), \
                500,{"Content-Type": "application/json"})
    return send_from_directory(lzv_util.CONFIGPARAMS["tempFolder"], filename, as_attachment=True)


@rep_labfolder.route("/storage", methods=["GET"])
def get_labfolder_storage_data():
    """
    Routed from /labfolder/storage
    Requests the storage file, containg metadata about stored files for the requesting user
    """
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
    response = lzv_util.query_db(query, lzv_util.CONFIGPARAMS["couchDBStorageDatabaseName"])
    return response if return_as_string else json.loads(response)


@rep_labfolder.route("/elements/download", methods=["POST"])
def download():
    """
    Download data provided in request from labfolder. Checks if duplicates already are in db.
    Only downloads new files from labfolder. Adds documents to doc db and metadata files to
    storage db. also creates package files for entrys for all elements containing the elements.
    """
    user_id = request.cookies["session_user"]
    data = request.get_data()
    json_data = json.loads(data)
    json_data = remove_already_existing_tupel(user_id, json_data)
    storage_metadata = []
    for item in json_data:
        storage_metadata.append(
            create_storage_data_structure_from_labfolder(user_id, item)
        )
    if storage_metadata:
        download_files_from_labfolder(storage_metadata)
        package_objects = create_package_for_downloaded_labfolder_data(
            user_id, storage_metadata
        )
        storage_metadata += package_objects
        lzv_util.add_to_storage(storage_metadata)
    return (json.dumps({"Message":"All good!"}), 200,{"Content-Type": "application/json"})


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
            "origin_uuid" : input_set["element_id"],
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
            lzv_util.query_db(query, lzv_util.CONFIGPARAMS["couchDBStorageDatabaseName"])
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
        lzv_util.CONFIGPARAMS["couchDBBaseURL"]
        + "/"
        + lzv_util.CONFIGPARAMS["couchDBDocumentDatabaseName"]
        + "/"
    )
    for ele in download_meta:
        couch_db_id = ele["data_object_metadata"]["db_filename"]
        # each element should only have one version, so wen access the first element
        cdb_doc_url = (
            cdb_doc_url_base + ele["data_object_metadata"]["doc_id"] + "/" + couch_db_id
        )
        tmp_path_file = Path(
            lzv_util.CONFIGPARAMS["tempFolder"] + ele["origin_metadata"]["element_id"]
        )
        token = lzv_util.authenticate_couchdb()
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
            elif (
                ele["origin_metadata"]["element_type"] == "IMAGE"
                or ele["origin_metadata"]["element_type"] == "FILE"
                ):
                tmp_path_file.write_bytes(response.content)
            absname = str(tmp_path_file.resolve())
            zip_file.write(absname, arcname=ele["data_object_metadata"]["filename"])
            try:
                tmp_path_file.unlink()
            except FileNotFoundError:
                print("Error deleting file from filesystem: File not Found")
    zip_file.close()

# @APP.route('/elements/file' , methods=['GET'])
def download_files_from_labfolder(data_array):
    """
    Function is called for File Download from LabFolder. This Function downloads the files and
    stored it in the database.
    """
    token = lzv_util.authenticate_couchdb()
    if not token:
        return
    for element in data_array:
        if element["origin_metadata"]["element_type"] == "IMAGE":
            file_info_url = (
                lzv_util.CONFIGPARAMS["labFolderBaseURL"]
                + "/elements/image/"
                + element["origin_metadata"]["element_id"]
            )
            file_url = file_info_url + "/original-data"
        elif element["origin_metadata"]["element_type"] == "FILE":
            file_info_url = (
                lzv_util.CONFIGPARAMS["labFolderBaseURL"]
                + "/elements/file/"
                + element["origin_metadata"]["element_id"]
            )
            file_url = file_info_url + "/download"
        elif element["origin_metadata"]["element_type"] == "TABLE":
            file_url = (
                lzv_util.CONFIGPARAMS["labFolderBaseURL"]
                + "/elements/table/"
                + element["origin_metadata"]["element_id"]
            )
        elif element["origin_metadata"]["element_type"] == "TEXT":
            file_url = (
                lzv_util.CONFIGPARAMS["labFolderBaseURL"]
                + "/elements/text/"
                + element["origin_metadata"]["element_id"]
            )
        else:
            continue
        headers = {
            "Content-Type": "application/json",
            "Authorization": "Token " + request.headers["Token"],
            "User-Agent": lzv_util.CONFIGPARAMS["labFolderDefaultUserAgentHeader"],
        }
        couch_header = {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "Cookie": token,
        }
        file_response = requests.get(file_url, headers=headers)
        couchdb_url = (
            lzv_util.CONFIGPARAMS["couchDBBaseURL"]
            + "/"
            + lzv_util.CONFIGPARAMS["couchDBDocumentDatabaseName"]
        )
        json_answer = json.loads(
            requests.post(couchdb_url, headers=couch_header, data=json.dumps({})).text
        )
        couch_header["If-Match"] = json_answer["rev"]
        element["data_object_metadata"]["doc_id"] = json_answer["id"]
        couchdb_url = couchdb_url + "/" + json_answer["id"] + "/"
        file_name = ""
        file_suffix = ""
        file_data = ""
        if (element["origin_metadata"]["element_type"] == "IMAGE"
            or element["origin_metadata"]["element_type"] == "FILE"
        ):
            file_info_reponse_jdata = json.loads(
                requests.get(file_info_url, headers=headers).text
            )
            print("fileinforesponse:")
            print(json.dumps(file_info_reponse_jdata))
            if element["origin_metadata"]["element_type"] == "IMAGE":
                file_name = file_info_reponse_jdata["title"]
                couch_header["Content-Type"] = file_info_reponse_jdata["original_file_content_type"]
            else:
                file_name = file_info_reponse_jdata["file_name"]
                couch_header["Content-Type"] = file_info_reponse_jdata["content_type"]
            file_data = file_response.content
            couchdb_url = couchdb_url + json_answer["id"]
            file_suffix = ""
            att_create_response = requests.put(
                couchdb_url, headers=couch_header, data=file_data
            )
            element["data_object_metadata"]["is_stored"] = bool(att_create_response)
        elif (element["origin_metadata"]["element_type"] == "TABLE"
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
        print(type(file_data))
        if type(file_data) is not bytes:
            print("in encode")
            file_data = file_data.encode('utf-8')
        element["data_object_metadata"]["checksums"] = [{
            "type" : "SHA224",
            "hash" : lzv_util.calculate_sha224_from_data(file_data)
        },
        {
            "type" : "MD5",
            "hash" : lzv_util.calculate_md5_from_data(file_data)
        }
        ]
        print(json.dumps(element["data_object_metadata"]["checksums"]))
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


@rep_labfolder.route("/mdb/categories", methods=["GET"])
def get_mdb_categories():
    """
    Routed from /mdb/categories.
    Retreives the category information about Material Databse from labfolder and returns this.
    """
    url = lzv_util.CONFIGPARAMS["labFolderBaseURL"] + "/mdb/categories"
    # prepare header
    headers = {
        "Content-Type": "application/json",
        "Authorization": "Token " + request.headers["Token"],
        "User-Agent": lzv_util.CONFIGPARAMS["labFolderDefaultUserAgentHeader"],
    }
    response = requests.get(url, headers=headers)
    return response.text


# ----does only support filtering by category_id----
@rep_labfolder.route("/mdb/items", methods=["GET"])
def download_mdb_items():
    """
    routed from /mdb/items
    Download the Material Database Items to Server.
    """
    url_items = lzv_util.CONFIGPARAMS["labFolderBaseURL"] + "/mdb/items"
    url_categories = lzv_util.CONFIGPARAMS["labFolderBaseURL"] + "/mdb/categories"
    category_id = request.args.get("category_id", default="", type=str)
    token = request.args.get("token", default="", type=str)
    if category_id == "":
        return json.dumps({"Error": "Missing Parameter id"}), 400,\
                {"Content-Type" : "application/json"}
    if token == "":
        return json.dumps({"Error": "Missing Labfolder Token"}), 400,\
                {"Content-Type" : "application/json"}
    url_items = url_items + "?category_id=" + category_id
    url_categories = url_categories + "/" + category_id
    # prepare header
    headers = {
        "Content-Type": "application/json",
        "Authorization": "Token " + token,
        "User-Agent": lzv_util.CONFIGPARAMS["labFolderDefaultUserAgentHeader"],
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
    f = open(lzv_util.CONFIGPARAMS["tempFolder"] + filename, "w")
    f.write(file_data)
    f.close()
    return send_from_directory(lzv_util.CONFIGPARAMS["tempFolder"], filename, as_attachment=True)
    # return json.dumps({'Result' : 'All good'}), 200, {'Content-Type' : 'application/json'}

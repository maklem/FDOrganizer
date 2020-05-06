"""
Software for LZV Server.
"""
import time
from pathlib import Path
from zipfile import ZipFile
import json
import requests

from flask import Flask
from flask_cors import CORS
from flask import request, render_template, send_from_directory
# from flask import render_template
# from flask import send_from_directory
# from flask import Response
# from flask import make_response
# from flask import send_file
# from flask import *
# from zipfile import *

DEBUG = 1



#
# All These Parameteres need to be included in a config file which is root read only and accessed
#on runtime
#

#baseURL of labFolder
# CONFIGPARAMS["labFolderBaseURL"] = 'https://eln.labfolder.com/api/v2'
#storage base url - here the downlaoded data is stored, should terminate with a '/'
# storageBaseURL = './LabFolderData/'
# storage_fileName = 'storage.json'
# CONFIGPARAMS["tempFolder"] = "./tmp/"

#couchDBConfiguration Parameters
# CONFIGPARAMS["couchDBBaseURL"] = "http://127.0.0.1:5984"
# CONFIGPARAMS["couchDBAdmin"] = "admin"
# CONFIGPARAMS["couchDBPassword"] = "aodqfyUQqA"
# couchDBToken = ""
# CONFIGPARAMS["couchDBStorageDatabaseName"] = "storage"
# CONFIGPARAMS["couchDBDocumentDatabaseName"] = "documents"
# CONFIGPARAMS["couchDBStaticDatabaseName"] = "static"


#DELETE AFTER DEV
DEVUSER_ID = "bt303343"
#----------------------global Parameters-------------------------------------------

CONFIGPARAMS = {}

#----------------------initialization------------------------------------------

APP = Flask(__name__)
CORS(APP)
try:
    with open('config.json') as f:
        CONFIGPARAMS = json.load(f)
except:
    print(("Error loading config-File! Quitting..."))



#----------------------Page Navigation-----------------------------------------
@APP.route('/')
def navhome():
    '''
    Navigation to site Home
    '''
    return render_template("index.html")

@APP.route('/impressum')
def navimpressum():
    '''
    Navigation to site Impressum
    '''
    return render_template("impressum.html")

@APP.route('/history')
def navhistory():
    '''
    Navigation to site History
    '''
    return render_template("history.html")

@APP.route('/labfolder')
def navlabfolder():
    '''
    Navigation to site Labfolder
    '''
    return render_template("labfolder.html")

@APP.route('/easydb')
def naveasydb():
    '''
    Navigation to site easyDB
    '''
    return render_template("easydb.html")

#----------------------Authentification LabFolder------------------------------
@APP.route('/auth/login', methods=['POST'])
def authenticate_labfolder():
    '''
    Authenticate to LabFolder and returns the login answer
    '''
    url = CONFIGPARAMS["labFolderBaseURL"] + '/auth/login'
    data = request.get_data()
    headers = {"Content-Type": "application/json"}
    response = requests.post(url, data=data, headers=headers)
    return response.text

@APP.route('/auth/logout', methods=['POST'])
def logout_labfolder():
    '''
    Kills the Session associated to the provided token
    '''
    url = CONFIGPARAMS["labFolderBaseURL"] + '/auth/logout'
    headers = {"Content-Type": "application/json",
               "Authorization" :  "Token " + request.headers['Authorization'],
               "User-Agent": CONFIGPARAMS["labFolderDefaultUserAgentHeader"]
              }

    response = requests.post(url, headers=headers)
    return response.text

def authenticate_couchdb():
    '''
    Authenticate to CouchDB and return login token
    '''
    url = CONFIGPARAMS["couchDBBaseURL"] + '/_session'
    data = "name=" + CONFIGPARAMS["couchDBAdmin"] + "&password=" + CONFIGPARAMS["couchDBPassword"]
    # data =  {"name":  CONFIGPARAMS["couchDBAdmin"], "password": CONFIGPARAMS["couchDBPassword"]}
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    response = requests.post(url, data=data, headers=headers)
    if response.status_code == 200:
        if DEBUG:
            print("Succesfully Authenticated, extracting Cookie!")
        cookie = response.headers["Set-Cookie"]
        couchdb_token = cookie[:cookie.find(";")]
        return couchdb_token
    if DEBUG:
        print("Error logging into couchDB. Wrong Username or Password!")
        print(response.text)
    return False

#----------------------Projects------------------------------------------------

@APP.route('/projects', methods=['GET'])
def get_projects():
    '''
    Accesses LabFolder by Token and retreives the Projects from User. Answer is returned by REST.
    '''
    url = CONFIGPARAMS["labFolderBaseURL"] + '/projects?'
    mod = 0
    #process optional parameters and add them to url if required
    group_id = request.args.get('group_id', default='', type=str)
    if group_id != '':
        mod = 1
        url = url + 'group_id=' + group_id + '&'
    owner_id = request.args.get('owner_id', default='', type=str)
    if owner_id != '':
        mod = 1
        url = url + 'owner_id=' + owner_id + '&'
    only_root_level = request.args.get('only_root_level', default=0, type=int)
    if only_root_level:
        mod = 1
        url = url + 'only_root_level=true&'
    folder_id = request.args.get('folder_id', default='', type=str)
    if folder_id != '':
        mod = 1
        url = url + 'folder_id=' + folder_id + '&'
    projects_ids = request.args.get('projects_ids', default='', type=str)
    if projects_ids != '':
        mod = 1
        url = url + 'projects_ids=' + projects_ids + '&'
    limit = request.args.get('limit', default=20, type=int)
    if limit != 20:
        mod = 1
        url = url + 'limit=' + str(limit) + '&'
    offset = request.args.get('offset', default=0, type=int)
    if offset != 0:
        mod = 1
        url = url + 'offset=' + str(offset) + '&'
    #remove '?' from url when no parameter has been added - basically just reset it to default
    if mod == 0:
        url = url.rstrip('?')
    else:
        url = url.rstrip('&')
    #prepare header
    headers = {"Content-Type": "application/json",
               "Authorization" :  "Token " + request.headers['Authorization'],
               "User-Agent": CONFIGPARAMS["labFolderDefaultUserAgentHeader"]
              }
    response = requests.get(url, headers=headers)
    return response.text

#-------------------Notebook---------------------------------------------------

@APP.route('/entries', methods=['GET'])
def get_notebook_entries():
    '''
    Accesses LabFolder by Token and retreives the Entries from User. Answer is returned by REST.
    '''
    url = CONFIGPARAMS["labFolderBaseURL"] + '/entries?'
    mod = 0
    #process optional parameters and add them to url if required <- !!!currently not yet tested!!!
    sort = request.args.get('sort', default='', type=str)
    if sort != '':
        mod = 1
        url = url + 'sort=' + sort + '&'
    omni_empty_title = request.args.get('omni_empty_title', default=0, type=int)
    if omni_empty_title:
        mod = 1
        url = url + 'omni_empty_title=true&'
    title = request.args.get('title', default='', type=str)
    if title != '':
        mod = 1
        url = url + 'title=' + title + '&'
    limit = request.args.get('limit', default=20, type=int)
    if limit != 20:
        mod = 1
        url = url + 'limit=' + str(limit) + '&'
    offset = request.args.get('offset', default=0, type=int)
    if offset != 0:
        mod = 1
        url = url + 'offset=' + str(offset) + '&'
    expand = request.args.get('expand', default='', type=str)
    if expand != '':
        mod = 1
        url = url + 'expand=' + expand + '&'
    #remove '?' from url when no parameter has been added - basically just reset it to default
    if mod == 0:
        url = url.rstrip('?')
    else:
        url = url.rstrip('&')
    #prepare header
    headers = {"Content-Type": "application/json",
               "Authorization" :  "Token " + request.headers['Authorization'],
               "User-Agent": CONFIGPARAMS["labFolderDefaultUserAgentHeader"]
              }
    response = requests.get(url, headers=headers)
    return response.text

@APP.route('/download', methods=['GET'])
def download_file_to_client():
    '''
    Creates a zip File with the Entry requested by the user, and transfers the zip by HTTP.
    '''
    download_meta = {"user_id" : DEVUSER_ID,
                     "projectID" : request.args.get('project_id', default='', type=str),
                     "entryID" : request.args.get('entry_id', default='', type=str),
                     "entryVersionID" : request.args.get('entry_version_id', default='', type=str)
                    }
    # elementID = request.args.get('element_id', default = '', type = str)
    # versionID = request.args.get('version_id', default = '', type = str)
    filename = download_meta["user_id"] + "-" + time.strftime("%d-%m-%Y") + "-" \
               + time.strftime("%H:%M:%S") + ".zip"
    if download_meta["user_id"] != '' and download_meta["projectID"] != '' and \
       download_meta["entryID"] != '' and download_meta["entryVersionID"] != '':
        createZipFileFromFiles(download_meta, CONFIGPARAMS["tempFolder"] + filename)
    else:
        return APP.response_class(json.dumps({'Error' : 'Missing Parameter id'}),
                                  status=200, mimetype='application/json')
    try:
        return send_from_directory(CONFIGPARAMS["tempFolder"], filename, as_attachment=True)
    except Exception as e:
        print(e)
        return APP.response_class(json.dumps({'Error' : 'Internal Error'}),
                                  status=400, mimetype='application/json')

@APP.route('/elements/download', methods=['POST'])
def download():
    '''
    Routed from /elements/download.
    Manages the download of the requests data provided in REST Request.
    '''
    #we also need to verify the loged in ldap user here
    #data should contain a json object with structure:
    #{
    #       elementType: [IMAGE,TABLE,TEXT],
    #       elementID: elementID
    #}
    user_id = DEVUSER_ID
    data = request.get_data()
    json_data = json.loads(data)
    json_data = remove_already_existing_tupel(user_id, json_data)
    download_file_from_labfolder(json_data)
    if len(json_data) > 0:
        update_storage_file(user_id, json_data)
    return APP.response_class(status=200, mimetype='application/json')

#@APP.route('/elements/file' , methods=['GET'])
def download_file_from_labfolder(data_array):
    '''
    Function is called for File Download from LabFolder. This Function downloads the files and
    stored it in the database.
    '''
    if DEBUG:
        print("-----in download_file_from_labfolder-----")
    token = authenticate_couchdb()
    if not token:
        if DEBUG:
            print("Auth to couchDB not successfull. Returning")
        return
    for element in data_array:
        if element["elementType"] == 'IMAGE':
            url = CONFIGPARAMS["labFolderBaseURL"] + '/elements/file/'
            file_info_url = url + element["elementID"]
            file_url = file_info_url + '/download'
        elif element["elementType"] == 'TABLE':
            url = CONFIGPARAMS["labFolderBaseURL"] + '/elements/table/'
            file_url = url + element["elementID"]
        elif element["elementType"] == 'TEXT':
            url = CONFIGPARAMS["labFolderBaseURL"] + '/elements/text/'
            file_url = url + element["elementID"]
        else:
            return
        headers = {"Content-Type": "application/json",
                   "Authorization" :  "Token " + request.headers['Authorization'],
                   "User-Agent": CONFIGPARAMS["labFolderDefaultUserAgentHeader"]
                  }
        couch_header = {"Accept": "application/json",
                        "Content-Type" : "application/json",
                        "Cookie" :  token}
        file_response = requests.get(file_url, headers=headers)
        couchdb_url = CONFIGPARAMS["couchDBBaseURL"] + "/" + \
                      CONFIGPARAMS["couchDBDocumentDatabaseName"]
        cdbdata = {}
        new_doc_response = requests.post(couchdb_url, headers=couch_header,
                                         data=json.dumps(cdbdata))
        json_answer = json.loads(new_doc_response.text)
        new_rev = json_answer["rev"]
        couch_header["If-Match"] = new_rev
        couch_id = json_answer["id"]
        element["couchdb_doc_id"] = couch_id
        couchdb_url = couchdb_url + "/" + couch_id + "/"
        filename = ''
        if DEBUG:
            print("New couch Document created with ID " + couch_id)
        if element["elementType"] == 'IMAGE':
            file_info_response = requests.get(file_info_url, headers=headers)
            file_info_reponse_jdata = json.loads(file_info_response.text)
            filename = file_info_reponse_jdata["file_name"]
            file_data = file_response.content
            couchdb_url = couchdb_url + filename
            couch_header["Content-Type"] = "image/png"
            att_create_response = requests.put(couchdb_url, headers=couch_header, data=file_data)
            if att_create_response.status_code == 201 or att_create_response.status_code == 202:
                if DEBUG:
                    print("Succesfully stored image " + filename + " in database")
            else:
                if DEBUG:
                    print("Error Storing image file in DB: " + att_create_response.text)
                # if DEBUG:
                #     print("---trying to write image file"))
                # file = open(storageURL + filename, "wb")
                # file.write(file_data)
        elif element["elementType"] == 'TABLE':
            # file_response = requests.get(file_url, headers=headers)
            if DEBUG:
                print("---trying to write table file")
            file_info_reponse_jdata = json.loads(file_response.text)
            title = file_info_reponse_jdata["title"]
            content = file_info_reponse_jdata["content"]
            sheets = content["sheets"]
            # print(sheets))
            file_data = ""
            for sheet_key in sheets:
                try:
                    data = sheets[sheet_key]["data"]["dataTable"]
                except:
                    if DEBUG:
                        print("no data in sheet " + sheet_key)
                    continue
                sheet_name = sheets[sheet_key]["name"]
                file_data = file_data + sheet_name + "\n"
                for line in data:
                    for row in data[line]:
                        append = data[line][row]["value"]
                        if type(append) is int:
                            append = str(append)
                        file_data = file_data + append + ","
                    file_data = file_data.rstrip(",")
                    file_data = file_data + "\n"
            filename = title
            couchdb_url = couchdb_url + filename
            couch_header["Content-Type"] = "text/plain"
            att_create_response = requests.put(couchdb_url, headers=couch_header, data=file_data)
            if att_create_response.status_code == 201 or att_create_response.status_code == 202:
                if DEBUG:
                    print("Succesfully stored table " + title + "-" + sheet_name + " in database")
            else:
                if DEBUG:
                    print("Error Storing table file in DB: " + att_create_response.text)
        elif element["elementType"] == 'TEXT':
            if DEBUG:
                print("---trying to write text file")
            # file_response = requests.get(file_url, headers=headers)
            file_info_reponse_jdata = json.loads(file_response.text)
            file_data = file_info_reponse_jdata["content"]
            filename = couch_id
            couchdb_url = couchdb_url + filename
            couch_header["Content-Type"] = "text/plain"
            att_create_response = requests.put(couchdb_url, headers=couch_header, data=file_data)
            if att_create_response.status_code == 201 or att_create_response.status_code == 202:
                if DEBUG:
                    print("Succesfully stored text file in database")
            else:
                if DEBUG:
                    print("Error " + str(att_create_response.status_code) + \
                          " Storing text file in DB: " + att_create_response.text)
        element["couchdb_doc_item_att_name"] = filename

@APP.route('/mdb/categories', methods=['GET'])
def get_mdb_categories():
    '''
    Routed from /mdb/categories.
    Retreives the category information about Material Databse from labfolder and returns this.
    '''
    url = CONFIGPARAMS["labFolderBaseURL"] + '/mdb/categories'
    #prepare header
    headers = {"Content-Type": "application/json",
               "Authorization" :  "Token " + request.headers['Authorization'],
               "User-Agent": CONFIGPARAMS["labFolderDefaultUserAgentHeader"]
              }
    if DEBUG:
        print(url)
    response = requests.get(url, headers=headers)
    return response.text

#TODO store downloaded files in another location (not on server storage) -> maybe direct dl?
#----does only support filtering by category_id----
@APP.route('/mdb/items', methods=['GET'])
def download_mdb_items():
    '''
    routed from /mdb/items
    Download the Material Database Items to Server.
    '''
    url_items = CONFIGPARAMS["labFolderBaseURL"] + '/mdb/items'
    url_categories = CONFIGPARAMS["labFolderBaseURL"] + '/mdb/categories'
    category_id = request.args.get('category_id', default='', type=str)
    if category_id == '':
        return APP.response_class(json.dumps({'Error' : 'Missing Parameter id'}),
                                  status=400,
                                  mimetype='application/json')
    url_items = url_items + '?category_id=' + category_id
    url_categories = url_categories + '/' + category_id
    #prepare header
    headers = {"Content-Type": "application/json",
               "Authorization" :  "Token " + request.headers['Authorization'],
               "User-Agent": CONFIGPARAMS["labFolderDefaultUserAgentHeader"]
              }
    if DEBUG:
        print(url_items)
        print(url_categories)
    response_categories = requests.get(url_categories, headers=headers)
    response_items = requests.get(url_items, headers=headers)
    if DEBUG:
        print(response_categories.text)
        print(response_items.text)
    #now we preprocess the answer to a csv
    category_response_jdata = json.loads(response_categories.text)
    item_response_jdata = json.loads(response_items.text)
    attributes = category_response_jdata["attributes"]
    attributes_sorted = sorted(attributes, key=lambda x: x["display_order"])
    title = category_response_jdata["title"]
    file_data = "Name, "
    for att in attributes_sorted:
        file_data = file_data + att["title"] + ","
    file_data.rstrip(",")
    file_data = file_data + "\n"
    if DEBUG:
        print("After headline")
        print(file_data)
    for item in item_response_jdata:
        file_data = file_data + item["title"] + ","
        for satt in attributes_sorted:
            #write the content of the sorted attribute field. identified by the id of the attribute
            file_data = file_data + item["custom_attributes"][satt["id"]] + ","
        file_data.rstrip(",")
        file_data = file_data + "\n"
    if DEBUG:
        print("After Content")
        print(file_data)
    file = open(title + ".csv", "w")
    file.write(file_data)
    file.close
    return json.dumps({'Result' : 'All good'}), 200, {'Content-Type' : 'application/json'}

@APP.route('/storage', methods=['GET'])
def getstorage_file():
    '''
    Routed from /storage
    Requests the storage file, containg metadata about stored files for the requesting user
    '''
    user_id = DEVUSER_ID
    return get_datastructure(user_id, return_as_string=True)


def get_datastructure(user_id, return_as_string=False):
    '''
    Returns the storage file for @user_id either as (json)string or object.
    '''
    if DEBUG:
        print("in get_datastructure")
    url = CONFIGPARAMS["couchDBBaseURL"] + "/" + CONFIGPARAMS["couchDBStorageDatabaseName"] + "/" +\
          user_id
    token = authenticate_couchdb()
    if token == False:
        if DEBUG:
            print("Auth to couchDB not successfull. Returning")
        return
    headers = {"Accept": "application/json", "Content-Type" : "application/json", "Cookie" :  token}
    if DEBUG:
        print("trying to get database for user with url: " + url)
        print(headers)
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        # if DEBUG:
        #     print("got answer, returning: " + response.text)
        if return_as_string:
            return response.text
        else:
            return json.loads(response.text)
    elif response.status_code == 404:
        if DEBUG:
            print("404, creating new document in db")
        initialData = {"user" : user_id, "projects": []}
        if DEBUG:
            print("initial_data: " + json.dumps(initialData))
        new_response = requests.put(url, headers=headers, data=json.dumps(initialData))
        if DEBUG:
            print(new_response.text)
        # new_response.raise_for_status()
        if return_as_string:
            return initialData
        else:
            return json.loads(initialData)

#updates the storage File with the added files
def update_storage_file(user_id, addElements):
    '''
    updated the storage file for @user_id with new Elements @addElements. Integrity is checked, so
    heritage is correctly considered.
    '''
    if DEBUG:
        print("---in updatestorage_file---")
        print("writing " + str(len(addElements)) + " items in file")
    storage_file = get_datastructure(user_id)
    # if DEBUG:
    #       print("storage file before process")
    #       print(json.dumps(storage_file))
    for item in addElements:
        if not [x for x in storage_file["projects"] if x["projectID"] == item["projectID"]]:
            storage_file["projects"].append({
                "projectID" : item["projectID"],
                "projectTitle" : item["projectTitle"],
                "entries" : [{
                    "entryID" : item["entryID"],
                    "entryTitle" : item["entryTitle"],
                    "versions" : [{
                        "versionID" : item["entryVersionID"],
                        "versionDate" : item["versionDate"],
                        "elements" : [{
                            "elementID" : item["elementID"],
                            "elementType" : item["elementType"],
                            "versions" : [{
                                "versionID" : item["versionID"],
                                "couchdb_doc_id" : item["couchdb_doc_id"],
                                "couchdb_doc_item_att_name" : item["couchdb_doc_item_att_name"]
                            }]
                        }]
                    }]
                }]
            })
        else:
            for proj in storage_file["projects"]:
                if proj["projectID"] == item["projectID"]:
                    if not [x for x in proj["entries"] if x["entryID"] == item["entryID"]]:
                        proj["entries"].append({
                            "entryID" : item["entryID"],
                            "entryTitle" : item["entryTitle"],
                            "versions" : [{
                                "versionID" : item["entryVersionID"],
                                "versionDate" : item["versionDate"],
                                "elements" : [{
                                    "elementID" : item["elementID"],
                                    "elementType" : item["elementType"],
                                    "versions" : [{
                                        "versionID" : item["versionID"],
                                        "couchdb_doc_id" : item["couchdb_doc_id"],
                                        "couchdb_doc_item_att_name" : \
                                            item["couchdb_doc_item_att_name"]
                                    }]
                                }]
                            }]
                        })
                        break
                    else:
                        for entry in proj["entries"]:
                            if entry["entryID"] == item["entryID"]:
                                if not [x for x in entry["versions"] if x["versionID"] \
                                        == item["entryVersionID"]]:
                                    entry["versions"].append({
                                        "versionID" : item["entryVersionID"],
                                        "versionDate" : item["versionDate"],
                                        "elements" : [{
                                            "elementID" : item["elementID"],
                                            "elementType" : item["elementType"],
                                            "versions" : [{
                                                "versionID" : item["versionID"],
                                                "couchdb_doc_id" : item["couchdb_doc_id"],
                                                "couchdb_doc_item_att_name" : \
                                                    item["couchdb_doc_item_att_name"]
                                            }]
                                        }]
                                    })
                                    break
                                else:
                                    for version in entry["versions"]:
                                        if version["versionID"] == item["entryVersionID"]:
                                            if not [x for x in version["elements"] if x["elementID"] == item["elementID"]]:
                                                version["elements"].append({
                                                    "elementID" : item["elementID"],
                                                    "elementType" : item["elementType"],
                                                    "versions" : [{
                                                        "versionID" : item["versionID"],
                                                        "couchdb_doc_id" : item["couchdb_doc_id"],
                                                        "couchdb_doc_item_att_name" :\
                                                            item["couchdb_doc_item_att_name"]
                                                    }]
                                                })
                                                break
                                            else:
                                                for element in version["elements"]:
                                                    if element["elementID"] == item["elementID"]:
                                                        element["versions"].append({
                                                            "versionID" : item["versionID"],
                                                            "couchdb_doc_id" : \
                                                                item["couchdb_doc_id"],
                                                            "couchdb_doc_item_att_name" : \
                                                                item["couchdb_doc_item_att_name"]
                                                        })
                                                        break

    url = CONFIGPARAMS["couchDBBaseURL"] + "/" + CONFIGPARAMS["couchDBStorageDatabaseName"] + \
          "/" + user_id
    token = authenticate_couchdb()
    if not token:
        return
    headers = {"Accept": "application/json", "Content-Type" : "application/json", "Cookie" :  token}
    response = requests.put(url, headers=headers, data=json.dumps(storage_file))
    if response.status_code == 201 or response.status_code == 202:
        if DEBUG:
            print("Succesfully stored storage file")
    else:
        if DEBUG:
            print("error storing storage file")

#checks if elements to download already exist in storage file. pops elements which are already
# existing of the checkArray
#check_elements is a list of dicts: (projectID: str, entryID: str, elementID: str, versionID: str)
def remove_already_existing_tupel(user_id, check_elements):
    '''
    Checks if in storage file of @user_id there are already files which are identical to
    @check_elements. @check_elements is stripped of already existing entries and returned.
    '''
    storage_file = get_datastructure(user_id)
    if DEBUG:
        print(json.dumps(storage_file))
    output = []
    for item in check_elements:
        new_item = True
        project_id = item["projectID"]
        entry_id = item["entryID"]
        entry_version_id = item["entryVersionID"]
        element_id = item["elementID"]
        version_id = item["versionID"]
        if DEBUG:
            print("Project ID: " + project_id)
            print("entry   ID: " + entry_id)
            print("entryVersionID: " + entry_version_id)
            print("elementID: " + element_id)
            print("versionID: " + version_id)
        if storage_file["projects"] is None:
            return check_elements
        if not storage_file["projects"]:
            return check_elements
        for proj_val in storage_file["projects"]:
            if proj_val["projectID"] == project_id:
                for entry_val in proj_val["entries"]:
                    if entry_val["entryID"] == entry_id:
                        for entry_version_val in entry_val["versions"]:
                            if entry_version_val["versionID"] == entry_version_id:
                                for element_val in entry_version_val["elements"]:
                                    if element_val["elementID"] == element_id:
                                        for version_val in element_val["versions"]:
                                            if version_val["versionID"] == version_id:
                                                new_item = False
                                                break
                                        break
                                break
                        break
                break
        if new_item:
            output.append(item)
    if DEBUG:
        print("output length: " + str(len(output)))
    return output

def createZipFileFromFiles(download_meta, filename):
    '''
    create zip file with name @filenmane for requested files in @download_meta.
    '''
    zip_file = ZipFile(filename, 'w')
    cdb_doc_url_base = CONFIGPARAMS["couchDBBaseURL"] + "/" + \
                       CONFIGPARAMS["couchDBDocumentDatabaseName"] + "/"
    storage_file = get_datastructure(download_meta["user_id"])
    proj = [x for x in storage_file["projects"] if x["projectID"] == download_meta["projectID"]][0]
    entry = [y for y in proj["entries"] if y["entryID"] == download_meta["entryID"]][0]
    entry_version = [z for z in entry["versions"] \
        if z["versionID"] == download_meta["entryVersionID"]][0]
    for ele in entry_version["elements"]:
        filename = ele["versions"][0]["couchdb_doc_item_att_name"]
        #each element should only have one version, so wen access the first element
        cdb_doc_url = cdb_doc_url_base + ele["versions"][0]["couchdb_doc_id"] + "/" \
        + filename
        tmp_path_file = Path(CONFIGPARAMS["tempFolder"] + ele["elementID"])
        token = authenticate_couchdb()
        if not token:
            return
        headers = {"Accept": "application/json",
                   "Content-Type" : "application/json",
                   "Cookie" :  token
                  }
        response = requests.get(cdb_doc_url, headers=headers)
        if response:
            if ele["elementType"] == "TEXT" or ele["elementType"] == "TABLE":
                tmp_path_file.write_text(response.text)
            elif ele["elementType"] == "IMAGE":
                tmp_path_file.write_bytes(response.content)
            absname = str(tmp_path_file.resolve())
            if DEBUG:
                print("writing in zip file")
            zip_file.write(absname, arcname=filename)
            if DEBUG:
                print("finished writing in zip file")
                print("removing file")
            try:
                tmp_path_file.unlink()
            except FileNotFoundError:
                print("Error deleting file from filesystem: File not Found")
    zip_file.close()
    # return zf



if __name__ == '__main__':
    #authenticate_couchdb()
    APP.run(debug=True)

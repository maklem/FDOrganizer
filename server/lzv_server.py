"""
Software for LZV Server.
"""
import time
from pathlib import Path
from zipfile import ZipFile
import json
import secrets
import requests

# from flask import Flask, session
from flask import Flask, request, render_template, send_from_directory, session
from flask_session import Session
from flask_cors import CORS

import ldap
# from flask import send_from_directory
# from flask import render_template
# from flask import Response
# from flask import make_response
# from flask import send_file
# from flask import *
# from zipfile import *

DEBUG = 1

#----------------------global Parameters-------------------------------------------

CONFIGPARAMS = {}
FAILED_AUTHENTICATION = 'Failed Authentication, please login to use this service!'


#----------------------initialization------------------------------------------

APP = Flask(__name__)
with open('/server/lzv/server/conf/config.json') as f:
    CONFIGPARAMS = json.load(f)
APP.secret_key = 'any random string'
APP.config['SESSION_TYPE'] = 'filesystem'
APP.config['PERMANENT_SESSION_LIFETIME'] = 43200
APP.config['SESSION_PERMANENT'] = False
CORS(APP)
Session(APP)


#----------------------Page Navigation-----------------------------------------
@APP.route('/')
def navhome():
    '''
    Navigation to site Home
    '''
    if not 'session_user' in request.cookies or not 'session_auth' in request.cookies:
        return render_template("login.html")
    if not check_session(request.cookies['session_user'], request.cookies['session_auth']):
        return render_template("login.html")
    return render_template("index.html")

@APP.route('/impressum')
def navimpressum():
    '''
    Navigation to site Impressum
    '''
    if not 'session_user' in request.cookies or not 'session_auth' in request.cookies:
        return render_template("login.html")
    if not check_session(request.cookies['session_user'], request.cookies['session_auth']):
        return render_template("login.html")
    return render_template("impressum.html")

@APP.route('/history')
def navhistory():
    '''
    Navigation to site History
    '''
    if not 'session_user' in request.cookies or not 'session_auth' in request.cookies:
        return render_template("login.html")
    if not check_session(request.cookies['session_user'], request.cookies['session_auth']):
        return render_template("login.html")
    return render_template("history.html")

@APP.route('/labfolder')
def navlabfolder():
    '''
    Navigation to site Labfolder
    '''
    if not 'session_user' in request.cookies or not 'session_auth' in request.cookies:
        return render_template("login.html")
    if not check_session(request.cookies['session_user'], request.cookies['session_auth']):
        return render_template("login.html")
    return render_template("labfolder.html")

@APP.route('/easydb')
def naveasydb():
    '''
    Navigation to site easyDB
    '''
    if not 'session_user' in request.cookies or not 'session_auth' in request.cookies:
        return render_template("login.html")
    if not check_session(request.cookies['session_user'], request.cookies['session_auth']):
        return render_template("login.html")
    return render_template("easydb.html")

@APP.route('/metadata')
def navmetadata():
    '''
    Navigation to site metadata
    '''
    if not 'session_user' in request.cookies or not 'session_auth' in request.cookies:
        return render_template("login.html")
    if not check_session(request.cookies['session_user'], request.cookies['session_auth']):
        return render_template("login.html")
    return render_template("metadata.html")

@APP.route('/lzv')
def navlzvingest():
    '''
    Navigation to site metadata
    '''
    if not 'session_user' in request.cookies or not 'session_auth' in request.cookies:
        return render_template("login.html")
    if not check_session(request.cookies['session_user'], request.cookies['session_auth']):
        return render_template("login.html")
    return render_template("lzvingest.html")

@APP.route('/login', methods=['GET'])
def navlogin():
    '''
    Navigation to login site
    '''
    return render_template("login.html")


#----------------------Authenticate LDAP --------------------------------------
def authenticate_ldap(uname, pword):
    '''
        Authenticate against LDAP Server, return true if uname,pword is correct, false else
    '''
    ldap_server = "ldaps://proxy-ubtrz.uni-bayreuth.de:636"
    ldap_base = "ou=users,ou=rz-ad,o=uni-bayreuth"
    user_dn = "cn="+uname+","+ldap_base
    try:
        connect = ldap.initialize(ldap_server)
        connect.bind_s(user_dn, pword)
        connect.unbind_s()
        return True
    except ldap.LDAPError:
        connect.unbind_s()
        return False

def create_sessionid():
    '''
        Creates a cryptographically-secure, URL-safe string
    '''
    return secrets.token_urlsafe(64)

def create_user_session(userid):
    '''
        create new session for user. check if correct credentials to ad if true, create new session
    '''
    session[userid] = create_sessionid()
def check_session(userid, sessionid):
    '''
        check if provided session id is valid
    '''
    return session.get(userid) == sessionid

def get_sessionid(userid):
    '''
    return the session id for userid
    '''
    return session.get(userid)

def logout_session(userid):
    '''
        deletes the session object for user userid
    '''
    session.pop(userid)

@APP.route('/login', methods=['POST'])
def login_lzv():
    '''
    Login to lzv site. Performs a lookup to ldap server to verify credentials.
    Returns a session token to user, to authenticate your session against.
    '''
    if 'session_user' in request.cookies and 'session_auth' in request.cookies:
        if check_session(request.cookies['session_user'], request.cookies['session_auth']):
            return json.dumps({'session_id' : request.cookies['session_auth'], 
                               'username' : request.cookies['session_user']}), \
                               200, \
                               {'Content-Type' : 'application/json'} 
    data = json.loads(request.get_data())
    if authenticate_ldap(data['username'], data['password']):
        create_user_session(data['username'])
        return json.dumps({'session_id' : get_sessionid(data['username']), \
               'username' : data['username']}), 200, {'Content-Type' : 'application/json'}
    return {'Error' : 'invalid credentials'}, 401, {'Content-Type' : 'application/json'}

@APP.route('/logout', methods=['POST'])
def logout_lzv():
    '''
    Logout User from lzv System. Deletes local stored session id.
    '''
    if not 'session_user' in request.cookies or not 'session_auth' in request.cookies:
        return {'Error' : FAILED_AUTHENTICATION}, 401, {'Content-Type' : 'application/json'}
    if not check_session(request.cookies['session_user'], request.cookies['session_auth']):
        return {'Error' : FAILED_AUTHENTICATION}, 401, {'Content-Type' : 'application/json'}
    logout_session(request.cookies['session_user'])
    return json.dumps({'Message': 'All good!'}), 200, {'Content-Type' : 'application/json'}


#----------------------Authentification LabFolder------------------------------
@APP.route('/labfolder/auth/login', methods=['POST'])
def authenticate_labfolder():
    '''
    Authenticate to LabFolder and returns the login answer
    '''
    if not 'session_user' in request.cookies or not 'session_auth' in request.cookies:
        return {'Error' : FAILED_AUTHENTICATION}, 401, {'Content-Type' : 'application/json'}
    if not check_session(request.cookies['session_user'], request.cookies['session_auth']):
        return {'Error' : FAILED_AUTHENTICATION}, 401, {'Content-Type' : 'application/json'}
    url = CONFIGPARAMS["labFolderBaseURL"] + '/auth/login'
    data = request.get_data()
    headers = {"Content-Type": "application/json"}
    response = requests.post(url, data=data, headers=headers)
    return response.text

@APP.route('/labfolder/auth/logout', methods=['POST'])
def logout_labfolder():
    '''
    Kills the Session associated to the provided token
    '''
    if not 'session_user' in request.cookies or not 'session_auth' in request.cookies:
        return {'Error' : FAILED_AUTHENTICATION}, 401, {'Content-Type' : 'application/json'}
    if not check_session(request.cookies['session_user'], request.cookies['session_auth']):
        return {'Error' : FAILED_AUTHENTICATION}, 401, {'Content-Type' : 'application/json'}
    url = CONFIGPARAMS["labFolderBaseURL"] + '/auth/logout'
    headers = {"Content-Type": "application/json",
               "Authorization" :  "Token " + request.headers['Token'],
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

@APP.route('/labfolder/projects', methods=['GET'])
def get_projects():
    '''
    Accesses LabFolder by Token and retreives the Projects from User. Answer is returned by REST.
    '''
    if not 'session_user' in request.cookies or not 'session_auth' in request.cookies:
        return {'Error' : FAILED_AUTHENTICATION}, 401, {'Content-Type' : 'application/json'}
    if not check_session(request.cookies['session_user'], request.cookies['session_auth']):
        return {'Error' : FAILED_AUTHENTICATION}, 401, {'Content-Type' : 'application/json'}
    url = CONFIGPARAMS["labFolderBaseURL"] + '/projects'
    #process optional parameters and add them to url if required
    # mod = 0
    # group_id = request.args.get('group_id', default='', type=str)
    # if group_id != '':
    #     mod = 1
    #     url = url + 'group_id=' + group_id + '&'
    # owner_id = request.args.get('owner_id', default='', type=str)
    # if owner_id != '':
    #     mod = 1
    #     url = url + 'owner_id=' + owner_id + '&'
    # only_root_level = request.args.get('only_root_level', default=0, type=int)
    # if only_root_level:
    #     mod = 1
    #     url = url + 'only_root_level=true&'
    # folder_id = request.args.get('folder_id', default='', type=str)
    # if folder_id != '':
    #     mod = 1
    #     url = url + 'folder_id=' + folder_id + '&'
    # projects_ids = request.args.get('projects_ids', default='', type=str)
    # if projects_ids != '':
    #     mod = 1
    #     url = url + 'projects_ids=' + projects_ids + '&'
    # limit = request.args.get('limit', default=20, type=int)
    # if limit != 20:
    #     mod = 1
    #     url = url + 'limit=' + str(limit) + '&'
    # offset = request.args.get('offset', default=0, type=int)
    # if offset != 0:
    #     mod = 1
    #     url = url + 'offset=' + str(offset) + '&'
    # #remove '?' from url when no parameter has been added - basically just reset it to default
    # if mod == 0:
    #     url = url.rstrip('?')
    # else:
    #     url = url.rstrip('&')
    #prepare header
    headers = {"Content-Type": "application/json",
               "Authorization" :  "Token " + request.headers['Token'],
               "User-Agent": CONFIGPARAMS["labFolderDefaultUserAgentHeader"]
              }
    response = requests.get(url, headers=headers)
    return response.text

#-------------------Notebook---------------------------------------------------

@APP.route('/labfolder/entries', methods=['GET'])
def get_notebook_entries():
    '''
    Accesses LabFolder by Token and retreives the Entries from User. Answer is returned by REST.
    '''
    if not 'session_user' in request.cookies or not 'session_auth' in request.cookies:
        return {'Error' : FAILED_AUTHENTICATION}, 401, {'Content-Type' : 'application/json'}
    if not check_session(request.cookies['session_user'], request.cookies['session_auth']):
        return {'Error' : FAILED_AUTHENTICATION}, 401, {'Content-Type' : 'application/json'}
    url = CONFIGPARAMS["labFolderBaseURL"] + '/entries'
    #process optional parameters and add them to url if required <- !!!currently not yet tested!!!
    # mod = 0
    # sort = request.args.get('sort', default='', type=str)
    # if sort != '':
    #     mod = 1
    #     url = url + 'sort=' + sort + '&'
    # omni_empty_title = request.args.get('omni_empty_title', default=0, type=int)
    # if omni_empty_title:
    #     mod = 1
    #     url = url + 'omni_empty_title=true&'
    # title = request.args.get('title', default='', type=str)
    # if title != '':
    #     mod = 1
    #     url = url + 'title=' + title + '&'
    # limit = request.args.get('limit', default=20, type=int)
    # if limit != 20:
    #     mod = 1
    #     url = url + 'limit=' + str(limit) + '&'
    # offset = request.args.get('offset', default=0, type=int)
    # if offset != 0:
    #     mod = 1
    #     url = url + 'offset=' + str(offset) + '&'
    # expand = request.args.get('expand', default='', type=str)
    # if expand != '':
    #     mod = 1
    #     url = url + 'expand=' + expand + '&'
    # #remove '?' from url when no parameter has been added - basically just reset it to default
    # if mod == 0:
    #     url = url.rstrip('?')
    # else:
    #     url = url.rstrip('&')
    #prepare header
    headers = {"Content-Type": "application/json",
               "Authorization" :  "Token " + request.headers['Token'],
               "User-Agent": CONFIGPARAMS["labFolderDefaultUserAgentHeader"]
              }
    response = requests.get(url, headers=headers)
    return response.text

@APP.route('/labfolder/download', methods=['GET'])
def download_file_to_client():
    '''
    Creates a zip File with the Entry requested by the user, and transfers the zip by HTTP.
    '''
    if not 'session_user' in request.cookies or not 'session_auth' in request.cookies:
        return {'Error' : FAILED_AUTHENTICATION}, 401, {'Content-Type' : 'application/json'}
    if not check_session(request.cookies['session_user'], request.cookies['session_auth']):
        return {'Error' : FAILED_AUTHENTICATION}, 401, {'Content-Type' : 'application/json'}
    download_meta = {"user_id" : request.cookies['session_user'],
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
        create_zip_from_files(download_meta, CONFIGPARAMS["tempFolder"] + filename)
    else:
        return APP.response_class(json.dumps({'Error' : 'Missing Parameter id'}),
                                  status=200, mimetype='application/json')
    return send_from_directory(CONFIGPARAMS["tempFolder"], filename, as_attachment=True)

@APP.route('/labfolder/elements/download', methods=['POST'])
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
    if not 'session_user' in request.cookies or not 'session_auth' in request.cookies:
        return {'Error' : FAILED_AUTHENTICATION}, 401, {'Content-Type' : 'application/json'}
    if not check_session(request.cookies['session_user'], request.cookies['session_auth']):
        return {'Error' : FAILED_AUTHENTICATION}, 401, {'Content-Type' : 'application/json'}
    user_id = request.cookies['session_user']
    data = request.get_data()
    json_data = json.loads(data)
    json_data = remove_already_existing_tupel(user_id, json_data)
    download_file_from_labfolder(json_data)
    if json_data:
        update_storage_file(user_id, json_data)
    return APP.response_class(status=200, mimetype='application/json')

#@APP.route('/elements/file' , methods=['GET'])
def download_file_from_labfolder(data_array):
    '''
    Function is called for File Download from LabFolder. This Function downloads the files and
    stored it in the database.
    '''
    token = authenticate_couchdb()
    if not token:
        return
    for element in data_array:
        if element["elementType"] == 'IMAGE':
            file_info_url = CONFIGPARAMS["labFolderBaseURL"] \
                            + '/elements/file/' + element["elementID"]
            file_url = file_info_url + '/download'
        elif element["elementType"] == 'TABLE':
            file_url = CONFIGPARAMS["labFolderBaseURL"] + '/elements/table/' + element["elementID"]
        elif element["elementType"] == 'TEXT':
            file_url = CONFIGPARAMS["labFolderBaseURL"] + '/elements/text/' + element["elementID"]
        else:
            continue
        headers = {"Content-Type": "application/json",
                   "Authorization" :  "Token " + request.headers['Token'],
                   "User-Agent": CONFIGPARAMS["labFolderDefaultUserAgentHeader"]
                  }
        couch_header = {"Accept": "application/json",
                        "Content-Type" : "application/json",
                        "Cookie" :  token}
        file_response = requests.get(file_url, headers=headers)
        couchdb_url = CONFIGPARAMS["couchDBBaseURL"] + "/" + \
                      CONFIGPARAMS["couchDBDocumentDatabaseName"]
        json_answer = json.loads(requests.post(couchdb_url, headers=couch_header,\
                                               data=json.dumps({})).text)
        couch_header["If-Match"] = json_answer["rev"]
        element["couchdb_doc_id"] = json_answer["id"]
        couchdb_url = couchdb_url + "/" + json_answer["id"] + "/"
        file_name = ''
        if element["elementType"] == 'IMAGE':
            file_info_reponse_jdata = json.loads(requests.get(file_info_url, headers=headers).text)
            file_name = file_info_reponse_jdata["file_name"]
            file_data = file_response.content
            couchdb_url = couchdb_url + file_name
            couch_header["Content-Type"] = "image/png"
            att_create_response = requests.put(couchdb_url, headers=couch_header, data=file_data)
            element["successfully_stored"] = bool(att_create_response)
        elif element["elementType"] == 'TABLE' or element["elementType"] == 'TEXT':
            file_data = ''
            file_info_reponse_jdata = json.loads(file_response.text)
            if element["elementType"] == 'TABLE':
                file_name = file_info_reponse_jdata["title"]
                sheets = file_info_reponse_jdata["content"]["sheets"]
                file_data = process_table_data(sheets)
            else: #text
                file_data = file_info_reponse_jdata["content"]
                file_name = json_answer["id"]
            couchdb_url = couchdb_url + file_name
            couch_header["Content-Type"] = "text/plain"
            att_create_response = requests.put(couchdb_url, headers=couch_header, data=file_data)
            element["successfully_stored"] = bool(att_create_response)
        element["couchdb_doc_item_att_name"] = file_name


def process_table_data(sheets):
    '''
        Processes data from sheets to a flat csv string
    '''
    file_data = ''
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


@APP.route('/labfolder/mdb/categories', methods=['GET'])
def get_mdb_categories():
    '''
    Routed from /mdb/categories.
    Retreives the category information about Material Databse from labfolder and returns this.
    '''
    if not 'session_user' in request.cookies or not 'session_auth' in request.cookies:
        return {'Error' : FAILED_AUTHENTICATION}, 401, {'Content-Type' : 'application/json'}
    if not check_session(request.cookies['session_user'], request.cookies['session_auth']):
        return {'Error' : FAILED_AUTHENTICATION}, 401, {'Content-Type' : 'application/json'}
    url = CONFIGPARAMS["labFolderBaseURL"] + '/mdb/categories'
    #prepare header
    headers = {"Content-Type": "application/json",
               "Authorization" :  "Token " + request.headers['Token'],
               "User-Agent": CONFIGPARAMS["labFolderDefaultUserAgentHeader"]
              }
    if DEBUG:
        print(url)
    response = requests.get(url, headers=headers)
    return response.text

#----does only support filtering by category_id----
@APP.route('/labfolder/mdb/items', methods=['GET'])
def download_mdb_items():
    '''
    routed from /mdb/items
    Download the Material Database Items to Server.
    '''
    if not 'session_user' in request.cookies or not 'session_auth' in request.cookies:
        return {'Error' : FAILED_AUTHENTICATION}, 401, {'Content-Type' : 'application/json'}
    if not check_session(request.cookies['session_user'], request.cookies['session_auth']):
        return {'Error' : FAILED_AUTHENTICATION}, 401, {'Content-Type' : 'application/json'}
    url_items = CONFIGPARAMS["labFolderBaseURL"] + '/mdb/items'
    url_categories = CONFIGPARAMS["labFolderBaseURL"] + '/mdb/categories'
    category_id = request.args.get('category_id', default='', type=str)
    token = request.args.get('token', default='', type=str)
    if category_id == '':
        return APP.response_class(json.dumps({'Error' : 'Missing Parameter id'}),
                                  status=400,
                                  mimetype='application/json')
    if token == '':
        return APP.response_class(json.dumps({'Error' : 'Missing Labfolder Token'}),
                                  status=400,
                                  mimetype='application/json')        
    url_items = url_items + '?category_id=' + category_id
    url_categories = url_categories + '/' + category_id
    #prepare header
    headers = {"Content-Type": "application/json",
               "Authorization" :  "Token " + token,
               "User-Agent": CONFIGPARAMS["labFolderDefaultUserAgentHeader"]
              }
    response_categories = requests.get(url_categories, headers=headers)
    response_items = requests.get(url_items, headers=headers)
    #now we preprocess the answer to a csv
    category_response_jdata = json.loads(response_categories.text)
    item_response_jdata = json.loads(response_items.text)
    attributes_sorted = category_response_jdata["attributes"]
    title = category_response_jdata["title"]
    file_data = "Name, "
    for att in attributes_sorted:
        file_data = file_data + att["title"] + ","
    file_data.rstrip(",")
    file_data = file_data + "\n"
    for item in item_response_jdata:
        file_data = file_data + item["title"] + ","
        for satt in attributes_sorted:
            #write the content of the sorted attribute field. identified by the id of the attribute
            file_data = file_data + item["custom_attributes"][satt["id"]] + ","
        file_data.rstrip(",")
        file_data = file_data + "\n"
    filename = title + ".csv"
    filename = filename.replace(">", "_")
    filename = filename.replace(" ", "")
    file = open(CONFIGPARAMS["tempFolder"] + filename, "w")
    file.write(file_data)
    file.close()
    return send_from_directory(CONFIGPARAMS["tempFolder"], filename, as_attachment=True)
    # return json.dumps({'Result' : 'All good'}), 200, {'Content-Type' : 'application/json'}

@APP.route('/labfolder/storage', methods=['GET'])
def get_storage_file():
    '''
    Routed from /storage
    Requests the storage file, containg metadata about stored files for the requesting user
    '''
    if not 'session_user' in request.cookies or not 'session_auth' in request.cookies:
        return {'Error' : FAILED_AUTHENTICATION}, 401, {'Content-Type' : 'application/json'}
    if not check_session(request.cookies['session_user'], request.cookies['session_auth']):
        return {'Error' : FAILED_AUTHENTICATION}, 401, {'Content-Type' : 'application/json'}
    user_id = request.cookies['session_user']
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
    if not token:
        if DEBUG:
            print("Auth to couchDB not successfull. Returning")
        return '' if return_as_string else {}
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
        return json.loads(response.text)
    initial_data = {"user" : user_id, "projects": []}
    requests.put(url, headers=headers, data=json.dumps(initial_data))
    # new_response.raise_for_status()
    if return_as_string:
        return initial_data
    return json.loads(initial_data)

#updates the storage File with the added files
def update_storage_file(user_id, add_elements):
    '''
    updated the storage file for @user_id with new Elements @add_elements. Integrity is checked, so
    heritage is correctly considered.
    '''
    if DEBUG:
        print("---in updatestorage_file---")
        print("writing " + str(len(add_elements)) + " items in file")
    storage_file = get_datastructure(user_id)
    # if DEBUG:
    #       print("storage file before process")
    #       print(json.dumps(storage_file))
    for item in add_elements:
        if not item["successfully_stored"]:
            continue
        projects = [x for x in storage_file["projects"] if x["projectID"] == item["projectID"]]
        if not projects:
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
            continue
        entries = [x for x in projects[0]["entries"] if x["entryID"] == item["entryID"]]
        if not entries:
            projects[0]["entries"].append({
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
            })
            continue
        entry_versions = [x for x in entries[0]["versions"] if \
                          x["versionID"] == item["entryVersionID"]]
        if not entry_versions:
            entries[0]["versions"].append({
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
            })
            continue
        elements = [x for x in entry_versions[0]["elements"] if x["elementID"] == item["elementID"]]
        if not elements:
            entry_versions[0]["elements"].append({
                "elementID" : item["elementID"],
                "elementType" : item["elementType"],
                "versions" : [{
                    "versionID" : item["versionID"],
                    "couchdb_doc_id" : item["couchdb_doc_id"],
                    "couchdb_doc_item_att_name" : item["couchdb_doc_item_att_name"]
                }]
            })
            continue
        elements[0]["versions"].append({
            "versionID" : item["versionID"],
            "couchdb_doc_id" : item["couchdb_doc_id"],
            "couchdb_doc_item_att_name" : item["couchdb_doc_item_att_name"]
        })
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
        print("----------in remove_existing_tuples----------\n")
        print("storage:")
        print(json.dumps(storage_file))
        print("check:")
        print(json.dumps(check_elements))
    output = []
    if storage_file["projects"] is None or not storage_file["projects"]:
        return check_elements
    for item in check_elements:
        proj_vals = [x for x in storage_file["projects"] if x["projectID"] == item["projectID"]]
        if not proj_vals:
            output.append(item)
            continue
        entry_vals = [x for x in proj_vals[0]["entries"] if x["entryID"] == item["entryID"]]
        if not entry_vals:
            output.append(item)
            continue
        entry_version_vals = [x for x in entry_vals[0]["versions"] \
                              if x["versionID"] == item["entryVersionID"]]
        if not entry_version_vals:
            output.append(item)
            continue
        element_vals = [x for x in entry_version_vals[0]["elements"] \
                        if x["elementID"] == item["elementID"]]
        if not element_vals:
            output.append(item)
            continue
        version_vals = [x for x in element_vals[0] \
                       ["versions"] if x["versionID"] == item["versionID"]]
        if version_vals:
            continue
        output.append(item)
    return output

def create_zip_from_files(download_meta, filename):
    '''curl 
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

@APP.route('/metadata/structures', methods=['GET'])
def get_metadata():
    '''
        Return Metadata structure file from server, providing information about supported meta data
    '''
    if not 'session_user' in request.cookies or not 'session_auth' in request.cookies:
        return {'Error' : FAILED_AUTHENTICATION}, 401, {'Content-Type' : 'application/json'}
    if not check_session(request.cookies['session_user'], request.cookies['session_auth']):
        return {'Error' : FAILED_AUTHENTICATION}, 401, {'Content-Type' : 'application/json'}
    data = ''
    with open(CONFIGPARAMS["METADATA_INFO_FILE"]) as file:
        data = file.read()
    return json.dumps(data)

@APP.route('/metadata/user', methods=['GET'])
def get_user_stored_metadata():
    '''
        Routed from /metadata/user GET
        Gets the stored metadata sets for the requesting user
    '''
    if not 'session_user' in request.cookies or not 'session_auth' in request.cookies:
        return {'Error' : FAILED_AUTHENTICATION}, 401, {'Content-Type' : 'application/json'}
    if not check_session(request.cookies['session_user'], request.cookies['session_auth']):
        return {'Error' : FAILED_AUTHENTICATION}, 401, {'Content-Type' : 'application/json'}
    user_id = request.cookies['session_user']
    url = CONFIGPARAMS["couchDBBaseURL"] + "/" + CONFIGPARAMS["couchDBMetaDataDatabaseName"] + "/"\
          + user_id
    token = authenticate_couchdb()
    if not token:
        if DEBUG:
            print("Auth to couchDB not successfull. Returning")
        return ''
    headers = {"Accept": "application/json", "Content-Type" : "application/json", "Cookie" :  token}
    if DEBUG:
        print("trying to get metadata for user with url: " + url)
        print(headers)
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        # if DEBUG:
        return response.text
    return ''

@APP.route('/metadata/user', methods=['PUT'])
def store_user_metadata():
    '''
        Routed from /metadata/user PUT
        Stores an updated metadata set for the user, version managing is done on client side
    '''
    if not 'session_user' in request.cookies or not 'session_auth' in request.cookies:
        return {'Error' : FAILED_AUTHENTICATION}, 401, {'Content-Type' : 'application/json'}
    if not check_session(request.cookies['session_user'], request.cookies['session_auth']):
        return {'Error' : FAILED_AUTHENTICATION}, 401, {'Content-Type' : 'application/json'}
    user_id = request.cookies['session_user']
    url = CONFIGPARAMS["couchDBBaseURL"] + "/" + CONFIGPARAMS["couchDBMetaDataDatabaseName"] + "/"\
          + user_id
    token = authenticate_couchdb()
    if not token:
        if DEBUG:
            print("Auth to couchDB not successfull. Returning")
        return ''
    headers = {"Accept": "application/json", "Content-Type" : "application/json", "Cookie" :  token}
    if DEBUG:
        print("trying to put metadata for user with url: " + url)
        print(headers)
        print("data:")
        print(json.loads(request.get_data()))
    response = requests.put(url, headers=headers, data=json.loads(request.get_data()))
    if response:
        return json.dumps({'Result' : 'All good'}), 200, {'Content-Type' : 'application/json'}
    return json.dumps({'Result' : 'Error Storing file'}), 500, {'Content-Type' : 'application/json'}

@APP.route("/ingest/submit", methods=['PUT'])
def submit_user_ingest_to_review():
    '''
        User Ingest provided in data is submitted to the lzv process. We need to safe the submitted
        ingest in a seperate db so it cant be deleted since we need to verify to always have access
        to the provided data. Ingests are first stored in a review
    '''
    if not 'session_user' in request.cookies or not 'session_auth' in request.cookies:
        return {'Error' : FAILED_AUTHENTICATION}, 401, {'Content-Type' : 'application/json'}
    if not check_session(request.cookies['session_user'], request.cookies['session_auth']):
        return {'Error' : FAILED_AUTHENTICATION}, 401, {'Content-Type' : 'application/json'}
    token = authenticate_couchdb()
    if not token:
        if DEBUG:
            print("Auth to couchDB not successfull. Returning")
        return json.dumps({'Result' : 'Internal Server Error'}), 500,\
                          {'Content-Type' : 'application/json'}
    user_id = request.cookies['session_user']
    storage_file = get_datastructure(user_id)
    ingest = json.loads(request.get_data())
    ingest_review_path = CONFIGPARAMS["LZV_REVIEW"] + ingest["ingest_id"] + "/content/"
    ingest['user_id'] = user_id
    print("---")
    print(json.dumps(ingest))
    for ingest_element in ingest['content']:
        print("ingest_element:---")
        print(json.dumps(ingest_element))
        version = search_for_version(storage_file, ingest_element['version_id'])
        if version is not None:
            filename = version['entry_title'] + '-'\
            + version['version']['versionID']
            # print("version:---")
            # print(json.dumps(version))
            download_files_to_path(ingest_review_path, filename, version['version'])
            ingest_element['path'] = filename
        else:
            if DEBUG:
                print("didnt find version in storage File")
    #store a file in the database for review
    couchdb_url = CONFIGPARAMS["couchDBBaseURL"] + "/" + CONFIGPARAMS["couchDBIngestsDatabaseName"]\
        + "/" + ingest['ingest_id']
    headers = {"Accept": "application/json", "Content-Type" : "application/json", "Cookie" :  token}
    if DEBUG:
        print("trying to submit ingest for user with url: " + couchdb_url)
        print(headers)
        print("ingest:")
        print(json.dumps(ingest))
    response = requests.put(couchdb_url, headers=headers, data=ingest)
    if response:
        return json.dumps({'Result' : 'All good'}), 200, {'Content-Type' : 'application/json'}
    return json.dumps({'Result' : 'Error Storing ingest'}), 500,\
                      {'Content-Type' : 'application/json'}

def download_files_to_path(path, element_name, version):
    '''
        downlaods the file provided in version from couchdb and saves it in element_name. filename 
        should contain the path from root
    '''
    cdb_doc_url_base = CONFIGPARAMS["couchDBBaseURL"] + "/" + \
                       CONFIGPARAMS["couchDBDocumentDatabaseName"] + "/"
    token = authenticate_couchdb()
    if not token:
        return
    tmp_path_file = Path(path)
    tmp_path_file.mkdir(mode=0o770, parents=True, exist_ok=True)
    for ele in version["elements"]:
        #each element should only have one version, so wen access the first element
        cdb_doc_url = cdb_doc_url_base + ele["versions"][0]["couchdb_doc_id"] + "/" \
        + ele["versions"][0]["couchdb_doc_item_att_name"]
        if ele["elementType"] == "TEXT":
            filetype = '.txt'
        elif ele["elementType"] == "TABLE":
            filetype = '.csv'
        elif ele["elementType"] == "IMAGE":
            filetype = '.png'
        tmp_file = Path(path+element_name+'-'+ele["versions"][0]["versionID"]+filetype)
        # print(tmp_file)
        # print(path)
        tmp_file.touch(mode=0o770, exist_ok=True)
        headers = {"Accept": "application/json",
                   "Content-Type" : "application/json",
                   "Cookie" :  token
                  }
        response = requests.get(cdb_doc_url, headers=headers)
        if response:
            if ele["elementType"] == "TEXT" or ele["elementType"] == "TABLE":
                tmp_file.write_text(response.text)
            elif ele["elementType"] == "IMAGE":
                tmp_file.write_bytes(response.content)


def search_for_version(storage_file, version_id):
    '''
        searched in storage_file for a entry version with id version id. returns the version object.
    '''
    for project in storage_file['projects']:
        for entry in project['entries']:
            for version in entry['versions']:
                if version['versionID'] == version_id:
                    return {'version': version, 'entry_title': entry['entryTitle'],\
                            'entry_id' : entry['entryID'], 'project_id' : project['projectID']}
    return None

if __name__ == '__main__':
    #authenticate_couchdb()
    APP.run(debug=True)

'''
    Script for creating a new couchDB Database
'''
import json
import sys
import requests
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

with open('./conf/config.json') as f:
    CONFIGPARAMS = json.load(f)




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
        cookie = response.headers["Set-Cookie"]
        couchdb_token = cookie[:cookie.find(";")]
        return couchdb_token
    return False


def create_database(name):
    token = authenticate_couchdb()
    if not token:
        return
    create_url = CONFIGPARAMS["couchDBBaseURL"] + "/" + name 
    couch_header = {"Accept": "application/json",
                    "Content-Type" : "application/json",
                    "Cookie" :  token}
    print(create_url)
    response = requests.put(create_url, headers=couch_header)
    if response:
        print("successfully created new database " + name)
        print(response.text)
    else:
        print("error creating database " + name)
        print(response.text)


if __name__ == '__main__':
    if len(sys.argv) == 2:
        create_database(str(sys.argv[1]))
    else:
        print("usage: create_database.py <database_name>")


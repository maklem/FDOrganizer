'''
    Script for purging the storageFile couchDB for testing purposes
'''
import json
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

with open('/server/lzv/server/conf/config.json') as f:
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


def purge_storage_file():
    '''
        Purges the storage file
    '''
    token = authenticate_couchdb()
    if not token:
        return
    purge_url = CONFIGPARAMS["couchDBBaseURL"] + "/" + CONFIGPARAMS["couchDBStorageDatabaseName"] + "/" + "_purge"
    print(purge_url)
    get_url = CONFIGPARAMS["couchDBBaseURL"] + "/" + CONFIGPARAMS["couchDBStorageDatabaseName"] + "/" + DEVUSER_ID
    print(get_url)
    couch_header = {"Accept": "application/json",
                    "Content-Type" : "application/json",
                    "Cookie" :  token}
    rev_response = json.loads(requests.get(get_url, headers=couch_header).text)
    if not rev_response:
        print("Error geting revision info")
    data = {DEVUSER_ID : [rev_response["_rev"]]}
    response = requests.post(purge_url, headers=couch_header, data=json.dumps(data))
    if response:
        print("succesfully purged with message: ")
        print(response.text)
    else:
        print("error purging!")
        print(response.text)


if __name__ == '__main__':
    purge_storage_file()

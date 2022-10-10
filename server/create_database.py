'''
    Script for creating a new couchDB Database
'''
import json
import sys
import requests

#Reading Config
def getConfig():
    with open('./conf/config.json') as f:
        return json.load(f)

def getCredentials():
    config = getConfig()
    return {
        "username": f'{config["couchDBAdmin"]}',
        "password": f'{config["couchDBPassword"]}',
    }

def getBaseURL():
    return getConfig()["couchDBBaseURL"]

#Authentication
def authenticate(url: str, username: str, password: str):
    data = f'name={username}&password={password}'
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    return requests.post(url, data=data, headers=headers)


def getAuthenticationToken(username: str, password: str):
    url = f'{getBaseURL()}/_session'
    response = authenticate(url, username, password)
    print(url)
    if not response.status_code == 200:
        print(f'User Authentication not sucessful! Check configured username and password')
        return False
    cookie = response.headers["Set-Cookie"]
    return cookie[:cookie.find(";")]


#Creating Database
def getDatabaseName():
    if len(sys.argv) == 2:
        return str(sys.argv[1])
    return input("Wählen Sie einen Namen für die Datenbank:\n")

def create(url: str, token: str):
    couch_header = {"Accept": "application/json",
                    "Content-Type" : "application/json",
                    "Cookie" :  token}
    return requests.put(url, headers=couch_header)

def create_database(name: str, token: str):
    print(f'Creating Database "{name}"')
    url = f'{getBaseURL()}/{name}'
    response = create(url, token)
    if response.status_code != 201:
        print(f'Error creating Database "{name}":')
        print(f'{response.json()["reason"]}')
        return
    print("Successfully created new database " + name)

#Run
if __name__ == '__main__':
    username, password = getCredentials().values()
    print(username, password)
    token = getAuthenticationToken(username, password)
    if not token:
        sys.exit()
    databaseName = getDatabaseName()
    create_database(databaseName, token)
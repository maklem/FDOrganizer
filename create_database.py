'''
    Script for creating a new couchDB Database
'''
import os
import sys
from dotenv import load_dotenv
import requests

def credentials():
    return {
        "username": f'{os.getenv("COUCHDB_USER")}',
        "password": f'{os.getenv("COUCHDB_PASSWORD")}',
    }

def base_url():
    return f'http://{os.getenv("COUCHDB_HOST")}:{os.getenv("COUCHDB_PORT")}'

#Authentication
def authenticate(url: str, username: str, password: str):
    data = f'name={username}&password={password}'
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    return requests.post(url, data=data, headers=headers)


def authentication_token(username: str, password: str):
    url = f'{base_url()}/_session'
    response = authenticate(url, username, password)
    print(url)
    if not response.status_code == 200:
        print(f'User Authentication not sucessful! Check configured username and password')
        return False
    cookie = response.headers["Set-Cookie"]
    return cookie[:cookie.find(";")]


#Creating Database
def get_database_names():
    if len(sys.argv) >= 2:
        return sys.argv[1:]
    return [input("Wählen Sie einen Namen für die Datenbank:\n")]

def create(url: str, token: str):
    couch_header = {"Accept": "application/json",
                    "Content-Type" : "application/json",
                    "Cookie" :  token}
    return requests.put(url, headers=couch_header)

def create_database(name: str, token: str):
    print(f'Creating Database "{name}"')
    url = f'{base_url()}/{name}'
    response = create(url, token)
    if response.status_code != 201:
        print(f'Error creating Database "{name}":')
        print(f'{response.json()["reason"]}')
        return
    print("Successfully created new database " + name)

#Run
if __name__ == '__main__':
    load_dotenv()
    username, password = credentials().values()
    token = authentication_token(username, password)
    if not token:
        sys.exit()
    databaseNames = get_database_names()
    for dbn in databaseNames:
        create_database(dbn, token)
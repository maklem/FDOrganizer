'''
    Script for purging the storageFile couchDB for testing purposes
'''
import sys
import requests
import create_database
from requests import HTTPError

def getDatabaseName():
    if len(sys.argv) == 2:
        return str(sys.argv[1])
    return input("Welche Datenbank möchten Sie zurücksetze:\n")

def delete(url: str, token: str):
    couch_header = {
        "Accept": "application/json",
        "Content-Type" : "application/json",
        "Cookie" :  token
    }
    return requests.delete(url, headers=couch_header)

def print_reset_error(name: str, error: HTTPError):
    print(f'Error resetting Database "{name}":')
    print(f'{error.response.reason}')

def reset_database(name: str, token: str):
    print(f'Resetting Database "{name}"')
    url = f'{create_database.getBaseURL()}/{name}'
    deletion = delete(url, token)
    deletion.raise_for_status()
    creation = create_database.create(url, token)
    creation.raise_for_status()
    print("Successfully reset database" + name)

if __name__ == '__main__':
    username, password = create_database.getCredentials().values()
    token = create_database.getAuthenticationToken(username, password)
    if not token:
        sys.exit()
    databaseName = getDatabaseName()
    try:
        reset_database(databaseName, token)
    except HTTPError as error:
        print_reset_error(databaseName, error)

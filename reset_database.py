'''
    Script for purging the storageFile couchDB for testing purposes
'''
import sys
import requests
import create_database

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

def print_reset_error(name: str, response: requests.Response):
    print(f'Error resetting Database "{name}":')
    print(f'{response.json()["reason"]}')

def reset_database(name: str, token: str):
    print(f'Resetting Database "{name}"')
    url = f'{create_database.getBaseURL()}/{name}'
    deletion = delete(url, token)
    if deletion.status_code != 201:
        print_reset_error(name, deletion)
        return
    creation = create_database.create(url, token)
    if creation.status_code != 201:
        print_reset_error(name, creation)
        return
    print("Successfully reset database" + name)

if __name__ == '__main__':
    username, password = create_database.getCredentials().values()
    token = create_database.getAuthenticationToken(username, password)
    if not token:
        sys.exit()
    databaseName = getDatabaseName()
    reset_database(databaseName, token)

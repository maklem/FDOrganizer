'''
    Script for creating a new couchDB Database
'''
import os
import sys
from pathlib import Path
from dotenv import load_dotenv
import requests #type: ignore
import json
from simple_term_menu import TerminalMenu #type: ignore

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
def get_organisation_data():
    if len(sys.argv) >= 1:
        return json.loads(open(Path(sys.argv[1])).read())
    # Init data structure
    organisation_data = {}
    organisation_data['reviewers'] = []
    organisation_data['plugins'] = []
    organisation_data['identity_provider'] = {}

    # Let user input data
    organisation_data['name'] = input("Name der Organisation:\n")
    organisation_data['identity_provider'] = get_idp_data()

    return organisation_data

def get_idp_data():
    identity_provider = {}

    options = ["OIDC", "SAML", "LDAP", "LOCAL"]
    terminal_menu = TerminalMenu(options)
    identity_provider['type'] = options[terminal_menu.show()] # type: ignore

    identity_provider['url'] = input("URL für Authentifizierung:\n")
    identity_provider['scope'] = []
    print("Der IDP stellt Nutzerinformationen mit unterschiedlichem Detailgrad bereit (sog. Scopes). Schreiben sie den Namen des Scopes und drücken Sie danach ENTER, um ihn hinzuzufügen. Wenn Sie alle Scopes hinzugefügt haben, drücken sie STRG + D")
    while True:
        try:
            item = input("Weiterer Scope:\n")
        except EOFError:
            break
        identity_provider['scope'].append(item)
        print(f'Scope {item} erfolgreich hinzugefügt')
    if identity_provider['type'] != 'LDAP':
        identity_provider['client_id'] = input("Registrierte ID des Clients beim IDP:\n")
        identity_provider['client_secret'] = input("Secret des Clients beim IDP:\n")
    return identity_provider

def create(url: str, token: str, data: dict):
    couch_header = {"Accept": "application/json",
                    "Content-Type" : "application/json",
                    "Cookie" :  token}
    return requests.post(url, data=json.dumps(data), headers=couch_header)

def create_organisation(organisation_data: dict, token: str):
    print(f'Creating organisation "{organisation_data["name"]}"')
    url = f'{base_url()}/organisations'
    response = create(url, token, organisation_data)
    if response.status_code != 201:
        print(f'Error creating organisation "{organisation_data["name"]}":')
        print(f'{response.json()["reason"]}')
        return
    print(f'Successfully created organisation "{organisation_data["name"]}"')
    return response.json()['id']

def create_users(users: list[dict], token: str):
    print(f'Creating users')
    url = f'{base_url()}/users'
    users = [create(url, token, user).json()['id'] for user in users]
    print(f'Successfully created users')
    return users

def get_users(organisation_id):
    with open('dummy_users.json', 'r') as file:
        users = json.load(file)
    return [{"username": user['username'],"password": user['password'], "organisation": organisation_id} for user in users]

#Run
if __name__ == '__main__':
    load_dotenv()
    username, password = credentials().values()
    token = authentication_token(username, password)
    if not token:
        sys.exit()
    org_data = get_organisation_data()
    organisation_id = create_organisation(org_data, token)
    if org_data['identity_provider']['type'] == "LOCAL":
        users = get_users(organisation_id)
        create_users(users, token)
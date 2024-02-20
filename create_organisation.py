'''
    Script for creating a new couchDB Database
'''
import os
import sys
from pathlib import Path
from dotenv import load_dotenv
import requests
import json
from simple_term_menu import TerminalMenu

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

    options = ["OIDC", "SAML", "LDAP"]
    terminal_menu = TerminalMenu(options)
    identity_provider['type'] = options[terminal_menu.show()]

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
def create(url: str, token: str, organisation_data: dict):
    couch_header = {"Accept": "application/json",
                    "Content-Type" : "application/json",
                    "Cookie" :  token}
    return requests.post(url, data=json.dumps(organisation_data), headers=couch_header)

def create_organisation(organisation_data: dict, token: str):
    print(f'Creating organisation "{organisation_data["name"]}"')
    url = f'{base_url()}/organisations'
    response = create(url, token, organisation_data)
    if response.status_code != 201:
        print(f'Error creating organisation "{organisation_data["name"]}":')
        print(f'{response.json()["reason"]}')
        return
    print(f'Successfully created organisation "{organisation_data["name"]}"')

#Run
if __name__ == '__main__':
    load_dotenv()
    username, password = credentials().values()
    token = authentication_token(username, password)
    if not token:
        sys.exit()
    identity_provider = get_organisation_data()
    create_organisation(identity_provider, token)
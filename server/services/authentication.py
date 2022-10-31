SECRET = 'In nomine domini est pax et salvatio'

from time import time
from json import dumps, loads
from typing import TypedDict
from flask.wrappers import Request
from jwt import InvalidSignatureError, encode, decode, DecodeError
from requests import HTTPError
import ldap
from server.services.database import get
from server.entities.databases import Databases

class TokenPayload(TypedDict):
    username: str
    organisation: str
    timeout: int

def create_payload(username: str, organisation: str) -> TokenPayload:
    return {
        'username': username,
        'timeout': int(time()) + 60 * 60 * 24,
        'organisation': organisation
    }

def create_token(username, organisation):
    return encode(payload = create_payload(username, organisation), key = SECRET)

def payload(token):
    return decode(token, key = SECRET, algorithms = ['HS256', ])


def token_valid(token: str):
    try:
        content = payload(token)
    except InvalidSignatureError:
        return False
    timeout = content.get('timeout') or 0
    if timeout < int(time()):
        return False
    return True

def authorize(username: str, password: str, organisation: str):
    if not credentials_valid(username, password, organisation):
        raise HTTPError("Credentials not valid")
    return create_token(username, organisation)

def is_authorized(request: Request):
    try:
        token = request.cookies['token']
    except KeyError:
        return False
    try:
        return token_valid(token)
    except DecodeError:
        return False

def user(request: Request):
    token = request.cookies['token']
    return payload(token)['username']


def credentials_valid(username: str, password: str, organisation: str):
    return True
    org = get_organisation(organisation)
    if org.authorization_method == "ldap":
        return auth_ldap(username, password, org.ldap_server, org.ldap_base)


def get_organisation(organisation: str):
    query = {"selector": {"name": organisation}}
    org = get(Databases.ORGANISATIONS, query = dumps(query))
    return loads(org.json())

def auth_ldap(username, password, ldap_server, ldap_base):
    user_dn = "cn=" + username + "," + ldap_base
    connect = ldap.initialize(ldap_server)
    try:
        connect.bind_s(user_dn, password)
        connect.unbind_s()
        return True
    except ldap.LDAPError:
        connect.unbind_s()
        return False
        
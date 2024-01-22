SECRET = 'In nomine domini est pax et salvatio'

from time import time
from json import dumps, loads
from typing import TypedDict
from flask.wrappers import Request
from jwt import InvalidSignatureError, encode, decode, DecodeError
from requests import HTTPError
import ldap

from .database import get
from ..entities import Databases, Organisation

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


def add_payload(token: str, key: str, value: str):
    updated_payload = payload(token) | {key: value}
    return encode(payload = updated_payload, key = SECRET)


def create_token(username, organisation):
    return encode(payload = create_payload(username, organisation), key = SECRET, algorithm='HS256')


def payload(token: str):
    return decode(token, key = SECRET, algorithms = ['HS256'])


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

def user(request: Request) -> str:
    token = request.cookies['token']
    return payload(token)['username']


def credentials_valid(username: str, password: str, organisation_id: str):
    organisation = Organisation.from_db(get(Databases.ORGANISATIONS, organisation_id).json())
    if organisation.identity_provider.type == "LDAP":
        return True
        return auth_ldap(username, password, organisation.identity_provider.url, organisation.identity_provider.scope)
    else:
        return True
    
def auth_ldap(username: str, password: str, url: str, scope:[str]):
    user_dn = f'cn={username},{",".join(str(element) for element in scope)}'
    connect = ldap.initialize(url)
    try:
        connect.bind_s(user_dn, password)
        connect.unbind_s()
        return True
    except ldap.LDAPError:
        connect.unbind_s()
        return False
        
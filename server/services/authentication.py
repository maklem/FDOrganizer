SECRET = 'In nomine domini est pax et salvatio'

import json
from time import time
from json import dumps, loads
from typing import TypedDict
from flask.wrappers import Request
from jwt import InvalidSignatureError, encode, decode, DecodeError
from requests import HTTPError #type: ignore
import ldap #type: ignore

from .database import find, get
from ..entities import Databases, Organisation

class TokenPayload(TypedDict):
    username: str
    organisation: str
    timeout: int
    reviewer: bool

def create_payload(username: str, organisation_id: str) -> TokenPayload:
    organisation = Organisation.from_db(get(Databases.ORGANISATIONS, organisation_id).json())
    is_reviewer = False
    if organisation.reviewers is not None:
        is_reviewer = username in organisation.reviewers
    return {
        'username': username,
        'timeout': int(time()) + 60 * 60 * 24,
        'organisation': organisation_id,
        'reviewer': is_reviewer
    }


def add_payload(token: str, key: str, value: str):
    updated_payload = payload(token) | {key: value}
    return encode(payload = updated_payload, key = SECRET)


def create_token(username, organisation):
    return encode(payload = dict(create_payload(username, organisation)), key = SECRET, algorithm='HS256')


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

def organisation(request) -> str:
    token = request.cookies['token']
    return payload(token)['organisation']

def is_reviewer(request: Request) -> bool:
    token = request.cookies['token']
    return payload(token)['reviewer']

def credentials_valid(username: str, password: str, organisation_id: str):
    organisation = Organisation.from_db(get(Databases.ORGANISATIONS, organisation_id).json())
    if organisation.identity_provider.type == "LDAP":
        return True
        return auth_ldap(username, password, organisation.identity_provider.url, organisation.identity_provider.scope)
    elif organisation.identity_provider.type == "LOCAL":
        query =  {
            "selector": {
                "organisation": organisation_id,
                "username": username
            }
        }
        user = find(Databases.USERS, json.dumps(query)).json().get('docs')[0]
        if user is not None:
            return True
        else:
            return False
    else:
        return True
    
def auth_ldap(username: str, password: str, url: str, scope: list[str]):
    user_dn = f'cn={username},{",".join(str(element) for element in scope)}'
    connect = ldap.initialize(url)
    try:
        connect.bind_s(user_dn, password)
        connect.unbind_s()
        return True
    except ldap.LDAPError: # type: ignore
        connect.unbind_s()
        return False
        
from server.entities.identityprovider import IdentityProvider

import json
import os
from time import time
from typing import TypedDict
from flask.wrappers import Request
from jwt import InvalidSignatureError, encode, decode, DecodeError
from requests import HTTPError #type: ignore
import ldap #type: ignore

from .database import find, get
from ..entities import Databases, Organisation

SECRET = str(os.getenv('TOKEN_SECRET'))

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


def remove_payload(token: str, key: str):
    updated_payload = payload(token) | {key: None}
    return encode(payload = updated_payload, key = SECRET)


def create_token(username, organisation):
    return encode(payload = {**create_payload(username, organisation)}, key = SECRET, algorithm='HS256')


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

def authorize(username: str, password: str, idp_id: str):
    identity_provider = IdentityProvider.from_db(get(Databases.IDENTITYPROVIDERS, idp_id).json())
    if not identity_provider.organisation:
        raise HTTPError(f"Invalid Configuration for {idp_id=}. Field 'organisation' not set or empty.")
    if not credentials_valid(username, password, idp_id):
        raise HTTPError("Credentials not valid")
    return create_token(username, identity_provider.organisation)

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

def user_displayname(request: Request) -> str:
    token = request.cookies['token']
    data = payload(token)
    return data["displayname"] if "displayname" in data else data["username"]

def organisation(request: Request) -> str:
    token = request.cookies['token']
    return payload(token)['organisation']

def organisation_displayname(request: Request) -> str:
    token = request.cookies['token']
    data = payload(token)
    return data["organisation_displayname"] if "organisation_displayname" in data else data["organisation"]

def is_reviewer(request: Request) -> bool:
    token = request.cookies['token']
    return payload(token)['reviewer']

def credentials_valid(username: str, password: str, idp_id: str) -> bool:
    identity_provider = IdentityProvider.from_db(get(Databases.IDENTITYPROVIDERS, idp_id).json())
    if identity_provider.organisation is None:
        return False
    if identity_provider.type == "LOCAL":
        query =  {
            "selector": {
                "organisation": idp_id,
                "username": username,
                "password": password
            }
        }
        user = find(Databases.USERS, json.dumps(query)).json().get('docs')[0]
        if user is not None:
            return True
        else:
            return False
    else:
        return False
    
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
        
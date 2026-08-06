import json
from time import time
from typing import TypedDict

from flask.wrappers import Request
from jwt import DecodeError, InvalidSignatureError, decode, encode
from requests import HTTPError

from server.entities.identityprovider import IdentityProvider

from ..entities import Databases, Organisation
from .database import find, get


class TokenPayload(TypedDict):
    username: str
    organisation: str
    timeout: int
    reviewer: bool


def token_secret() -> str:
    import os
    secret = os.getenv('TOKEN_SECRET')
    if secret is None:
        raise ValueError("no secret set!")
    return str(secret)


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
    return encode(payload = updated_payload, key = token_secret())


def remove_payload(token: str, key: str):
    updated_payload = payload(token) | {key: None}
    return encode(payload = updated_payload, key = token_secret())


def create_token(username, organisation_id):
    return encode(payload = {**create_payload(username, organisation_id)}, key = token_secret(), algorithm='HS256')


def payload(token: str):
    return decode(token, key = token_secret(), algorithms = ['HS256'])


def token_valid(token: str):
    try:
        content = payload(token)
    except InvalidSignatureError:
        return False
    timeout = content.get('timeout') or 0
    
    return timeout > int(time())


def find_organisation_by_tag(idp_tag: str) -> Organisation:
    errors = list[str]()
    query = {
        "selector": {
            "idp_tag": idp_tag
        }
    }
    org_response = find(Databases.ORGANISATIONS, json.dumps(query))
    if org_response.status_code != 200:
        errors.append("Invalid Configuration."),
        errors.append(f"Organisation '{idp_tag}' is not configured on this server.")
        raise RuntimeError(errors)
    
    org_data = org_response.json()['docs']
    if len(org_data) != 1:
        errors.append("Invalid Configuration."),
        errors.append(f"Organisation '{idp_tag}' is ambiguous on this server. ({len(org_data)})")
        raise RuntimeError(errors)

    return Organisation.from_db(org_data[0])


def authorize(username: str, password: str, idp_id: str):
    identity_provider = IdentityProvider.from_db(get(Databases.IDENTITYPROVIDERS, idp_id).json())
    if not identity_provider.organisation:
        raise HTTPError(f"Invalid Configuration for {idp_id=}. Field 'organisation' not set or empty.")
    if not (organisation := find_organisation_by_tag(identity_provider.organisation)):
        raise HTTPError(f"Could not log into {organisation=}. Organisation not found.")
    if not credentials_valid(username, password, idp_id):
        raise HTTPError("Credentials not valid")
    token = create_token(username, organisation.id)
    token = add_payload(token, "organisation_displayname", organisation.name)
    return token

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
                "username": username,
                "password": password,
            }
        }
        try:
            user = find(Databases.USERS, json.dumps(query)).json().get('docs')[0]
        except IndexError:
            return False

        if user is not None:
            return True
        else:
            return False
    else:
        return False

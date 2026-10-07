import dataclasses
import json
from typing import Any

from flask import session
from requests import HTTPError

from server.entities.identityprovider import IdentityProvider

from ..entities import Databases, Organisation
from .database import find, get


@dataclasses.dataclass
class UserData:
    username: str
    displayname: str
    organisation_id: str
    plugins: dict[str,Any] = dataclasses.field(default_factory=dict)

    def organisation(self) -> Organisation:
        return Organisation.from_db(get(Databases.ORGANISATIONS, self.organisation_id).json())

    @property
    def organisation_displayname(self) -> str:
        return self.organisation().name

    @property
    def reviewer(self) -> bool:
        return self.username in self.organisation().reviewers

    def list_plugins(self) -> list[str]:
        return list(self.plugins.keys())

def add_plugin(key:str, value: str):
    session["user"].plugins.update({key: value})
    session.modified = True

def remove_plugin(key: str):
    session["user"].plugins.pop(key, None)
    session.modified = True

def userdata() -> UserData:
    if "user" not in session:
        raise RuntimeError("Reading UserData without authenticated user.")
    return session["user"]


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
    if organisation.id is None:
        raise HTTPError(f"Could not log into {organisation=}. Organisation not found.")
    if not credentials_valid(username, password, idp_id):
        raise HTTPError("Credentials not valid")

    session["user"] = UserData(username, username, organisation.id, {})


def is_authorized():
    return "user" in session


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

        return user is not None
    else:
        return False

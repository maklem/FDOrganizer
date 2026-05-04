import json
from couchdb.http import HTTPError
from re import I
from server.entities.identityprovider import IdentityProvider
from flask import Response, request, redirect, session, url_for
import requests #type: ignore
from requests_oauth2client import OAuth2Client, ClientSecretJwt

from typing import Any

from server import APP
from .entities.errors import IdentityProviderError
from .entities.organisation import Organisation
from .entities.databases import Databases
from .services.database import get, getall, find
from .util import json_body, web_error, web_response, error_page
from .services.authentication import authorize, create_token, add_payload, is_authorized, user, user_displayname, organisation_displayname

@APP.route("/organisations", methods=["GET"])
def get_organisations():
    identity_providers = [IdentityProvider.from_db(identityprovider) for identityprovider in getall(Databases.IDENTITYPROVIDERS)]
    identity_provider_stubs = [{'id': identity_provider.id, 'name': identity_provider.name, 'authType': identity_provider.type} for identity_provider in identity_providers]
    return web_response(200, details=identity_provider_stubs)

@APP.route("/login-local/<idp_id>", methods=["POST"])
@json_body
def login_local(idp_id: str, username: str, password: str) -> Response:
    try:
        token = authorize(username, password, idp_id)
    except HTTPError as e:
        return web_response(403, details = {'success': False, 'reason': e.args[0]})
    except RuntimeError:
        return web_response(403, details = {'success': False, 'reason': "wrong credentials"})

    auth_response =  web_response(200, details = {'success': True})
    auth_response.set_cookie('token', token)
    return auth_response

@APP.route("/login-oidc/<idp_id>", methods=["GET"])
def login_oidc(idp_id: str):
    identity_provider = get_idp_from_db(idp_id)
    try:
        client = oidc_client(identity_provider)
    except IdentityProviderError as error:
        return web_error(500, error.args[0], component = "SERVER")
    # create auth request for OIDC-IDP
    az_request = client.authorization_request(scope=identity_provider.scope)
    # save current login attempt data
    session['code_verifier'] = az_request.code_verifier
    session['state'] = az_request.state
    session['nonce'] = az_request.nonce
    # redirect to OIDC login window
    return web_response(200, details={"auth_url": az_request.uri})

@APP.route("/login-oidc-callback/<organisation_id>", methods=["GET"])
def callback_oidc(idp_id: str):
    identity_provider = get_idp_from_db(idp_id)
    client = oidc_client(identity_provider)
    
    # create auth request from callback URL
    url= request.url
    az_request = client.authorization_request(scope=identity_provider.scope,
                                              state=session['state'],
                                              code_verifier=session['code_verifier'],
                                              nonce=session['nonce']
                                              )
    
    # get info of authenticated user after successful authorization
    az_response = az_request.validate_callback(url)
    idp_token = client.authorization_code(az_response)                                  
    userinfo = client.userinfo(idp_token)
    # email = userinfo['email']
    # given_name = userinfo['given_name']
    # family_name = userinfo['family_name']
    # sub = userinfo['sub']
    username = userinfo['username']

    # remove login attempt ID after successful login
    session.pop('code_verifier')
    session.pop('state')
    session.pop('nonce')

    try:
        user_organisation = user_organisation_from_login(identity_provider, userinfo)
    except RuntimeError as e:
        return error_page(e.args[0])

    # create token with info for authenticated user
    token = create_token(username, user_organisation)

    # redirect to start page and set auth cookie
    redirect_response = redirect(url_for('navhome'))
    redirect_response.set_cookie('token', token)
    return redirect_response

@APP.route("/login-keycloak/<idp_id>", methods=["GET"])
def login_keycloak(idp_id: str):
    identity_provider = get_idp_from_db(idp_id)

    scopes = '+'.join(identity_provider.scope)
    auth_url = f'{identity_provider.url}auth?scope={scopes}&response_type=code&client_id={identity_provider.client_id}&redirect_uri={request.url_root}login-keycloak-callback/{identity_provider.id}'
    if identity_provider.client_secret is not None:
        auth_url += f'&client_secret={identity_provider.client_secret}'
    # redirect to OIDC login window
    return web_response(200, details={"auth_url": auth_url})

@APP.route("/login-keycloak-callback/<idp_id>", methods=["GET"])
def callback_keycloak(idp_id: str):
    identity_provider = get_idp_from_db(idp_id)
    errors = []

    token_url = f'{identity_provider.url}token'
    token_request_body= {
        'grant_type': 'authorization_code',
        'client_id': identity_provider.client_id,
        'redirect_uri': f'{request.url_root}login-keycloak-callback/{identity_provider.id}',
        'code': request.args.get('code')
    }
    if identity_provider.client_secret is not None:
        token_request_body['client_secret'] = identity_provider.client_secret
    token_response = requests.post(token_url, data=token_request_body)
    try:
        access_token = token_response.json()['access_token']
    except KeyError:
        return error_page(400, ["Could not accquire access token for fetching user info. Organisation IDP-data might be wrong."])

    userinfo_url = f'{identity_provider.url}userinfo'
    userinfo_response = requests.get(userinfo_url, headers={'Authorization': f'Bearer {access_token}'})
    userinfo = userinfo_response.json()

    if identity_provider.username_field is None:
        try:
            username = userinfo['username']
        except KeyError:
            return error_page(400, [f"No 'username' field or custom field for the organisation found in {userinfo=}"])
    else:
        username = userinfo[identity_provider.username_field]

    try:
        user_organisation = user_organisation_from_login(identity_provider, userinfo)
    except RuntimeError as e:
        return error_page(500, e.args[0])

    organisation = get_organisation_from_db(user_organisation)

    user_displayname= None
    if identity_provider.displayname_field is not None and identity_provider.displayname_field in userinfo:
        user_displayname = userinfo[identity_provider.displayname_field]

    # create token with info for authenticated user
    token = create_token(username, user_organisation)
    if user_displayname:
        token = add_payload(token, "displayname", user_displayname)

    token = add_payload(token, "organisation_displayname", organisation.name)

    # redirect to start page and set auth cookie
    redirect_response = redirect(url_for('navhome'))
    redirect_response.set_cookie('token', token)
    return redirect_response

def user_organisation_from_login(identity_provider: IdentityProvider, userinfo: dict[str,Any]) -> str:
    errors = []
    user_organisation_tag = ""
    if identity_provider.organisation:
        user_organisation_tag = identity_provider.organisation
    elif identity_provider.organisation_field is not None:
        if identity_provider.organisation_field in userinfo:
            user_organisation_tag = userinfo[identity_provider.organisation_field]
        else:
            errors.append(f"Could not log in. Expected '{identity_provider.organisation_field}' in userinfo. Received {userinfo=}")
    else:
        errors.append("Invalid Configuration for IdentityProvider. 'organisation' and 'organisation_field' are not set.")

    if user_organisation_tag == "":
        errors.append("User could not be assigned to an organisation.")
        raise RuntimeError(errors)

    query = {
        "selector": {
            "idp_id": user_organisation_tag
        }
    }
    org_response = find(Databases.ORGANISATIONS, json.dumps(query))
    if org_response.status_code != 200:
        errors.append("Invalid Configuration."),
        errors.append(f"Organisation '{user_organisation_tag}' is not configured on this server.")
    
    org_data = org_response.json()['docs']
    if len(org_data) != 1:
        errors.append("Invalid Configuration."),
        errors.append(f"Organisation '{user_organisation_tag}' is ambiguous on this server.")
        raise RuntimeError(errors)

    user_organisation = Organisation.from_db(org_data[0])

    if not user_organisation.id:
        errors.append("Invalid Configuration."),
        errors.append(f"Found {user_organisation=}")
        raise RuntimeError(errors)

    return user_organisation.id


def oidc_client(provider: IdentityProvider):
    if provider.client_id is None or provider.client_secret is None:
        raise IdentityProviderError("Missing client id or secret")
    return OAuth2Client.from_discovery_endpoint(
        issuer=provider.url,
        auth=ClientSecretJwt(provider.client_id, provider.client_secret),
        redirect_uri=f'{request.url_root}/login-oidc-callback/{provider.id}'
    )

def get_organisation_from_db(organisation_id: str) -> Organisation:
    org_response = get(Databases.ORGANISATIONS, organisation_id).json()
    return Organisation.from_db(org_response)

def get_idp_from_db(idp_id: str) -> IdentityProvider:
    org_response = get(Databases.IDENTITYPROVIDERS, idp_id).json()
    return IdentityProvider.from_db(org_response)

@APP.route("/whoami", methods=["GET"])
def whoami():
    if not is_authorized(request):
        return web_response(200, details={"name": "", "displayname": "Not logged in", "organisation": ""})
    return web_response(200, details={"name": user(request), "displayname": user_displayname(request), "organisation": organisation_displayname(request)})
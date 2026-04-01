from flask import Response, request, redirect, session, url_for
import requests #type: ignore
from requests_oauth2client import OAuth2Client, ClientSecretJwt

from server import APP
from .entities.errors import IdentityProviderError
from .entities.organisation import Organisation
from .entities.databases import Databases
from .services.database import get, getall
from .util import json_body, web_error, web_response, error_page
from .services.authentication import authorize, create_token

@APP.route("/organisations", methods=["GET"])
def get_organisations():
    organisations = [Organisation.from_db(organisation) for organisation in getall(Databases.ORGANISATIONS)]
    organisation_stubs = [{'id': organisation.id, 'name': organisation.name, 'authType': organisation.identity_provider.type} for organisation in organisations]
    return web_response(200, details=organisation_stubs)

@APP.route("/login-local/<organisation_id>", methods=["POST"])
@json_body
def login_local(organisation_id: str, username: str, password: str) -> Response:
    try:
        token = authorize(username, password, organisation_id)
    except RuntimeError:
        return web_response(200, details = {'success': False, 'reason': "wrong credentials"})
    auth_response =  web_response(200, details = {'success': True})
    auth_response.set_cookie('token', token)
    return auth_response

@APP.route("/login-oidc/<organisation_id>", methods=["GET"])
def login_oidc(organisation_id: str):
    organisation = get_organisation_from_db(organisation_id)
    try:
        client = oidc_client(organisation)
    except IdentityProviderError as error:
        return web_error(500, error.args[0], component = "SERVER")
    # create auth request for OIDC-IDP
    az_request = client.authorization_request(scope=organisation.identity_provider.scope)
    # save current login attempt data
    session['code_verifier'] = az_request.code_verifier
    session['state'] = az_request.state
    session['nonce'] = az_request.nonce
    # redirect to OIDC login window
    return web_response(200, details={"auth_url": az_request.uri})

@APP.route("/login-oidc-callback/<organisation_id>", methods=["GET"])
def callback_oidc(organisation_id: str):
    organisation = get_organisation_from_db(organisation_id)
    client = oidc_client(organisation)
    
    # create auth request from callback URL
    url= request.url
    az_request = client.authorization_request(scope=organisation.identity_provider.scope,
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

    # create token with info for authenticated user
    token = create_token(username, organisation_id)

    # redirect to start page and set auth cookie
    redirect_response = redirect(url_for('navhome'))
    redirect_response.set_cookie('token', token)
    return redirect_response

@APP.route("/login-keycloak/<organisation_id>", methods=["GET"])
def login_keycloak(organisation_id: str):
    organisation = get_organisation_from_db(organisation_id)

    scopes = '+'.join(organisation.identity_provider.scope)
    auth_url = f'{organisation.identity_provider.url}auth?scope={scopes}&response_type=code&client_id={organisation.identity_provider.client_id}&redirect_uri={request.url_root}login-keycloak-callback/{organisation.id}'
    if organisation.identity_provider.client_secret is not None:
        auth_url += f'&client_secret={organisation.identity_provider.client_secret}'
    # redirect to OIDC login window
    return web_response(200, details={"auth_url": auth_url})

@APP.route("/login-keycloak-callback/<organisation_id>", methods=["GET"])
def callback_keycloak(organisation_id: str):
    organisation = get_organisation_from_db(organisation_id)

    token_url = f'{organisation.identity_provider.url}token'
    token_request_body= {
        'grant_type': 'authorization_code',
        'client_id': organisation.identity_provider.client_id,
        'redirect_uri': f'{request.url_root}login-keycloak-callback/{organisation.id}',
        'code': request.args.get('code')
    }
    if organisation.identity_provider.client_secret is not None:
        token_request_body['client_secret'] = organisation.identity_provider.client_secret
    token_response = requests.post(token_url, data=token_request_body)
    try:
        access_token = token_response.json()['access_token']
    except KeyError:
        return error_page(400, ["Could not accquire access token for fetching user info. Organisation IDP-data might be wrong."])

    userinfo_url = f'{organisation.identity_provider.url}userinfo'
    userinfo_response = requests.get(userinfo_url, headers={'Authorization': f'Bearer {access_token}'})
    userinfo = userinfo_response.json()

    if organisation.identity_provider.username_field is None:
        try:
            username = userinfo['username']
        except KeyError:
            return error_page(400, [f"No 'username' field or custom field for the organisation found in {userinfo=}"])
    else:
        username = userinfo[organisation.identity_provider.username_field]

    if organisation.identity_provider.required_fields is not None:
        errors = []
        for field, value in  organisation.identity_provider.required_fields.items():
            if field not in userinfo:
                errors.append(f"Field '{field}' is missing in userinfo. IdP reported {userinfo=}.")
                continue
            if userinfo[field] != value:
                errors.append(f"Could not log in. Required field '{field}' to be '{value}', but got '{userinfo[field]}'.")
        if errors:
            return error_page(403, errors)

    # create token with info for authenticated user
    token = create_token(username, organisation_id)

    # redirect to start page and set auth cookie
    redirect_response = redirect(url_for('navhome'))
    redirect_response.set_cookie('token', token)
    return redirect_response

def oidc_client(organisation: Organisation):
    # OIDC declaration
    provider = organisation.identity_provider
    if provider.client_id is None or provider.client_secret is None:
        raise IdentityProviderError("Missing client id or secret")
    return OAuth2Client.from_discovery_endpoint(
        issuer=provider.url, #https://sso-test.hm.edu  https://shibboleth-idp.uni-regensburg.de/idp/profile/SAML2/POST/SSO?execution=e1s1
        auth=ClientSecretJwt(provider.client_id, provider.client_secret),
        redirect_uri=f'{request.url_root}/login-oidc-callback/{organisation.id}'
    )

def get_organisation_from_db(organisation_id: str):
    org_response = get(Databases.ORGANISATIONS, organisation_id).json()
    return Organisation.from_db(org_response)

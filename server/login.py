from flask import Response, request, redirect, session, url_for
import json
from requests_oauth2client import OAuth2Client, ClientSecretJwt

from server import APP
from .entities.organisation import IdentityProvider, Organisation
from .entities.databases import Databases
from .services.database import get, getall
from .util import json_body, web_error, web_response
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

@APP.route("/login-ldap/<organisation_id>", methods=["POST"])
@json_body
def login_ldap(organisation_id: str, username: str, password: str) -> Response:
    try:
        token = authorize(username, password, organisation_id)
    except RuntimeError:
        return web_response(200, details = {'success': False, 'reason': "wrong credentials"})
    auth_response =  web_response(200, details = {'success': True})
    auth_response.set_cookie('token', token)
    return auth_response


@APP.route("/login-oidc/<organisation_id>", methods=["GET"])
def redirect_oidc(organisation_id: str):
    organisation = get_organisation_from_db(organisation_id)
    client = oidc_client(organisation)
    # create auth request for OIDC-IDP
    az_request = client.authorization_request(scope=organisation.identity_provider.scope)
    # save current login attempt data
    session['code_verifier'] = az_request.code_verifier
    session['state'] = az_request.state
    session['nonce'] = az_request.nonce
    # redirect to OIDC login window
    return redirect(az_request.uri)

@APP.route("/login-oidc-callback/<organisation_id>", methods=["GET"])
def login_oidc(organisation_id: str):
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

def oidc_client(organisation: Organisation):
    # OIDC declaration
    provider = organisation.identity_provider
    return OAuth2Client.from_discovery_endpoint(
        issuer=provider.url, #https://sso-test.hm.edu  https://shibboleth-idp.uni-regensburg.de/idp/profile/SAML2/POST/SSO?execution=e1s1
        auth=ClientSecretJwt(provider.client_id, provider.client_secret),
        redirect_uri=f'{request.url_root}/login-oidc-callback/{organisation.id}'
    )

def get_organisation_from_db(organisation_id: str):
    org_response = get(Databases.ORGANISATIONS, organisation_id).json()
    return Organisation.from_db(org_response)
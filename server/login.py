import secrets
from typing import Any

import requests
from couchdb.http import HTTPError
from flask import Response, redirect, request, session, url_for
from requests_oauth2client import (
    AuthorizationRequest,
    BearerToken,
    ClientSecretJwt,
    IdToken,
    InvalidIdToken,
    OAuth2Client,
    OAuth2Error,
)

from server import APP
from server.entities.identityprovider import IdentityProvider

from .entities.databases import Databases
from .entities.errors import IdentityProviderError
from .entities.organisation import Organisation
from .services.authentication import (
    UserData,
    authorize,
    find_organisation_by_tag,
    is_authorized,
)
from .services.database import get, getall
from .util import error_page, json_body, web_error, web_response

REMOTE_AUTHENTICATION_TIMEOUT = 5.0


@APP.route("/organisations", methods=["GET"])
def get_organisations():
    identity_providers = [
        IdentityProvider.from_db(identityprovider)
        for identityprovider in getall(Databases.IDENTITYPROVIDERS)
    ]
    identity_provider_stubs = [
        {
            "id": identity_provider.id,
            "name": identity_provider.name,
            "authType": identity_provider.type,
        }
        for identity_provider in identity_providers
    ]
    return web_response(200, details=identity_provider_stubs)


@APP.route("/login-local/<idp_id>", methods=["POST"])
@json_body
def login_local(idp_id: str, username: str, password: str) -> Response:
    try:
        authorize(username, password, idp_id)
    except HTTPError as e:
        return web_response(403, details={"success": False, "reason": e.args[0]})
    except RuntimeError:
        return web_response(
            403, details={"success": False, "reason": "wrong credentials"}
        )

    return web_response(200, details={"success": True})


@APP.route("/login-oidc/<idp_id>", methods=["GET"])
def login_oidc(idp_id: str):
    identity_provider = get_idp_from_db(idp_id)
    try:
        client = oidc_client(identity_provider)
    except IdentityProviderError as error:
        return web_error(500, error.args[0], component="SERVER")
    # create auth request for OIDC-IDP
    az_request = client.authorization_request(scope=identity_provider.scope)
    # save current login attempt data
    session["code_verifier"] = az_request.code_verifier
    session["state"] = az_request.state
    session["nonce"] = az_request.nonce
    # redirect to OIDC login window
    return web_response(200, details={"auth_url": az_request.uri})


@APP.route("/login-oidc-callback/<organisation_id>", methods=["GET"])
def callback_oidc(idp_id: str):
    identity_provider = get_idp_from_db(idp_id)
    client = oidc_client(identity_provider)

    # create auth request from callback URL
    url = request.url
    az_request = client.authorization_request(
        scope=identity_provider.scope,
        state=session["state"],
        code_verifier=session["code_verifier"],
        nonce=session["nonce"],
    )

    # get info of authenticated user after successful authorization
    az_response = az_request.validate_callback(url)
    idp_token = client.authorization_code(az_response)
    userinfo = client.userinfo(idp_token)
    # email = userinfo['email']
    # given_name = userinfo['given_name']
    # family_name = userinfo['family_name']
    # sub = userinfo['sub']
    username = userinfo["username"]

    # remove login attempt ID after successful login
    session.pop("code_verifier")
    session.pop("state")
    session.pop("nonce")

    try:
        user_organisation = user_organisation_from_login(identity_provider, userinfo)
    except RuntimeError as e:
        return error_page(e.args[0])

    user_displayname = username
    if (
        identity_provider.displayname_field is not None
        and identity_provider.displayname_field in userinfo
    ):
        user_displayname = userinfo[identity_provider.displayname_field]

    session["user"] = UserData(
        username=username,
        displayname=user_displayname,
        organisation_id=user_organisation,
    )

    return redirect(url_for("navhome"))


@APP.route("/login-keycloak/<idp_id>", methods=["GET"])
def login_keycloak(idp_id: str):
    identity_provider = get_idp_from_db(idp_id)
    if identity_provider.type != "KEYCLOAK" or identity_provider.client_id is None:
        return error_page(400, ["Invalid login flow."])

    az_request = AuthorizationRequest(
        authorization_endpoint=f"{identity_provider.url}auth",
        client_id=identity_provider.client_id,
        redirect_uri=f"{request.url_root}login-keycloak-callback/{identity_provider.id}",
        scope=identity_provider.scope,
    )
    session["keycloak_state"] = az_request.state
    session["keycloak_nonce"] = az_request.nonce
    session["keycloak_code_verifier"] = az_request.code_verifier

    # redirect to OIDC login window
    return web_response(200, details={"auth_url": az_request.uri})


@APP.route("/login-keycloak-callback/<idp_id>", methods=["GET"])
def callback_keycloak(idp_id: str):
    identity_provider = get_idp_from_db(idp_id)
    if identity_provider.type != "KEYCLOAK" or identity_provider.client_id is None:
        return error_page(400, ["Invalid login attempt."])

    expected_state = session.pop("keycloak_state", None)
    expected_nonce = session.pop("keycloak_nonce", None)
    code_verifier = session.pop("keycloak_code_verifier", None)
    if expected_state is None or expected_nonce is None or code_verifier is None:
        return error_page(400, ["Missing or expired login attempt."])

    az_request = AuthorizationRequest(
        authorization_endpoint=f"{identity_provider.url}auth",
        client_id=identity_provider.client_id,
        redirect_uri=f"{request.url_root}login-keycloak-callback/{identity_provider.id}",
        scope=identity_provider.scope,
        state=expected_state,
        nonce=expected_nonce,
        code_verifier=code_verifier,
    )
    try:
        az_response = az_request.validate_callback(request.url)
    except OAuth2Error as error:
        return error_page(400, [str(error)])

    token_url = f"{identity_provider.url}token"
    token_request_body = {
        "grant_type": "authorization_code",
        "client_id": identity_provider.client_id,
        "redirect_uri": f"{request.url_root}login-keycloak-callback/{identity_provider.id}",
        "code": az_response.code,
        "code_verifier": code_verifier,
    }
    if identity_provider.client_secret is not None:
        token_request_body["client_secret"] = identity_provider.client_secret
    token_response = requests.post(
        token_url, data=token_request_body, timeout=REMOTE_AUTHENTICATION_TIMEOUT
    )
    try:
        token_data = token_response.json()
        access_token = token_data["access_token"]
    except (KeyError, ValueError):
        return error_page(
            400,
            [
                "Could not accquire access token for fetching user info. Organisation IDP-data might be wrong."
            ],
        )

    if not nonce_matches(token_data.get("id_token"), expected_nonce):
        return error_page(400, ["ID token nonce validation failed."])

    userinfo_url = f"{identity_provider.url}userinfo"
    userinfo_response = requests.get(
        userinfo_url,
        headers={"Authorization": f"Bearer {access_token}"},
        timeout=REMOTE_AUTHENTICATION_TIMEOUT,
    )
    userinfo = userinfo_response.json()

    if identity_provider.username_field is None:
        try:
            username = userinfo["username"]
        except KeyError:
            return error_page(
                400,
                [
                    f"No 'username' field or custom field for the organisation found in {userinfo=}"
                ],
            )
    else:
        username = userinfo[identity_provider.username_field]

    try:
        user_organisation = user_organisation_from_login(identity_provider, userinfo)
    except RuntimeError as e:
        return error_page(500, e.args[0])

    user_displayname = username
    if (
        identity_provider.displayname_field is not None
        and identity_provider.displayname_field in userinfo
    ):
        user_displayname = userinfo[identity_provider.displayname_field]

    # create token with info for authenticated user
    session["user"] = UserData(
        username=username,
        displayname=user_displayname,
        organisation_id=user_organisation,
    )

    # redirect to start page and set auth cookie
    return redirect(url_for("navhome"))


def user_organisation_from_login(
    identity_provider: IdentityProvider, userinfo: dict[str, Any]
) -> str:
    errors = []
    user_organisation_tag = ""
    if identity_provider.organisation:
        user_organisation_tag = identity_provider.organisation
    elif identity_provider.organisation_field is not None:
        if identity_provider.organisation_field in userinfo:
            user_organisation_tag = userinfo[identity_provider.organisation_field]
        else:
            errors.append(
                f"Could not log in. Expected '{identity_provider.organisation_field}' in userinfo. Received {userinfo=}"
            )
    else:
        errors.append(
            "Invalid Configuration for IdentityProvider. 'organisation' and 'organisation_field' are not set."
        )

    if user_organisation_tag == "":
        errors.append("User could not be assigned to an organisation.")
        raise RuntimeError(errors)

    user_organisation = find_organisation_by_tag(user_organisation_tag)

    if not user_organisation.id:
        (errors.append("Invalid Configuration."),)
        errors.append(f"Found {user_organisation=}")
        raise RuntimeError(errors)

    return user_organisation.id


def oidc_client(provider: IdentityProvider):
    if provider.client_id is None or provider.client_secret is None:
        raise IdentityProviderError("Missing client id or secret")
    return OAuth2Client.from_discovery_endpoint(
        issuer=provider.url,
        auth=ClientSecretJwt(provider.client_id, provider.client_secret),
        redirect_uri=f"{request.url_root}/login-oidc-callback/{provider.id}",
    )


def get_organisation_from_db(organisation_id: str) -> Organisation:
    org_response = get(Databases.ORGANISATIONS, organisation_id).json()
    return Organisation.from_db(org_response)


def get_idp_from_db(idp_id: str) -> IdentityProvider:
    org_response = get(Databases.IDENTITYPROVIDERS, idp_id).json()
    return IdentityProvider.from_db(org_response)


def nonce_matches(id_token_str: Any, expected_nonce: str) -> bool:
    if not isinstance(id_token_str, str):
        return False
    try:
        token = BearerToken(id_token=id_token_str)
    except InvalidIdToken:
        return False
    if not isinstance(token.id_token, IdToken):
        return False
    token_nonce = token.id_token.get_claim("nonce")
    return isinstance(token_nonce, str) and secrets.compare_digest(
        token_nonce, expected_nonce
    )


@APP.route("/whoami", methods=["GET"])
def whoami():
    data = {
        "name": "",
        "displayname": "Not logged in",
        "organisation": "",
        "reviewer": False,
        "plugins": [],
    }

    if not is_authorized():
        return web_response(200, details=data)

    user: UserData = session["user"]

    return web_response(
        200,
        details={
            "name": user.username,
            "displayname": user.displayname,
            "organisation": user.organisation().name,
            "reviewer": user.reviewer,
            "plugins": user.list_plugins(),
        },
    )

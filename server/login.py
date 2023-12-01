from flask import request, url_for, redirect, Flask, session
import json
from requests_oauth2client import * #OAuth2Client, ClientSecretJwt, BearerTokenSerializer
import os

from server import APP
from .util import web_error, web_response
from .services.authentication import authorize

import time
from datetime import datetime, timedelta, timezone
from binapy import BinaPy

@APP.route("/login", methods=["POST"])
def login_lzv():
    username = json.loads(request.data).get('username')
    password = json.loads(request.data).get('password')
    try:
        token = authorize(username, password, organisation='uni-bayreuth')
    except RuntimeError:
        return web_response(200, details = {'success': False, 'reason': "wrong credentials"})
    return web_response(200, details = {'success': True, 'token': token})

@APP.route("/login_oidc", methods=["POST", "GET"])
def login_oidc():
    # OIDC declaration
    client = OAuth2Client.from_discovery_endpoint(
        issuer=os.getenv("OIDC_IDP"),
        auth=ClientSecretJwt(os.getenv('OIDC_CLIENT_ID'), os.getenv('OIDC_CLIENT_SECRET')),
        redirect_uri=os.getenv('REDIRECT_URI')
    )

    #redirect to sso
    az_request = client.authorization_request(scope=os.getenv('SCOPE'))
    session['code_verifier'] = az_request.code_verifier
    session['state'] = az_request.state
    session['nonce'] = az_request.nonce
    return web_response(200, details={'success':True, 'redirect':az_request.uri})
    
@APP.route("/login_oidc/response")
def oidc_response():
    client = OAuth2Client.from_discovery_endpoint(
        issuer=os.getenv("OIDC_IDP"),
        auth=ClientSecretJwt(os.getenv('OIDC_CLIENT_ID'), os.getenv('OIDC_CLIENT_SECRET')),
        redirect_uri=os.getenv('REDIRECT_URI')
    )
    url= request.url
    #print("hallo", flush=True)
    #print(url, flush=True)
    az_request = client.authorization_request(scope=os.getenv('SCOPE'),
                                              state=session['state'],
                                              code_verifier=session['code_verifier'],
                                              nonce=session['nonce']
                                              )
    az_response = az_request.validate_callback(url)
    token = client.authorization_code(az_response)
                                            
    print(token, flush=True)
    userinfo = client.userinfo(token)
    email = userinfo['email']
    given_name = userinfo['given_name']
    family_name = userinfo['family_name']
    sub = userinfo['sub']
    print ('{} \n {} \n {} \n {}'.format(email, given_name, family_name, sub), flush=True)

    session.pop('code_verifier')
    session.pop('state')
    session.pop('nonce')

    serialize_bearertoken = BearerTokenSerializer()
    token_serialized = serialize_bearertoken.default_dumper(token)
    session["bearer_token"] = token_serialized
    return redirect("/start")

def is_authorized(abc):
    if session.get('bearer_token') is None:
        return False

    serialize_bearertoken = BearerTokenSerializer()
    #token = serialize_bearertoken.default_loader(session['bearer_token'])
    token = load(session['bearer_token'])

    #print(token.expires_in, flush=True)
    print(token.expires_at, flush=True)
    
    print("old \n", flush=True)
    print(token, flush=True)
    
    if token.is_expired(leeway=540):
        
        client = OAuth2Client.from_discovery_endpoint(
            issuer=os.getenv("OIDC_IDP"),
            auth=ClientSecretJwt(os.getenv('OIDC_CLIENT_ID'), os.getenv('OIDC_CLIENT_SECRET'))
        )



        token = client.refresh_token(
            refresh_token = token
        )
        print("new \n", flush=True)
        print(token, flush=True)
        session["bearer_token"] = serialize_bearertoken.default_dumper(token)

    return True

def load(serialized):
    attrs = BinaPy(serialized).decode_from("b64u").decode_from("deflate").parse_from("json")
    #print(attrs, flush=True)
    # if expire_in exist in atters
    del attrs['expires_in']
    attrs["expires_at"] = datetime.fromtimestamp(attrs.get("expires_at"))
    #print(attrs, flush=True)
    return BearerToken(**attrs)
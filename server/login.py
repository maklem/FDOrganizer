from flask import request
import json

from server import APP
from .util import web_error, web_response
from .services.authentication import authorize

from requests_oauth2client import * 
import os

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
        issuer=os.getenv("OIDC_IDP"), #https://sso-test.hm.edu
        auth=ClientSecretJwt(os.getenv('OIDC_CLIENT_ID'), os.getenv('OIDC_CLIENT_SECRET')),
        redirect_uri='https://playground-msagir.cc.private.hm.edu:8080/login_oidc/response',
        code_challenge_method=None,
    )
    if request.method == 'GET':
        #redirect to sso
        az_request = client.authorization_request(scope="openid profile email")
        return web_response(200, details={'success':True, 'redirect':az_request.uri, 'state':az_request.state})
    
    else: 
        #check response
        url = json.loads(request.data).get('url')
        #print(url)
        state_req = json.loads(request.data).get('state') 
        az_request = client.authorization_request(scope="openid profile email",
                                                  state=state_req
                                                  )

        az_response = az_request.validate_callback(url)
        token = client.authorization_code(#az_response)
                                                code=az_response.code,
                                                code_verifier=az_response.code_verifier,
                                                redirect_uri=az_response.redirect_uri
                                                )
        
        userinfo = client.userinfo(token)
        email = userinfo['email']
        given_name = userinfo['given_name']
        family_name = userinfo['family_name']

        print ('{} \n {} \n {}'.format(email, given_name, family_name ) , flush=True)

        #TODO use token from OIDC
        token = authorize("abc", "abc", organisation='uni-bayreuth')
        return web_response(200, details = {'success': True, 'token': token})

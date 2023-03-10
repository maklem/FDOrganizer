from flask import request
import json

from server import APP
from .util import web_error, web_response
from .services.authentication import authorize

@APP.route("/login", methods=["POST"])
def login_lzv():
    username = json.loads(request.data).get('username')
    password = json.loads(request.data).get('password')
    try:
        token = authorize(username, password, organisation='uni-bayreuth')
    except RuntimeError:
        return web_response(200, details = {'success': False, 'reason': "wrong credentials"})
    return web_response(200, details = {'success': True, 'token': token})

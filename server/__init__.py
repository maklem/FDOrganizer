import json
import logging
import logging.handlers
import re
from dotenv import load_dotenv
from flask import Flask, has_request_context, request
from werkzeug.exceptions import HTTPException
from flask_session import Session
from .services.authentication import is_authorized, user

from .util import web_error

APP = Flask(__name__)
APP.config["UPLOAD_FOLDER"] = './uploads'
APP.config["MAX_CONTENT_LENGTH"] = 1_000_000_000
APP.config["APPLICATION_ROOT"] = "/fdorganizer"

APP.config["SESSION_PERMANENT"] = False
APP.config["SESSION_TYPE"] = "filesystem"
Session(APP)

load_dotenv(dotenv_path="../.env")

@APP.errorhandler(HTTPException)
def handle_exception(error):
    return web_error(error.code, f'{error.name}: {error.description}', stacktrace=error.description, component="SERVER")

class CredentialFilter(logging.Filter):
    def filter(self, record):
        record.contains_credentials = False
        if not has_request_context():
            return True
        route = request.path
        if "/login-oidc" in route or "/login-ldap" in route or "/login-local" in route:
            record.contains_credentials = True
        if re.search("/import/.+/login",route):
            record.contains_credentials = True
        return True

class RequestFormatter(logging.Formatter):
    def format(self, record):
        if has_request_context():
            record.url = request.url
            record.type = request.method
            record.username = request.remote_addr
            if is_authorized(request):
                record.username = user(request)
            record.params = '---'
            if not record.contains_credentials and request.is_json: #type: ignore
                jsondata = request.get_json(silent=True)
                if jsondata is not None: 
                    record.params = request.json
        else:
            record.url = None
            record.remote_addr = None

        return super().format(record)

formatter = RequestFormatter(
    '[%(asctime)s] %(username)s %(type)s to %(url)s\n%(params)s',
    datefmt='%d.%m.%y %H:%M:%S'
)
credentialfilter = CredentialFilter()
new_handler = logging.handlers.RotatingFileHandler(
        'server.log',
        maxBytes=15000000,
        backupCount=5)
new_handler.addFilter(credentialfilter)
new_handler.setFormatter(formatter)
APP.logger.addHandler(new_handler)

from . import router,login,metadata,package_details,package,source_import,archive,export, review
from flask import Flask
from werkzeug.exceptions import HTTPException

from .util import web_error

APP = Flask(__name__)
APP.config["UPLOAD_FOLDER"] = './uploads'


@APP.errorhandler(HTTPException)
def handle_exception(error):
    return web_error(error.code, f'{error.name}: {error.description}', stacktrace=error.description, component="SERVER")

import server.router
import server.login
import server.upload
import server.package
import server.source_import

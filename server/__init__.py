import logging
from flask import Flask
from werkzeug.exceptions import HTTPException

from .util import web_error

APP = Flask(__name__)
APP.config["UPLOAD_FOLDER"] = './uploads'
APP.config["MAX_CONTENT_LENGTH"] = 1_000_000_000


@APP.errorhandler(HTTPException)
def handle_exception(error):
    return web_error(error.code, f'{error.name}: {error.description}', stacktrace=error.description, component="SERVER")

logging.basicConfig(level=logging.DEBUG)

import server.router
import server.login
import server.metadata
import server.package_details
import server.package
import server.source_import
import server.archive

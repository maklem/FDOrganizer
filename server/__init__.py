import logging
from dotenv import load_dotenv
from flask import Flask
from werkzeug.exceptions import HTTPException
from flask_session import Session

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

logging.basicConfig(level=logging.DEBUG)
from . import router,login,metadata,package_details,package,source_import,archive,export

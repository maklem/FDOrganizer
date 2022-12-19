import json
from flask import Flask
from werkzeug.exceptions import HTTPException

from server.lzv_util import get_config

APP = Flask(__name__)
APP.config["UPLOAD_FOLDER"] = get_config()["USR_UPLOAD_TMP_FOLDER"]


@APP.errorhandler(HTTPException)
def handle_exception(error):
    """Return JSON instead of HTML for HTTP errors."""
    # start with the correct headers and status code from the error
    response = error.get_response()
    # replace the body with JSON
    response.data = json.dumps({
        "message": f'{error.name} - {error.code}: {error.description}' ,
        "component": "SERVER",
        "stacktrace": error.description,
    })
    response.content_type = "application/json"
    return response

import server.router
import server.upload
import server.lzv_server
import server.source_import

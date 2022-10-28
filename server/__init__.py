from flask import Flask
from flask_cors import CORS
from flask_session import Session

from server.lzv_util import get_config
from server.repoman_easydb import rep_easydb
from server.repoman_labfolder import rep_labfolder

APP = Flask(__name__)
APP.secret_key = "any random string"
APP.config["SESSION_TYPE"] = "filesystem"
APP.config["PERMANENT_SESSION_LIFETIME"] = 43200
APP.config["SESSION_PERMANENT"] = False
APP.config["UPLOAD_FOLDER"] = get_config()["USR_UPLOAD_TMP_FOLDER"]
CORS(APP)
Session(APP)
APP.register_blueprint(rep_labfolder, url_prefix="/labfolder")
APP.register_blueprint(rep_easydb, url_prefix="/easydb")

import server.router
import server.upload
import server.lzv_server

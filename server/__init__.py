from flask import Flask

from server.lzv_util import get_config
from server.repoman_easydb import rep_easydb
from server.repoman_labfolder import rep_labfolder

APP = Flask(__name__)
APP.config["UPLOAD_FOLDER"] = get_config()["USR_UPLOAD_TMP_FOLDER"]
APP.register_blueprint(rep_labfolder, url_prefix="/labfolder")
APP.register_blueprint(rep_easydb, url_prefix="/easydb")

import server.router
import server.upload
import server.lzv_server

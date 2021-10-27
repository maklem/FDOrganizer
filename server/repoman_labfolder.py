from flask import Blueprint, render_template, abort
from jinja2 import TemplateNotFound

rep_labfolder = Blueprint('labfolder', __name__ )

@rep_labfolder.route('/test')
def show():
    print("test")
    print(rep_labfolder.root_path)
    return {"Error": "invalid credentials"}, 401, {"Content-Type": "application/json"}
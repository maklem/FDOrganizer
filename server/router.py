from flask import render_template, request, url_for, redirect
from server import APP
from server.lzv_util import check_user_permission_review, validate_user_session


def needs_authentication():
    return request.path != url_for("navlogin") and "static" not in request.path

@APP.before_request
def auth_guard():
    if not needs_authentication():
        return None
    if not validate_user_session(request):
        return redirect(url_for("navlogin"))
    return None

@APP.route("/")
def navhome():
    return render_template("index.html")


@APP.route("/impressum")
def navimpressum():

    return render_template("impressum.html")


@APP.route("/history")
def navhistory():
    return render_template("history.html")


@APP.route("/labfolder")
def navlabfolder():
    return render_template("labfolder.html")


@APP.route("/easydb")
def naveasydb():

    return render_template("easydb.html")


@APP.route("/metadata")
def navmetadata():
    return render_template("metadata.html")


@APP.route("/lzv")
def navlzvingest():
    return render_template("lzvingest.html")


@APP.route("/package")
def navlzvpackage():
    return render_template("lzvpackage.html")


@APP.route("/upload")
def navupload():
    return render_template("upload.html")


@APP.route("/review")
def navlzvreview():
    if not check_user_permission_review(request.cookies["session_user"]):
        return render_template("index.html")
    return render_template("lzvreview.html")


@APP.route("/login", methods=["GET"])
def navlogin():
    if validate_user_session(request):
        return redirect(url_for("navhome"))
    return render_template("login.html")

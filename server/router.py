from flask import render_template, request, url_for, redirect
from server import APP
from .services.authentication import is_authorized


def needs_authentication(route: str) -> bool:
    return route not in [url_for("navlogin"), url_for('get_organisations')] and "static" not in route and "/login-oidc" not in route and "/login-ldap" not in route

@APP.before_request
def auth_guard():
    if not needs_authentication(request.path):
        return None
    if not is_authorized(request):
        return redirect(url_for("navlogin"))
    return None

@APP.route("/")
def navhome():
    return redirect(url_for("navindex"))

@APP.route("/start")
def navindex():
    return render_template("index.html")

@APP.route("/impressum")
def navimpressum():
    return render_template("impressum.html")

@APP.route("/history")
def navhistory():
    return render_template("history.html")

@APP.route("/package")
def navpackage():
    return render_template("package.html")

@APP.route("/package/<id>")
def navpackageedit(id):
    return render_template("package-edit.html")

@APP.route("/archive")
def navarchive():
    return render_template("archive.html")

@APP.route("/login")
def navlogin():
    if is_authorized(request):
        return redirect(url_for("navhome"))
    return render_template("login.html")

@APP.route("/test")
def navtest():
    if is_authorized(request):
        return redirect(url_for("navhome"))
    return render_template("test.html")

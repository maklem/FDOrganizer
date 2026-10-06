import os

import jinja2.exceptions
from flask import redirect, render_template, request, url_for

from server import APP

from .services.authentication import is_authorized, is_reviewer


def needs_authentication(route: str) -> bool:
    return not any([
        route.startswith(url_for("navlogin")),
        route.startswith(url_for("navlogout")),
        route.startswith(url_for('get_organisations')),
        route.startswith("/static"),
        route.startswith("/info/"),
        route.startswith("/whoami"),
        route.startswith("/login-oidc"),
        route.startswith("/login-local"),
        route.startswith("/login-keycloak"),
    ])

@APP.before_request
def request_logger():
    if "static" not in request.path:
        APP.logger.info('Request')
    return None

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

@APP.route("/info/source")
def navsource():
    if os.getenv("SOURCE_LINK") is not None:
        return redirect(str(os.getenv("SOURCE_LINK")))
    return render_template("missing-link.html")

@APP.route("/info/impressum")
def navimpressum():
    if os.getenv("IMPRESSUM_LINK") is not None:
        return redirect(str(os.getenv("IMPRESSUM_LINK")))
    return render_template("missing-link.html")

@APP.route("/info/datenschutz")
def navdatenschutz():
    if os.getenv("DATENSCHUTZ_LINK") is not None:
        return redirect(str(os.getenv("DATENSCHUTZ_LINK")))
    return render_template("missing-link.html")

@APP.route("/info/a11y")
def navbarrierefreiheit():
    if os.getenv("BARRIEREFREIHEIT_LINK") is not None:
        return redirect(str(os.getenv("BARRIEREFREIHEIT_LINK")))
    return render_template("missing-link.html")

@APP.route("/info/tos")
def navtos():
    TOS_FILE="terms-of-service.html"
    try:
        return render_template(TOS_FILE)
    except jinja2.exceptions.TemplateNotFound as e:
        APP.logger.error("Terms of Service not found. Please add your terms as 'server/templates/terms-of-service.html'")
        return render_template("terms-of-service-missing.html")

@APP.route("/package")
def navpackage():
    return render_template("package.html")

@APP.route("/package/<id>")
def navpackageedit(id):
    return render_template("package-edit.html")

@APP.route("/archive")
def navarchive():
    return render_template("archive.html")

@APP.route("/review")
def navreview():
    if not is_reviewer(request):
        return redirect(url_for("navhome"))
    return render_template("review.html")

@APP.route("/login")
def navlogin():
    if is_authorized(request):
        return redirect(url_for("navhome"))
    return render_template("login.html")

@APP.route("/logout", methods=['POST'])
def navlogout():
    response = redirect("/login")
    response.delete_cookie("token")
    return response

import json
from typing import Literal
from flask import Response, request
from requests import HTTPError #type: ignore
from server import APP
from .entities import Review, Comment, Package, Databases
from .services.database import find, get, post, update
from .services.authentication import is_reviewer, organisation, user
from .util import can_read, json_body, web_error, web_response, is_owner


@APP.route("/review/packages", methods=["GET"])
def get_review_packages():
    if not is_reviewer(request):
        return web_error(401, "You don't have permission to view this content", component= "SERVER")
    query = {
        "selector": {
            "organisation": organisation(request),
            "status": {"$in": ["rework", "review", "archived"]}
        }
    }

    try:
        packages = find(Databases.PACKAGES, json.dumps(query)).json().get('docs')
    except HTTPError as error:
        return web_error(error.response.status_code, error.response.reason, component= "DATABASE")
    return web_response(200, details = [Package.convert(x) for x in packages])

@APP.route("/review/<package_id>", methods=["GET"])
def get_package_reviews(package_id) -> Response:
    package = get(Databases.PACKAGES, package_id).json()
    if not can_read(package, request) or is_reviewer(request):
        return web_error(401, "You don't have permission to view this package", component= "SERVER")
    query = {
        "selector": {
            "package_id": package_id
       }
    }

    try:
        reviews = find(Databases.REVIEWS, json.dumps(query)).json().get('docs')
    except HTTPError as error:
        return web_error(error.response.status_code, error.response.reason, component= "DATABASE")
    if not is_reviewer(request):
        reviews = [review for review in reviews if review.status != "open"]
        return web_error(401, "You don't have permission to view this content", component= "SERVER") 
    return web_response(200, details = [Review.convert(x) for x in reviews])

@APP.route("/review/<package_id>", methods=["PUT"])
@json_body
def post_new_review(package_id: str, comments: list[dict[str, str]] | None = None) -> Response:
    if not is_reviewer(request):
        return web_error(401, "You don't have permission to review packages", component= "SERVER")
    review = Review(package_id=package_id, status="open", comments=[])
    if comments is not None:
        review.comments = [Comment(index = comment['index'], content=comment['content'], owner=user(request)) for comment in comments]
    try:
        review_created = post(Databases.REVIEWS, review.to_json())
    except HTTPError as error:
        return web_error(error.response.status_code, error.response.reason, component= "DATABASE")
    return web_response(200, 'Success', review_created.json())

@APP.route("/review/<review_id>/comment/", methods=["PUT"])
def post_new_comment(review_id: str, comment: dict[str, str]) -> Response:
    if not is_reviewer(request):
        return web_error(401, "You don't have permission to review packages", component= "SERVER")
    changes = {
        "comments": {
            "method": 'append',
            "value": Comment(index = comment['index'], content=comment['content'], owner=user(request))
        }
    }
    try:
        update(Databases.REVIEWS, review_id, changes)
    except HTTPError as error:
        return web_error(error.response.status_code, error.response.reason, component= "DATABASE")
    return web_response(200, 'Success')

@APP.route("/review/<review_id>/<comment_index>", methods=["DELETE"])
def delete_comment(review_id, comment_index):
    if not is_reviewer(request):
        return web_error(401, "You don't have permission to review packages", component= "SERVER")
    review = Review.from_db(get(Databases.REVIEWS, review_id).json())
    comment_to_delete = [comment for comment in review.comments if comment.index == comment_index][0]
    if not is_owner(comment_to_delete.to_dict(), request):
        return web_error(401, "You don't have permission to delete this comment", component= "SERVER")
    updated_comments = [comment for comment in review.comments if comment.index != comment_index]
    changes = {
        "comments": {
            "method": 'replace',
            "value": updated_comments
        }
    }
    try:
        update(Databases.REVIEWS, review_id, changes)
    except HTTPError as error:
        return web_error(error.response.status_code, error.response.reason, component= "DATABASE")
    return web_response(200, 'Success')

@APP.route("/review/<package_id>/<review_id>", methods=["POST"])
def submit_review(package_id: str, review_id: str, status: Literal["accepted", "rejected"]) -> Response:
    if not is_reviewer(request):
        return web_error(401, "You don't have permission to review packages", component= "SERVER")
    
    return web_error(501, "Not implemented", component= "SERVER")
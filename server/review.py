from datetime import datetime
import json
from typing import Any, Literal
from flask import Response, request
from requests import HTTPError #type: ignore
from server import APP
from .shared import update_package_state
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
    if not can_read(package, request) and not is_reviewer(request):
        return web_error(401, "You don't have permission to view this package", component= "SERVER")

    try:
        reviews = get_reviews(package.get("reviews"))
    except HTTPError as error:
        return web_error(error.response.status_code, error.response.reason, component= "DATABASE")
    if not is_reviewer(request):
        reviews = [review for review in reviews if review.status != "open"]
    return web_response(200, details = [x.to_dict() for x in reviews])

@APP.route("/review/<package_id>", methods=["PUT"])
@json_body
def post_new_review(package_id: str, comments: list[dict[str, Any]] | None = None) -> Response:
    # Check if user is a reviewer
    if not is_reviewer(request):
        return web_error(401, "You don't have permission to review packages", component= "SERVER")
    # Check if package can be reviewed
    package = Package.from_db(get(Databases.PACKAGES, package_id).json())
    if not package.status == 'review':
        return web_error(400, f'Review cannot be submitted for package in status {package.status}', component="SERVER")
    # Check if there is an open review
    if not not package.reviews:
        reviews = get_reviews(package.reviews)
        if any(review.status == 'open' for review in reviews):
            return web_error(400, "Cannot create new review for package with open review", component= "SERVER")
    # Create new review
    review = Review(status="open", comments=[])
    # Add comments
    if comments is not None:
        review.comments = [Comment(index = comment['index'], content=comment['content'], owner=user(request)) for comment in comments]
    try:
        post_response = post(Databases.REVIEWS, review.to_json()).json()
        created_review = get(Databases.REVIEWS, post_response.get('id')).json()
        created_review = Review.from_db(created_review)
    except HTTPError as error:
        return web_error(error.response.status_code, error.response.reason, component= "DATABASE")
    # Update package with new review
    try:
        update(Databases.PACKAGES, package_id, {
            "reviews": {
                "method": 'append',
                "value": created_review.id
            }
        })
    except HTTPError as error:
        return web_error(error.response.status_code, error.response.reason, component= "DATABASE")
    return web_response(200, 'Success', created_review.to_dict())

@APP.route("/review/<review_id>/comment/", methods=["PUT"])
@json_body
def post_new_comment(review_id: str, index: int, content: str) -> Response:
    if not is_reviewer(request):
        return web_error(401, "You don't have permission to review packages", component= "SERVER")
    review: Review = Review.from_db(get(Databases.REVIEWS, review_id).json())
    if not review.status == 'open':
        return web_error(400, "Cannot add comment to review with status {review.status}", component= "SERVER")
    new_comment = Comment(index = index, content=content, owner=user(request))
    changes = {
        "comments": {
            "method": 'append',
            "value": new_comment.to_dict()
        }
    }
    try:
        update(Databases.REVIEWS, review_id, changes)
    except HTTPError as error:
        return web_error(error.response.status_code, error.response.reason, component= "DATABASE")
    return web_response(200, details = Comment.convert(new_comment.to_dict()))

@APP.route("/review/<review_id>/<comment_index>", methods=["DELETE"])
def delete_comment(review_id: str, comment_index: int):
    if not is_reviewer(request):
        return web_error(401, "You don't have permission to review packages", component= "SERVER")
    review = Review.from_db(get(Databases.REVIEWS, review_id).json())
    if not review.status == 'open':
        return web_error(400, "Cannot delete comment from review with status {review.status}", component= "SERVER")
    comment_to_delete = [comment for comment in review.comments if comment.index == int(comment_index)][0]
    if not comment_to_delete:
        return web_error(400, "No comment with index {comment_index} found in review {review_id}", component= "SERVER")
    # if not is_owner(comment_to_delete.to_dict(), user(request)):
    #     return web_error(401, "You don't have permission to delete this comment", component= "SERVER")
    updated_comments = [comment for comment in review.comments if comment.index != int(comment_index)]
    changes = {
        "comments": {
            "method": 'replace',
            "value": json.loads(Comment.schema().dumps(updated_comments, many=True))
        }
    }
    try:
        update(Databases.REVIEWS, review_id, changes)
    except HTTPError as error:
        return web_error(error.response.status_code, error.response.reason, component= "DATABASE")
    return web_response(200, 'Success')

@APP.route("/review/submit/<package_id>", methods=["POST"])
@json_body
def submit_review(package_id: str, status: Literal["accepted", "rejected"]) -> Response:
    if not is_reviewer(request):
        return web_error(401, "You don't have permission to review packages", component= "SERVER")
    package = Package.from_db(get(Databases.PACKAGES, package_id).json())
    if not package.status == 'review':
        return web_error(400, "Review cannot be submitted for package in status {}".format(package.status), component= "SERVER")
    query = {
        "selector": {
            "_id": {
                "$in": package.reviews
            },
            "status": "open"
       }
    }
    result = find(Databases.REVIEWS, json.dumps(query)).json().get('docs')[0]
    if result == None:
        if status == "rejected":
            return web_error(400, "No open review found for package", component= "SERVER")
        elif status == "accepted":
            return web_response(200, 'Success')
    review = Review.from_db(result)
    if status == "accepted":
        update(Databases.REVIEWS, review.id, {
            "status": "accepted",
            "creation_date": datetime.now().timestamp()
        })
    elif status == "rejected":
        update(Databases.REVIEWS, review.id, {
            "status": "rejected",
            "creation_date": datetime.now().timestamp()
        })
        update_package_state(package_id, 'rework')
    return web_response(200, 'Success')
    
def get_reviews(review_ids: list[str]) -> list[Review]:
    query = {
        "selector": {
            "_id": {
                "$in": review_ids
            }
       }
    }

    reviews = find(Databases.REVIEWS, json.dumps(query)).json().get('docs')
    if reviews is None:
        reviews = []
    return [Review.from_db(x) for x in reviews]

    
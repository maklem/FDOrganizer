from flask import jsonify, make_response, request
from requests import HTTPError, Response
from .services.authentication import user

from server.db_connector import attach, post
from server.entities.databases import Databases
from server.entities.document import CouchDocument
from server.entities.file import File
from server import APP


@APP.route("/upload/file", methods=["POST"])
def receive_file():
    """
    Receive files belonging to a package. This is definied by package_id in parameteres. It
    needs to check if the package is manually created AND belonging to the right user.
    """
    if request.files.get("file") is None:
        return make_response(jsonify({
            'title': 'Server Error',
            'text': 'No file content'
        }), 400)
        # Put here some other checks (security, file length etc...)
    file = request.files["file"]
    if not file.filename:
        return make_response(jsonify({
            'title': 'Server Error',
            'text': 'No filename available'
        }), 400)
    # file.save(f'{lzv_util.get_config()["tempFolder"]}/{secure_filename(file.filename)}')
    metadata = File(name=file.filename or "", size=file.content_length,
                    mimetype=file.mimetype, origin="manual", is_stored=True, owner=user(request))
    try:
        success = create_document_with_attachement(file, metadata)
    except HTTPError as error:
        return make_response(jsonify({
            'title': error.response.reason,
            'method': error.request.method,
            'url': error.request.url
        }), error.response.status_code)
    return make_response(jsonify({
        "result": success.json(),
        "file": file.filename
    }), 200)


def create_document_with_attachement(file, metadata: File) -> Response:
    document_created = post(Databases.DOCUMENTS,
                            metadata.to_json())  # type: ignore
    document_created.raise_for_status()

    document = CouchDocument(document_created.json())

    attachment_response = attach(Databases.DOCUMENTS, document, file)
    attachment_response.raise_for_status()

    return attachment_response

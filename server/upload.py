from flask import request
from requests import HTTPError, Response

from .util import web_error, web_response
from .services.authentication import user

from server.services.database import attach, post
from .entities.databases import Databases
from .entities.couch_document import CouchDocument
from .entities.document import Document
from server import APP


@APP.route("/upload/file", methods=["POST"])
def receive_file():
    """
    Receive files belonging to a package. This is definied by package_id in parameteres. It
    needs to check if the package is manually created AND belonging to the right user.
    """
    if request.files.get("file") is None:
        return web_error(400, 'No file content detected')
        # Put here some other checks (security, file length etc...)
    file = request.files["file"]
    if not file.filename:
        return web_error(400, 'No filename available')
    # file.save(f'{lzv_util.get_config()["tempFolder"]}/{secure_filename(file.filename)}')
    metadata = Document(name=file.filename or "", size=file.content_length,
                    mimetype=file.mimetype, origin="manual", is_stored=True, owner=user(request))
    try:
        success = create_document_with_attachement(file, metadata)
    except HTTPError as error:
        return web_error(error.response.status_code, error.response.reason, component= "DATABASE")
    return web_response(200, 'Success', success.json() | {"file": file.filename})


def create_document_with_attachement(file, document: Document) -> Response:
    document_created = post(Databases.DOCUMENTS,
                            document.to_json())  # type: ignore
    document_created.raise_for_status()

    response_document = CouchDocument(document_created.json())

    attachment_response = attach(Databases.DOCUMENTS, response_document, file)
    attachment_response.raise_for_status()

    return attachment_response

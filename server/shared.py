from datetime import datetime
from typing import List, Literal
from requests import HTTPError #type: ignore

from .entities import Document, Databases, CouchDocument

from .util import get_database_from_string
from .services.database import attach, delete, get, update, post

def delete_folder(id: str) -> bool:
    folder = get(Databases.FOLDERS, id).json()
    failed_subfolders = []
    failed_documents = []

    # Delete subfolders, rollback for all if failed
    for subfolder in folder.get('folders'):
        try:
            if not delete_folder(subfolder):
                failed_subfolders.append(subfolder)
        except BaseException:
            failed_subfolders.append(subfolder)
    if len(failed_subfolders) > 0:
        # TODO: Rollback for deletion 
        return False
    
    # Delete documents, rollback for all if failed
    for document in folder.get('documents'):
        try:
            if not delete_document(document):
                failed_documents.append(document)
        except BaseException:
            failed_documents.append(document)
    if len(failed_documents) > 0:
        # TODO: Rollback for deletion 
        return False
    
    # Delete metadata of folder, rollback for all, if failed
    if folder.get('metadata') is not None:
        try:
            delete(Databases.METADATA, folder.get('metadata'))
        except BaseException:
            # TODO: Rollback for deletion 
            return False
        
    # Delete the folder itself
    try:
        delete(Databases.FOLDERS, id)
    except BaseException:
        # TODO: Rollback for deletion 
        return False

    return True
    
def delete_document(id: str) -> bool:
    document = get(Databases.DOCUMENTS, id).json()

    # Delete metadata of document
    if document.get('metadata') is not None:
        try:
            delete(Databases.METADATA, document.get('metadata'))
        except BaseException:
            return False
        
    # Delete the document itself
    try:
        delete(Databases.DOCUMENTS, id)
    except BaseException:
        # TODO: Rollback for deletion 
        return False

    return True

def persist_documents(doc_file_pairs: List, parent, parent_type):    
    documents: dict[str, list[dict[str, str]]] = {
        'failed': [],
        'success': []
    }
    for pair in doc_file_pairs:
        try:
            document_id = create_document_with_attachement(pair['file'], pair['document'])
            documents['success'].append({'file': pair['document'].name, 'document_id': document_id})
        except BaseException as error:
            documents['failed'].append({'file': pair['document'].name, 'error': error.args[0]})

    #Update parent to include documents
    new_documents = [x['document_id'] for x in documents['success'] if x.get('document_id') is not None]
    changes = {
        "documents": {
            "method": 'extend',
            "value": new_documents
        }
    }
    try:
        update(get_database_from_string(parent_type), parent, changes)
        # TODO: Get package id for modify_package()
    except HTTPError as error:
        # Delete new documents on error
        for doc in new_documents:
            delete_document(doc)
        for document in documents['success']:
            del document['document_id']
            document['error'] = 'Parent Entity could not be updated'
        return {'failed': [documents['failed'], documents['success']], 'success': []}
    return documents

def create_document_with_attachement(file, document: Document) -> str:
    # Create initial document in DB
    document_created = post(Databases.DOCUMENTS,document.to_json())  # type: ignore
    # Attach uploaded file to created document
    response_document = CouchDocument(document_created.json())
    attach(Databases.DOCUMENTS, response_document, file_content = file, filename = document.name, mimetype=document.type)

    return response_document.id

def update_package_state(package_id: str, package_state: Literal['active', 'archived', 'review', 'rework']):
    changes = {
        'status': package_state,
        'last_changed': int(datetime.now().timestamp() * 1000)
    }
    update(Databases.PACKAGES, package_id, changes=changes)
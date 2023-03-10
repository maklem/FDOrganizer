from .entities.databases import Databases
from .services.database import delete, get

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
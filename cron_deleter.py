from datetime import datetime, timedelta
from dotenv import load_dotenv

from server.package import delete_folder, delete_document
from server.entities import Databases, Package
from server.services.database import get, getall, delete

load_dotenv(dotenv_path=".env")

now = datetime.now()
delete_before = {
    "active":   now - timedelta(days=7),
    "review":   now - timedelta(days=7),
    "rework":   now - timedelta(days=7),
    "archived": now - timedelta(days=1),
}

def delete_package(package_id):
    package = get(Databases.PACKAGES, package_id).json()

    failed_folders = []
    failed_documents = []

    # Delete folders, rollback for all if failed
    for folder in package.get('folders'):
        try:
            if not delete_folder(folder):
                failed_folders.append(folder)
        except HTTPError as error:
            print(f"Error deleting folder: {error.response.status_code} - {error.response.reason}")
            failed_folders.append(folder)

    # Delete documents, rollback for all if failed
    for document in package.get('documents'):
        try:
            if not delete_document(document):
                failed_documents.append(document)
        except HTTPError as error:
            print(f"Error deleting document: {error.response.status_code} - {error.response.reason}")
            failed_documents.append(document)

    # Delete metadata of folder, rollback for all, if failed
    if package.get('metadata') is not None:
        try:
            delete(Databases.METADATA, package.get('metadata'))
        except HTTPError as error:
            print(f"Error deleting metadata: {error.response.status_code} - {error.response.reason}")

    # Delete the folder itself
    try:
        package_deleted = delete(Databases.PACKAGES, package_id).json()
    except HTTPError as error:
        print(f"Error deleting package: {error.response.status_code} - {error.response.reason}")

packages = [Package.from_db(x) for x in getall(Databases.PACKAGES)]
for package in packages:
    print(f"{package.id} - {package.name}")
    created = datetime.fromtimestamp(package.created/1000)
    print(f"Created: {created.isoformat()}")
    changed = datetime.fromtimestamp(package.last_changed/1000)
    print(f"Changed: {changed.isoformat()}")
    print(f"Owner:   {package.owner}")
    print(f"Status:  {package.status}")
    
    if changed < delete_before[package.status]:
        print(" -> delete")
        delete_package(package.id)
    else:
        print(" -> keep")

    print("")


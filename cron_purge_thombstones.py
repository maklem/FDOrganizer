import os
from dotenv import load_dotenv
from couchdb import Server, Database
import couchdb

def purge_thombstones(database: Database):
    try:
        deletions = database.changes(since='0', include_docs='true')
    except couchdb.http.ResourceNotFound as e:
        print(e)
        return
    
    for d in deletions["results"]:
        if not d.get("deleted"):
            print(f"keeping {d['id']}")
            continue
        doc = d['doc']
        print(f"purging {doc=}")
        database.purge([doc])

load_dotenv(dotenv_path=".env")

user = f'{os.getenv("COUCHDB_USER")}'
password = f'{os.getenv("COUCHDB_PASSWORD")}'
host = f'{os.getenv("COUCHDB_HOST")}'
port = f'{os.getenv("COUCHDB_PORT")}'

COUCHDB_SERVER = f'http://{user}:{password}@{host}:{port}/'
DATABASE_NAMES = [
    "documents",
    "folders",
    "metadata",
    "packages",
]

server = Server(COUCHDB_SERVER)

for db in server:
    print("database -> ", db, db in DATABASE_NAMES)

for db in DATABASE_NAMES:
    print(f"For {db} purge ...")
    purge_thombstones(server[db])



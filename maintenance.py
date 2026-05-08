'''
    Script for creating a new couchDB Database
'''
import os
import sys
from dotenv import load_dotenv
import json
import couchdb
from server.entities.databases import Databases

def getenv(key: str) -> str:
    val = os.getenv(key)
    if not val:
        raise ValueError(f"Could not find {key} in environment. Is not defined or empty.")
    return val

def connect_couchdb() -> couchdb.Server:
    user = getenv("COUCHDB_USER")
    password = getenv("COUCHDB_PASSWORD")
    host = getenv("COUCHDB_HOST")
    port = getenv("COUCHDB_PORT")

    COUCHDB_SERVER = f'http://{user}:{password}@{host}:{port}/'
    return couchdb.Server(COUCHDB_SERVER)

def print_help():
    import textwrap
    print(textwrap.dedent("""
    ---- FDOrganizer Maintenance Tool ----

    Usage: python3 maintenance.py [command] [Options...]

    Commands:
        databases
            Lists expected databases, creates missing ones.

        populate [Database] [File]
            Inserts contents of [File] into [Database]. In case [File] is a List,
            each element is inserted into the database.
            Examples
                uv run maintenance.py populate organisations dummy_organisation.json
                uv run maintenance.py populate identityproviders dummy_local_idp.json
                uv run maintenance.py populate users dummy_local_users.json
    """
))

def populate(server: couchdb.Server, args: list[str]) -> bool:
    if len(args) != 2:
        print("populate: invalid arguments")
        return False
    database, filename = args
    if database not in server:
        print("Can not populate database: No such database in server.")

    with open(filename) as f:
        contents = json.load(f)
    
    if isinstance(contents, list):
        for entry in contents:
            server[database].save(entry)
    else:
        server[database].save(contents)
    return True


def reset_database(server: couchdb.Server, args) -> None:
    database = args[0]
    found = database in server
    if not found:
        print(f"Could not find database {database} for reset. Stop.")
        return
    server.delete(database)
    server.create(database)
    print(f"Reset database {database}.")


def create_databases(server: couchdb.Server) -> None:
    def _ensure_database(server: couchdb.Server, database: str):
        found = database in server
        if not found:
            server.create(database)
        print(f"{database:20s} {'OK' if found else 'Created':>8s}")

    for db in ["_users", "_replicator", "_global_changes"]:
        _ensure_database(server, db)

    for db in Databases:
        _ensure_database(server, db.value)

if __name__ == '__main__':
    if len(sys.argv) == 1 or "--help" in sys.argv:
        print_help()
        sys.exit()

    load_dotenv()
    try:
        server = connect_couchdb()
    except ValueError as e:
        print("Could not connect to couchdb.")
        print(e.args[0])

    if sys.argv[1] == "databases":
        create_databases(server)
    elif sys.argv[1] == "populate":
        populate(server, sys.argv[2:])
    elif sys.argv[1] == "reset":
        reset_database(server, sys.argv[2:])
    else:
        print_help()
        sys.exit()

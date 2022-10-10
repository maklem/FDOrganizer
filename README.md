# LZV 

Projekt LZV des Bibliotheksverbund Bayern
## Installation
### Voraussetzungen

* Python 3.X ist installiert
* pip ist installiert
* Venv für die App ist vorhanden
* CouchDB-Instanz ist vorhanden
* CouchDB-Nutzer mit Berechtigung zum Anlegen von Datenbanken ist verfügbar

### Schritte

1. Aktivieren des venv 

    1. Linux
    
         ```bash
        source .venv/bin/activate
        ```
    
    2. Windows
    
        ```
        .venv\Scripts\activate.bat
        ```

1. Installation der Abhängigkeiten am Server (siehe `requirements.txt`)

    `pip install -r`

1. Installation des ldap-binaries

    1. Für Windows

        `pip install python_ldap-3.4.0-cp310-cp310-win_amd64.whl`

    2. Für Linux/macOS siehe [hier](https://www.python-ldap.org/en/python-ldap-3.3.0/installing.html)

1. Konfigurieren der CouchDB Zugangsdaten in `.server/conf/config.json`

    ```json
    {
        "couchDBBaseURL": "protocol[http|https]://host:port",
        "couchDBAdmin": "username",
        "couchDBPassword": "password"
    }
    ```

1. Erstellen von Datenbanken

    Datenbanken können mit Hilfe des Scripts *create_database* erstellt werden.

    ```python
        python create_database.py <database_name>
    ```
    Wird kein Name beim Start des Skripts übergeben, wird dieser nachträglich abgefragt.
    Die Namen der Datenbank können frei gewählt werden.
    Dadurch werden Namenskonflikte auf bestehenden Server-Instanzen vermieden.

1. Konfiguration der Datenbanken

    Nach dem Erstellen muss das Matching zwischen Datenbank <-> und gespeicherter Entität in der Konfiguration hinterlegt werden

    ```json
    {
        "couchDBStorageDatabaseName": "storage",
        "couchDBMetaDataDatabaseName": "metadata",
        "couchDBDocumentDatabaseName": "documents",
        "couchDBStaticDatabaseName": "static",
        "couchDBIngestsDatabaseName": "ingests",
        "couchDBIngestReviewDatabaseName": "ingest_review"
    }
    ```
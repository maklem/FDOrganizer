# LZV 

Projekt LZV des Bibliotheksverbund Bayern
## Installation
### Voraussetzungen

* Python in Version >=3.9 ist installiert
* pip ist installiert
* Virtual Environment für die App ist vorhanden
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

    `pip install -r requirements.txt`

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
    Die Namen der benötigten Datenbanken können in der Datei `server/entities/databases.py` eingesehen werden.

## Betrieb

### Lokal

Zum lokalen Ausführen der App können entweder das [Flask CLI](https://flask.palletsprojects.com/en/2.2.x/cli/) oder die Startskripte benutzt werden.
Die Startskripte starten die App im Debug-Modus und nutzen die mitgelieferten Self-Signed-Certificates zur ssl-Verschlüsselung.

* Windows

    Start via `./start.bat`

* Linux

    Start via `./start.sh` oder `sh start.sh`

## Wartung

### Datenbanken verwalten

* Zurücksetzen von Datenbanken

    Während der Entwicklung in einer Testinstanz kann es Sinn machen, die Datenbanken des FDOrganizer zu leeren um keine überholten Daten zu nutzen.
    Dazu kann das Skript zum zurücksetzen der Datenbanken genutzt werden.

    ```python
        python reset_database.py <database_name>
    ```

    Wird der Name beim Start des Skripts nicht übergeben, wird dieser nachträglich abgefragt.

## Struktur

### Aufbau der Applikation

![Aufbau FD Organizer](structure.svg)

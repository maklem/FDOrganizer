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

1. Konfigurieren der CouchDB Zugangsdaten in `.env`-Datei

    1. Erstellen einer Datei im Projektverzeichnis mit dem Namen `.env`

    2. Setzen von Umgebungsvariablen, die für die Interaktion des FDOrganizer mit der Datenbank nötig sind (hier mit Beispielwerten)

        ```
        COUCHDB_USER=admin
        COUCHDB_PASSWORD=admin
        COUCHDB_HOST=127.0.0.1
        COUCHDB_PORT=5984
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

### Docker

Für das Setup via docker wird eine funktionierende Installation der Docker Engine sowie des Docker Compose Plugins benötigt.

1. Setzen von Datenbanknutzer und -passwort wie unter [Installation -> Schritte](#schritte) beschrieben.

2. Port Mapping für Datenbank und FDO in `docker-compose.yml` anpassen

    * Die Syntax für die Ports ist *hostsystem:container*.

    * Standardmäßig nutzt CouchDB Port **5984**, der FDO nutzt Port **5000**.

3. Die benötigten Datenbanken und deren Setup wird beim ersten Starten des FDO-Containers ausgeführt (siehe [`init.sh`](./init.sh))

4. Wird das compose plugin für Docker zum Starten genutzt, kann der Cluster über `docker compose up` gestartet werden.

5. Die Default-Namen der Container können auch in `docker-compose.yml` angepasst werden mit dem Property `container_name`.

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

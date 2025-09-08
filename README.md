# LZV 

Projekt LZV des Bibliotheksverbund Bayern

## Beschreibung

Der FDOrganizer (kurz für Forschungsdatenorganizer) ist eine Webapplikation, die genutzt werden kann, um

1. Daten von einem Computer hochzuladen oder

1. mithilfe eines Plugins aus einem Storage-System (elektronisches Laborbuch, Gitlab) zu importieren und

3. die Daten mit Metadaten für die Archivierung anzureichern, um sie dann

4. von einem Datenkurator prüfen zu lassen. Sind die Daten geprüft, werden

5. die Daten für die Archivierung paketiert und für das Archivsystem (z.B. Rosetta) zum Import bereitgestellt

## Struktur

### Aufbau der Applikation

![Aufbau FD Organizer](structure.svg)

## Konfiguration

1. Konfigurieren der CouchDB Zugangsdaten in `.env`-Datei

    1. Erstellen einer Datei im Projektverzeichnis mit dem Namen `.env`

    2. Setzen von Umgebungsvariablen, die für die Interaktion des FDOrganizer mit der Datenbank nötig sind (hier mit Beispielwerten)

        ```
        COUCHDB_USER=admin
        COUCHDB_PASSWORD=admin
        COUCHDB_HOST=127.0.0.1
        COUCHDB_PORT=5984
        ```

1. Setzen von Umgebungsvariablen für den export von Datenpaketen in der .env-Datei

    1. Setzen eines Target-Verzeichnisses für exportierte Datenpakete in den Umgebungsvariablen

        ```
        EXPORT_DIR=/directory/for/exported/packages
        ```

    1. OPTIONAL: Erstellen eines linux-Nutzers für das Handling von exportierten Datenpaketen. Für das Einrichten eines sicheren Zugriffs auf die exportierten Daten via **SFTP** siehe z.B. [hier](https://thunderysteak.github.io/sftp-user-chroot)

        1. Überprüfe die ID des neu erstellten Linux-Nutzers

            ```bash
            id -u NUTZERNAME
            ```

        1. Setzen der Linux-Nutzer-ID in den Umgebungsvariablen
        
            ```
            EXPORT_USER=NUTZER_ID
            ```

1. Setzen von Umgebungsvariable für Impressum-Link

    * Um ein externes impressum einzubinden muss eine Umgebungsvariable in `.env` hinzugefügt werden, die den Hyperlink zum Impressum enthält:

        ```
        IMPRESSUM_LINK=https://localhost:5000/impressum
        ```

    * Wird diese Variable nicht gesetzt, wird automatisch das HTML-Template `impressum.html` gerendert, das sich in `server/templates/` befindet.

1. Setzen von Umgebungsvariable für das Login-Secret

    Beim Login in den FDOrganizer wird ein JWT-Token erstellt und im Browser gespeichert. Es dient zur Authentifizierung des Nutzers für alle weiteren HTTP-Anfragen die der FDOrganizer durchführt. Der Key sollte mindestens 512 Bit (also 64 Byte) lang sein.

    1. OPTIONAL: Erstellen des Secret Keys mit openssl

        ```
        openssl rand -base64 64
        ```

    1. Setzen des Secret Keys in `.env`

        ```
        TOKEN_SECRET=EbwDR8KR/dXAH55dMtTcqOqARfpwT04El7VlV3QiruXt4zaXiHOrvWd9Ic11UKPhZ98lAuBQ05kpmZ0EIXuJrg==
        ```
## Betrieb

### Lokal

#### Voraussetzungen

* Python in Version >=3.11 ist installiert
* pip ist installiert
* Virtual Environment für die App ist vorhanden
* CouchDB-Instanz ist vorhanden
* CouchDB-Nutzer mit Berechtigung zum Anlegen von Datenbanken ist verfügbar

#### Installation

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

    ```bash
    pip install -r requirements.txt
    ```

1. Erstellen von Datenbanken

    Datenbanken können unter Linux mit Hilfe des Scripts `init_db.sh` erstellt werden.

    Unter Windows muss dies manuell über die [CouchDB-Weboberfläche](localhost:5984/_utils) passieren
    Die Namen der benötigten Datenbanken können in der Datei `server/entities/databases.py` eingesehen werden.

1. Hinzufügen einer Organisation

    Eine einzelne Installation des FDOrganizer kann von einer oder mehreren Organisationen (Universitäten, Forschungseinrichtungen, etc.) genutzt werden.
    Um den FDOrganizer zu nutzen muss mindestens eine Organisation mit dazugehöriger Authentifizierung in der Datenbank hinterlegt werden.
    Dazu kann das Script *create_organisation* genutzt werden:

    ```python
        python create_organisation.py <file_path>
    ```

    Wenn der Parameter *file_path* genutzt wird, wird die organisation anhand der JSON-Struktur in der referenzierten Datei aufgebaut (siehe Datei *dummy_organisation*).
    Ansonsten wird eine interaktive Abfrage nach den Eigenschaften der Organisation gestartet.
    In beiden Fällen wird die Organisation in der Datenbank angelegt.

1. Zum lokalen Ausführen der App können entweder das [Flask CLI](https://flask.palletsprojects.com/en/2.2.x/cli/) oder die Startskripte benutzt werden.
Die Startskripte starten die App im Debug-Modus auf [`localhost:5000`](https://localhost:5000) und nutzen die mitgelieferten Self-Signed-Certificates zur SSL-Verschlüsselung.

* Windows

    Start via `./start.bat`

* Linux

    Start via `./start_local.sh` oder `sh start_local.sh`

#### Wartung

* Zurücksetzen von Datenbanken

    Während der Entwicklung in einer Testinstanz kann es Sinn machen, die Datenbanken des FDOrganizer zu leeren um keine überholten Daten zu nutzen.
    Dazu kann das Skript zum zurücksetzen der Datenbanken genutzt werden.

    ```python
        python reset_database.py <database_name>
    ```

    Wird der Name der Datenbank beim Start des Skripts nicht übergeben, wird dieser nachträglich abgefragt.

### Docker

#### Voraussetzungen

* Installiertes Docker-CLI (empfohlen: >= 23.0.6)
* Docker Compose Plugin (empfohlen: >= 2.17.3)

#### Installation

1. Setzen von Datenbanknutzer und -passwort wie unter [Konfiguration](#konfiguration) beschrieben.

1. Port Mapping für Datenbank und FDO in `docker-compose.yml` anpassen

    * Die Syntax für die Ports ist *hostsystem:container*.

    * Standardmäßig nutzt der FDO Port **34000** auf dem Hostsystem.

1. Das Anlegen der benötigten Datenbanken wird beim ersten Starten des FDO-Containers ausgeführt (siehe [`init_db.sh`](./init_db.sh))

1. Ebenfalls wird mit den Daten aus [`dummy_organisation.json`](./dummy_organisation.json) eine default-organisation angelegt, deren Daten für die Authentifizierung genutzt werden (siehe [`init_organisation.sh`](./init_organisation.sh))

1. Wird das compose plugin für Docker zum Starten genutzt, kann der Cluster über `docker compose up` gestartet werden.

1. Die Default-Namen der Container können auch in `docker-compose.yml` angepasst werden mit dem Property `container_name`.

#### Wartung

* Ein cronjob führt per default eine zeitgesteuerte Löschung aller Dokumente in der Datenbank zwischen **20 Uhr und 8 Uhr des Folgetags** durch.
Angelegte Organisationen und Nutzer bleiben hiervon unberührt.
Für eine Nutzung im Produktionsmodus kann

    * ein anderer Zeitraum gewählt werden, indem `./cron_clean/cronjobs` angepasst wird

    * der container `cron` aus `docker-compose.yaml` entfernt werden

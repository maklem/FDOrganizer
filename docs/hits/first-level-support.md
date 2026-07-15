---
title: Angebot "FDOrganizer" durch HITS
draft: true
tags:
- HITS FDM
---

# Anleitung für First Level Support (HITS FDM)

## Angebot

### Technischer Angebotsumfang

* Webservice, gehostet durch UB.FAU.de
* Anbindung an Hochschul-SSO über DFN-AAI
* Vorübergehend nutzbarer, limitierter, flüchtiger Speicherplatz
  * Max 1 GB pro Datei
  * Max 5 GB pro Paket
  * Max 100? GB für alle Nutzenden zusammen (Datenbanklimit)
  * Gegebenenfalls weitere Einschränkung, falls diese für den Betrieb nötig sind
    * (ein Limit für Dateianzahl ist derzeit nicht implementiert)
    * (ein Limit pro Nutzer ist derzeit nicht implementiert)
    * (ein Limit pro Hochschule ist derzeit nicht implementiert)
  * Kein Backup

### Serviceparameter

* Webservice ist durchgehend erreichbar, ausgenommen Wartung, Updates und technische Probleme
* Hochgeladene Daten werden nach einer Frist gelöscht. Sofern nichts anderes besprochen wird:
  * Aktivdaten 60 Tage
  * Archivdaten 15 Tage
* Kein Zugriffs**recht** auf Daten durch HITS (Admins *können* immer alles, was der angebotene Webservice kann.)
* Hochgeladene Daten sind für Autoren **und alle Reviewer der Hochschule** lesbar und sichtbar.

###	Voraussetzungen seitens der Hochschule

* Ausschluss des Uploads personenbezogener Daten, über Daten der Urheber hinaus
* Anforderung des Service zentral über die Hochschule
* (fortlaufende) Benennung von Reviewern

---

* stark modifizierter FDOrganizer

* Platform für
  * Zusammenstellung von Daten und Metadaten
  * Reviewprozess
  * Download eines Pakets aus Daten + Metadaten
    * Ersteller: immer, Reviewer nach Review
    * Metadaten kommen als Rosetta mets.xml

* Einschränkungen
  * Maximale Dateigröße: 1 GB (auch maximale Größe eines Uploadvorgangs)
  * Maximale Paketgröße: 5 GiB
  * Maximale Speicherdauer 60 Tage
    * Speicherdauer nach Review: 15 Tage

* Zugriff auf Daten haben
  * wer etwas hochlädt
  * alle Reviewer der zugehörigen Organisation
    * Zugriff wird erst ab Review beworben, ist aber ab Erstellung eines Pakets vorhanden
  * (technisch gesehen alle Admins)

## Anforderungen

* Anbindung an HITS-SSO
  * Freigabe von Home-Organisation
  * Freigabe von Pairwise-Id
* Anfrage an Adminteam mit
  * Benennung der Home-Organisation
  * Benennung von Reviewern


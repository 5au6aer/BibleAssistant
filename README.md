# Bibel Assistent (Version beta-1.3)

Ein Desktop-Anwendung zur Verwaltung und Dokumentation des persönlichen Bibellese-Fortschritts.

## Funktionsumfang
- Interaktives Dashboard: Visualisierung des Fortschritts in verschiedenen Bereichen (z. B. Altes Testament, Neues Testament oder benutzerdefinierte Abschnitte).
- Sperrbildschirm-Modus: Tägliche Erfassung des gelesenen Pensums inklusive optionaler Notizfunktion.
- PDF-Export: Automatische Generierung von detaillierten Lese-Protokollen im Verzeichnis /exports.
- Sicherheit: Schutz administrativer Funktionen (Reset, Löschen, Import) durch ein Master-Passwort.

## Release Notes

### Version beta-1.3 (Aktuell)
- **Projekt-Strukturierung:** Umstellung auf eine saubere Verzeichnislogik (/src, /data, /exports, /archive).
- **Open Source Vorbereitung:** Implementierung der MIT-Lizenz und Erstellung einer umfassenden .gitignore.
- **Daten-Sicherheit:** Trennung von Programmlogik und privaten Benutzerdaten (Master-Passwort und Fortschritt werden nun lokal geschützt).
- **Code-Hygiene:** Entfernung von Altlasten (SQL-Datenbank-Überreste) und Optimierung der Import-Struktur durch Packages.
- **Dokumentation:** Vollständige Überarbeitung der README und Präzisierung der requirements.txt.

### Version beta-1.2
- Implementierung des PDF-Exports für Lese-Protokolle.
- Hinzufügen der Master-Passwort-Abfrage für administrative Funktionen.
- Dashboard-Visualisierung der 9 Segmente.

## Installation und Start

1. Repository klonen oder Quelldateien in ein lokales Verzeichnis kopieren.

2. Abhängigkeiten installieren:
pip install -r requirements.txt

3. Programm starten:
python main.py

## Verzeichnisstruktur
- /data: Enthält die Datei progress.json (Benutzerfortschritt), die Struktur-Dateien (*_structure.json) und das Master-Passwort (master_pass.txt).
- /src: Enthält die Programmlogik und die Datenbank-Klasse (database.py).
- /exports: Zielverzeichnis für automatisch generierte PDF-Reports und Backup-Dateien.
- /archive: Manuelle Ablage für veraltete Dateiversionen oder historische Exporte.

## Systemvoraussetzungen
- Python 3.x
- Betriebssystem: Windows (getestet), Linux/macOS (kompatibel)

## Lizenz
Dieses Projekt ist unter der MIT-Lizenz lizenziert - siehe die [LICENSE](LICENSE) Datei für Details.
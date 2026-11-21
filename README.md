# RW – Digitale Essenswunscherfassung

Interne Webanwendung für die **Ruhesitz Wetterstein gGmbH** zur Erfassung, Verwaltung und Küchenübersicht der täglichen Essenswünsche von Bewohnerinnen und Bewohnern.

## Funktionsumfang
- **Für Pflegekräfte**: Strukturierte und intuitive Erfassung der Essenswünsche, mit detaillierten Auswahl- und Zusatzoptionen sowie seperaten Hinweisfeldern.
- **Für die Küche**: Automatische Berechnung der gesamten Essenswünsche für das gewählte Datum automatisch nach Menü und Mahlzeit. Übersichtliche Liste mit Bewohnername, Essenswunsch und Zimmer mit direkter Druckfunktion.
- **Für die Verwaltung**: Einfaches Eintragen und Löschen von Bewohern. Relationales Datenmodell, inklusiver einfacher Backup-Möglichkeit.

## Einblicke in die Anwendung
<img width="3040" height="1756" alt="grafik" src="https://github.com/user-attachments/assets/a3f2ebdd-f654-43c9-b12f-5c0d33e7ff77" />
<img width="3040" height="1756" alt="grafik" src="https://github.com/user-attachments/assets/d5f446f5-5d23-4d76-86c1-d48354c0d038" />
<img width="3040" height="1756" alt="grafik" src="https://github.com/user-attachments/assets/75f5220c-0134-4be1-923d-e1b4ad6a94be" />

## Technologie
| Eigenschaft | Details |
|---|---|
| **Framework** | Flask  |
| **Datenbank** | SQLite3 |
| **Host/Port** | 127.0.0.1:5000 |

## Installation
### Voraussetzungen
- **Python 3.8+** installiert
- Terminal/Kommandozeile
### Schritt-für-Schritt Anleitung
#### 1. Abhängigkeiten installieren
```bash
pip install -r requirements.txt
```
#### 2. Datenmigration ausführen (nur erforderlich bei Update von v1.1.0 oder älter)
```bash
python migration.py
```
#### 3. Anwendung starten
```bash
python app.py
```

Die Anwendung ist anschließend im Browser erreichbar unter:
```
http://127.0.0.1:5000
```

## Datenbankarchitektur
<img width="762" height="392" alt="rw-essensbestellung-db-schema" src="https://github.com/user-attachments/assets/ed4b7f77-d569-4772-8312-2f00d4b90f64" />

## Changelog

### Version 1.3.0 - *Oktober 2026*
* **Auslagerung der SQL-Dateien:** Sämtliche Inline-SQL-Queries wurden aus `app.py` entfernt und übersichtlich unter `database/sql/queries/` abgelegt.
* **Trennung von Mittag- und Abendessen:** Seperate Hinweisfelder sind vorhanden, seperate Zusatzoptionen wie "halbe Portion". Zudem erscheinen Bewohner, bei denen kein Essen ausgewählt wurde nicht in der Küchenübersicht für die jeweilige Übersicht (Mittag/Abend) am jeweiligen Tag.
* **Architektur:** Einführung des `database/`-Pakets inkl. `database.py` für die zentrale Verwaltung von Verbindungen, Schema-Initialisierung (`database/sql/schema/`) und der Hilfsfunktion `load_sql()`.
* **Repository:** `.gitignore` hinzugefügt, um lokale Entwicklungsdatenbanken (`*.db`) und Python-Cache (`__pycache__`) aus der Versionsverwaltung auszuschließen.

### Version 1.2.1 - *August 2026*
* **Umstellung auf SQLite:** Umstellung von JSON-Dateien auf eine SQLite-Datenbank.
* **Datenmigration:** Vor dem ersten Start von `app.py` muss einmalig `migration.py` ausgeführt werden, um bestehende JSON-Daten in die neue Datenbank-Struktur zu überführen:
```bash
python migration.py
```

---

**Version**: 1.3.0
**Letzte Aktualisierung**: 21. November 2026
**Entwicklung und Wartung**: Cosmo Caruso

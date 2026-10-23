# RW – Digitale Essenswunscherfassung

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

## Installation

### Voraussetzungen
- **Python 3.8+** installiert
- Terminal/Kommandozeile

### Schritt-für-Schritt Anleitung

#### 1. Abhängigkeiten installieren
```bash
pip install -r requirements.txt
```
#### 2. Migration ausführen (nur bei Update von 1.1.0 oder älter)
```bash
python migration.py
```

#### 3. Anwendung starten
```bash
python app.py
```

Die Anwendung ist im Browser erreichbar unter:
```
http://127.0.0.1:5000
```
## Technische Details

| Eigenschaft | Details |
|---|---|
| **Framework** | Flask  |
| **Datenbank** | SQLite3 |
| **Host/Port** | 127.0.0.1:5000 |

## Datenbank Schema (vereinfacht)
<img width="742" height="272" alt="DB Schema" src="https://github.com/user-attachments/assets/61feaee6-26c4-4593-8fb4-3f6b33924a6e" />

---

**Version**: 1.3.0
**Stand**: 23. Oktober 2026

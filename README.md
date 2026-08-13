# Ruhesitz Wetterstein – Digitale Essenswunscherfassung


## Änderungen
>Das System wurde auf SQLite umgestellt. Bitte führen Sie vor dem ersten Ausführen der app.py nach dem Update auf v1.2.0 die migration.py aus,
```bash
python migration.py
```
 um die Daten aus JSON in die Datenbank zu überführen. Ansonsten kann es zu Datenkonflikten kommen. 

## Installation

### Voraussetzungen
- **Python 3.8+** installiert
- Terminal/Kommandozeile

### Schritt-für-Schritt Setup

#### 1. Abhängigkeiten installieren
```bash
pip install -r requirements.txt
```

#### 2. App starten
```bash
python app.py
```

Die App lädt dann automatisch unter:
```
http://127.0.0.1:5000
```
## Technische Details

| Eigenschaft | Details |
|---|---|
| **Framework** | Flask  |
| **Datenbank** | SQLite3 DB (lokal) |
| **Port** | 5000 |

---

**Version**: 1.2.0  
**Stand**: August 2026

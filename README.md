# Ruhesitz Wetterstein – Digitale Essenswunscherfassung

Ein modernes, einfach zu bedienendes System zur Verwaltung von Essenswünschen für Bewohner im Seniorenheim.

## Update auf v1.2.0
**Wichtiger Hinweis**
Das System wurde auf SQLite umgestellt. Bitte führen Sie vor dem ersten Ausführen der app.py nach dem Update auf v1.2.0 mit migration.py aus um die Daten aus JSON in die Datenbank zu überführen. Ansonsten kann es zu Datenkonflikten kommen.

## Features

- **Essenswunscherfassung**: Pfleger erfassen Mittagessens- und Abendessenswünsche für jeden Bewohner 
- **Küchenübersicht**: Küchenpersonal sieht sofort alle Bestellungen für einen bestimmten Tag und kann sie ausdrucken
- **Bewohnerverwaltung**: Neue Bewohner hinzufügen und entfernen, Station zuweisen
- **Status-Filter**: Offene und erledigte Bestellungen auf einen Blick
- **Station-Filter**: Nach Wohnbereich filtern
- **Notizen**: Spezielle Ernährungswünsche vermerken

## Datenbank 
<img width="742" height="272" alt="DB Schema" src="https://github.com/user-attachments/assets/0b79584a-a796-4809-9bc1-6218fbab1184" />

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
| **Framework** | Flask |
| **Datenbank** | SQLite3 (lokal) |
| **Frontend** | HTML/CSS |
| **Live-Reload** | livereload |
| **Port** | 5000 |
| **Einsatz** | Seniorenheim (Intranet, lokal) |

## Troubleshooting

### "ModuleNotFoundError: No module named 'flask'"
→ `pip install -r requirements.txt` ausführen

### App lädt nicht unter http://127.0.0.1:5000
→ Port 5000 ist möglicherweise bereits in Nutzung. Alternatives Vorgehen:
1. Andere App beenden die Port 5000 nutzt
2. Oder in `app.py` letzte Zeile `port=5000` ändern zu z.B. `port=5001`

## Support

Bei Fragen: Entwickler kontaktieren 

---

**Entwickelt für**: Ruhesitz Wetterstein  
**Version**: 1.2.0  
**Stand**: August 2026

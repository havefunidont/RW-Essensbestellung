# Ruhesitz Wetterstein – Digitale Essenswunscherfassung

Ein modernes, einfach zu bedienendes System zur Verwaltung von Essenswünschen für Bewohner im Seniorenheim.

## Features

- **Essenswunscherfassung**: Pfleger erfassen Lunch- und Dinner-Wünsche für jeden Bewohner (7-Tage-Wochenansicht)
- **Küchenübersicht**: Küchenpersonal sieht sofort alle Bestellungen für einen bestimmten Tag (mit Statistiken)
- **Bewohnerverwaltung**: Neue Bewohner hinzufügen/entfernen, Station zuweisen
- **Status-Filter**: Offene/erledigte Bestellungen auf einen Blick
- **Station-Filter**: Nach Wohnbereich filtern
- **Notizen**: Spezielle Ernährungswünsche vermerken (z.B. "passiert", "Allergie")

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
| **Framework** | Flask (Python Web Framework) |
| **Datenbank** | JSON Files (lokal) |
| **Frontend** | HTML/CSS (Vanilla, keine JS-Frameworks) |
| **Live-Reload** | livereload (Auto-Refresh bei Änderungen) |
| **Port** | 5000 |
| **Einsatz** | Seniorenheim (Intranet, lokal) |

## Troubleshooting

### "ModuleNotFoundError: No module named 'flask'"
→ `pip install -r requirements.txt` ausführen

### App lädt nicht unter http://127.0.0.1:5000
→ Port 5000 ist möglicherweise bereits in Nutzung. Alternatives Vorgehen:
1. Andere App beenden die Port 5000 nutzt
2. Oder in `app.py` letzte Zeile `port=5000` ändern zu z.B. `port=5001`

### Änderungen erscheinen nicht
→ Normalerweise auto-reload. Falls nicht: Browser mit `Ctrl+Shift+R` hard-refreshen

## Support

Bei Fragen: Entwickler kontaktieren 

---

**Entwickelt für**: Ruhesitz Wetterstein  
**Version**: 1.1.0  
**Stand**: Juni 2026

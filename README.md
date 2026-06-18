# Ruhesitz Wetterstein – Digitale Essenswunscherfassung

Ein modernes, einfach zu bedienendes System zur Verwaltung von Essenswünschen für Bewohner im Seniorenheim.

## Features

- 📋 **Essenswunscherfassung**: Pfleger erfassen Lunch- und Dinner-Wünsche für jeden Bewohner (7-Tage-Wochenansicht)
- 👨‍⚖️ **Küchenübersicht**: Küchenpersonal sieht sofort alle Bestellungen für einen bestimmten Tag (mit Statistiken)
- 👤 **Bewohnerverwaltung**: Neue Bewohner hinzufügen/entfernen, Station zuweisen
- 🏷️ **Status-Filter**: Offene/erledigte Bestellungen auf einen Blick
- 🏢 **Station-Filter**: Nach Wohnbereich filtern
- 💬 **Notizen**: Spezielle Ernährungswünsche vermerken (z.B. "passiert", "Allergie")

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

Öffne diese Adresse im Browser.

> **Tipp**: Die App wird überwacht – wenn du eine Datei änderst (HTML, CSS, Python), lädt der Browser automatisch neu (Live-Reload).

## Bedienung

### Startseite (`/`)
Zentrale Anlaufstelle mit 3 Buttons:
- 📝 **Bestellungen erfassen** → Zu Bewohnerliste
- 🍽️ **Küchenübersicht** → Tagesplanung
- ⚙️ **Bewohner verwalten** → Admin-Bereich

### Essenswunscherfassung (`/entry`)
1. **Station/Status-Filter** setzen (optional)
2. **Woche wählen** (Aktuelle/Kommende/Übernächste)
3. Auf einen **Bewohner klicken**
4. Für jeden der 7 Tage Mittag + Abendessen wählen
5. **Speichern** – Status wechselt zu ✅ Erledigt

### Küchenübersicht (`/overview`)
- Zeigt alle Bestellungen für einen bestimmten Tag
- **Statistik unten**: Wie viele × Menü 1, Menü 2, Suppe, etc.
- Nach Name filtern (Suche)

### Bewohnerverwaltung (`/administration`)
- Neue Bewohner: Name, Zimmer, Station eingeben → **Hinzufügen**
- Bewohner löschen: ❌ Button klicken

## Datenstruktur

Die App speichert alles lokal:
- `residents.json` – Liste aller Bewohner (ID, Name, Zimmer, Station)
- `orders.json` – Alle Bestellungen (Bewohner-ID, Datum, Mittag, Abend, Notizen)

> Beide Dateien sind reguläre JSON und können notfalls mit einem Text-Editor bearbeitet werden.

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

Bei Fragen: Entwickler kontaktieren 📧

---

**Entwickelt für**: Ruhesitz Wetterstein  
**Version**: 1.0.0  
**Stand**: Juni 2026

import json, sqlite3

DB_FILE = "datenbank.db"

# Gibt die Verbindung zurück:
def get_connection():
    verbindung = sqlite3.connect(DB_FILE, timeout=5.0)
    verbindung.row_factory = sqlite3.Row
    verbindung.execute("PRAGMA foreign_keys = ON;")
    verbindung.execute("PRAGMA busy_timeout = 5000;")
    verbindung.execute("PRAGMA journal_mode = WAL;")
    return verbindung

# Bewohner laden
def load_residents():
    with open("residents.json", "r", encoding="utf-8") as f:
        return json.load(f)

# Bestellungen laden
def load_orders():
    with open("orders.json", "r", encoding="utf-8") as f:
        return json.load(f)

# Erstelle die Tabellen, wenn sie nicht existieren
def create_tables_if_not_exist():
    verbindung = get_connection()
    zeiger = verbindung.cursor()
    
    # Erstelle die DB-Tabellen beim ersten Start
    zeiger.execute("""
                   CREATE TABLE IF NOT EXISTS Stations(
                       stationID INTEGER PRIMARY KEY AUTOINCREMENT,
                       name VARCHAR(50) UNIQUE
                   )
                   """)
    
    # Füge die Stationen ein
    zeiger.execute("INSERT OR IGNORE INTO Stations (name) VALUES ('Betreutes Wohnen')")
    zeiger.execute("INSERT OR IGNORE INTO Stations (name) VALUES ('Wohngruppe 1')")
    zeiger.execute("INSERT OR IGNORE INTO Stations (name) VALUES ('Wohngruppe 2')")
    zeiger.execute("INSERT OR IGNORE INTO Stations (name) VALUES ('Wohngruppe 3')")
    
    zeiger.execute("""
                   CREATE TABLE IF NOT EXISTS Residents(
                       residentID INTEGER PRIMARY KEY AUTOINCREMENT,
                       name VARCHAR(50),
                       room INTEGER,
                       stationID INTEGER REFERENCES Stations(stationID)
                   )
                   """)
    
    zeiger.execute("""
                   CREATE TABLE IF NOT EXISTS Orders(
                       orderID INTEGER PRIMARY KEY AUTOINCREMENT,
                       date DATE,
                       lunch VARCHAR(50),
                       dinner VARCHAR(50),
                       halfPortion BOOLEAN,
                       noSoup BOOLEAN,
                       notes VARCHAR(100),
                       residentID INTEGER REFERENCES Residents(residentID),
                       UNIQUE (residentID, date)
                   )
                   """)
    
    # Speichere die Änderungen und schließe die Verbindung
    verbindung.commit()
    verbindung.close()

# Lade die JSON Daten und schreibe sie in die DB:
def main():
    print("Start der Migration zu SQL")
    # Erstelle die Tabellen falls das Migration script ausgeführt wird vor app.py:
    create_tables_if_not_exist()
    
    # Datenbankverbindung herstellen
    verbindung = get_connection()
    zeiger = verbindung.cursor()
    
    # Bewohner aus JSON laden:
    residents = load_residents()
    
    for resident in residents:
        resident_id = int(resident["id"])
        resident_name = resident["name"]
        resident_room = int(resident["room"])
        resident_stationID = 1 # Vor Umstellung existierte nur Betreutes Wohnen als Station

        zeiger.execute("""
                       INSERT OR IGNORE INTO
                       Residents (residentID, name, room, stationID) 
                       VALUES (?, ?, ?, ?)
                       """, (resident_id, resident_name, resident_room, resident_stationID))
    
    # Bestellungen aus JSON laden:
    orders = load_orders()
    
    for order in orders:
        # Order ID wird automaitsch durch AUTOINCREMENT vergeben
        order_date = order["timestamp"]
        order_lunch = order["lunch"]
        order_dinner = order["dinner"]
        order_halfPortion = bool(order["half_portion"])
        order_noSoup = bool(order["no_soup"])
        order_notes = order.get("notes", "")
        order_resident_ID = order["resident_id"] # FK speichern
        
        zeiger.execute("""
                       INSERT OR IGNORE INTO
                       Orders (date, lunch, dinner, halfPortion, noSoup, notes, residentID)
                       VALUES (?, ?, ?, ?, ?, ?, ?)
                       """, (order_date, order_lunch, order_dinner, order_halfPortion, order_noSoup, order_notes, order_resident_ID)) 

    # Speichere die Bewohner Bestellungen in der DB:
    verbindung.commit()
    
    verbindung.close()
    print("Ende der Migration zu SQL")

if __name__ == "__main__":
    main()
    
import json

from database.database import load_sql, get_connection, create_tables_if_not_exist

# Bewohner laden
def load_residents():
    with open("residents.json", "r", encoding="utf-8") as f:
        return json.load(f)

# Bestellungen laden
def load_orders():
    with open("orders.json", "r", encoding="utf-8") as f:
        return json.load(f)

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

        zeiger.execute(load_sql("migrate_resident"), (resident_id, resident_name, resident_room, resident_stationID))
    
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
        
        zeiger.execute(load_sql("migrate_order"), (order_date, order_lunch, order_dinner, order_halfPortion, order_noSoup, order_notes, order_resident_ID)) 

    # Speichere die Bewohner Bestellungen in der DB:
    verbindung.commit()
    verbindung.close()
    print("Ende der Migration zu SQL")

if __name__ == "__main__":
    main()
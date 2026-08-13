import json 

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
    residents = load_residents()
    
from flask import Flask, render_template, request, redirect
import json
from datetime import datetime, timedelta

app = Flask(__name__)
# Diese Zeile zwingt Flask, HTML-Dateien JEDES MAL frisch zu laden:
app.config['TEMPLATES_AUTO_RELOAD'] = True


# Bewohner laden
def load_residents():
    with open("residents.json", "r", encoding="utf-8") as f:
        return json.load(f)

# Bestellungen laden
def load_orders():
    with open("orders.json", "r", encoding="utf-8") as f:
        return json.load(f)

# Bestellungen speichern
def save_orders(orders):
    with open("orders.json", "w", encoding="utf-8") as f:
        json.dump(orders, f, indent=4, ensure_ascii=False)

# Startseite
@app.route("/")
def index():
    return render_template(
        "index.html"
    )

@app.route("/order/<int:resident_id>", methods=["GET", "POST"])
def order(resident_id):

    residents = load_residents()
    resident = next((r for r in residents if r["id"] == resident_id), None)

    if resident is None:
        return "Bewohner nicht gefunden", 404

    # Deutsche Wochentage für die Anzeige
    wochentage = ["Montag", "Dienstag", "Mittwoch", "Donnerstag", "Freitag", "Samstag", "Sonntag"]

    orders = load_orders()
    if request.method == "POST":
        station = request.form.get("station", "")
        status = request.form.get("status", "")
        # Alle 7 Wochentage durchlaufen
        for i in range(7):
            date_str = request.form.get(f"date_{i}")
            lunch = request.form.get(f"lunch_{i}")
            dinner = request.form.get(f"dinner_{i}")
            note = request.form.get(f"notes_{i}", "").strip()

            if date_str and (lunch or dinner):
                # Bestehende Bestellungen löschen falls vorhanden, um Duplikate zu vermeiden
                orders = [o for o in orders if not (o["resident_id"] == resident_id and o["timestamp"] == date_str)]

                orders.append({
                    "resident_id": resident_id,
                    "resident_name": resident["name"],
                    "room": resident["room"],
                    "station": resident["station"],
                    "lunch": lunch,
                    "dinner": dinner,
                    "notes": note,
                    "timestamp": date_str
                })

        save_orders(orders)

        # Nach dem Speichern zurück zur Übersicht
        today_str = datetime.now().date().isoformat()
        return redirect(
            f"/entry?date={today_str}&station={station}&status={status}"
        )

    # --- GET-DIENST: Generierung der Woche & Laden bestehender Daten ---
    today = datetime.now().date()
    start_of_week = today + timedelta(days=(0 - today.weekday()) % 7)
    if today.weekday() >= 4:
        start_of_week += timedelta(weeks=1)

    days = []
    for i in range(7):
        current_date = start_of_week + timedelta(days=i)
        date_str = current_date.isoformat()
        
        # Suchen, ob für diesen Tag bereits eine Bestellung im System existiert
        existing_order = next((o for o in orders if o["resident_id"] == resident_id and o["timestamp"] == date_str), None)
        
        # Wenn eine Bestellung existiert, nehmen wir deren Werte, ansonsten leere/Standardwerte
        days.append({
            "index": i,
            "date_str": date_str,
            "date_de": current_date.strftime("%d.%m.%Y"),
            "day_name": wochentage[i],
            "saved_lunch": existing_order["lunch"] if existing_order else "Menü 1", # Standardwert Menü 1
            "saved_dinner": existing_order["dinner"] if existing_order else "Menü 1",
            "saved_notes": existing_order["notes"] if existing_order else ""
        })

    return render_template("order.html", resident=resident, days=days)
    
# Übersicht
@app.route("/overview")
def overview():

    orders = load_orders()
    residents = load_residents()
    date_filter = request.args.get("date")

    if not date_filter:
        today = datetime.now().date()
        start_of_week = today + timedelta(days=(0 - today.weekday()) % 7)
        if today.weekday() >= 4:
            start_of_week += timedelta(weeks=1)
        date_filter = start_of_week.isoformat()
        
    name_filter = request.args.get("name", "").strip().lower()

    filtered_orders = []
    
    # Statistiken initialisieren
    lunch_stats = {"Menü 1": 0, "Menü 2": 0, "Suppe": 0, "Grießbrei": 0, "passiert": 0, "Kein Essen": 0}
    dinner_stats = {"Menü 1": 0, "Menü 2": 0, "Suppe": 0, "Grießbrei": 0, "passiert": 0, "Kein Essen": 0}

    for order in orders:
        if date_filter and order.get("timestamp", "") != date_filter:
            continue
        if name_filter and name_filter not in order.get("resident_name", "").lower():
            continue
            
        filtered_orders.append(order)
        
        # Gerichte hochzählen, falls sie in den Statistiken existieren
        l_meal = order.get("lunch")
        if l_meal in lunch_stats:
            lunch_stats[l_meal] += 1
            
        d_meal = order.get("dinner")
        if d_meal in dinner_stats:
            dinner_stats[d_meal] += 1

    return render_template(
        "overview.html",
        orders=filtered_orders,
        residents=residents,
        date_filter=date_filter,
        name_filter=name_filter,
        lunch_stats=lunch_stats,
        dinner_stats=dinner_stats
    )

@app.route("/entry")
def entry():

    residents = load_residents()
    orders = load_orders()

    station_filter = request.args.get("station", "")
    status_filter = request.args.get("status")if "status" in request.args else "offen"
    date_filter = request.args.get("date")

    if not date_filter:
        date_filter = (
            datetime.now().date() + timedelta(days=1)
        ).isoformat()

    station_options = sorted({r["station"] for r in residents})

    # Station filtern
    if station_filter:
        residents = [
            r for r in residents
            if r["station"] == station_filter
        ]

    # --- LOGIK FÜR DIE WOCHENABHAKUNG ---
    today = datetime.now().date()
    # Berechne den kommenden Montag (identisch zur Logik in /order)
    start_of_week = today + timedelta(days=(0 - today.weekday()) % 7)
    if today.weekday() >= 4:  # Wenn bereits Freitag/Wochenende ist
        start_of_week += timedelta(weeks=1)
    
    start_of_week_str = start_of_week.isoformat()

    for resident in residents:
        # Finde alle Bestellungen dieses Bewohners für die kommende Woche
        resident_week_orders = [
            order for order in orders 
            if order["resident_id"] == resident["id"] and order["timestamp"] >= start_of_week_str
        ]
        
        # Ein Bewohner ist abgehakt, wenn mindestens ein Eintrag für die neue Woche existiert
        resident["done"] = len(resident_week_orders) > 0
        
        # Punkt 3: Text-Zusammenfassung generieren, falls Bestellungen existieren
        if resident["done"]:
            # Wir nehmen beispielhaft den ersten gefundenen Tag für die Vorschau auf dem Dashboard
            first_order = resident_week_orders[0]
            resident["summary"] = f"Mittag: {first_order['lunch']}, Abend: {first_order['dinner']}"
        else:
            resident["summary"] = ""
    
    # Statusfilter
    if status_filter == "erledigt":
        residents = [r for r in residents if r["done"]]
    elif status_filter == "offen":
        residents = [r for r in residents if not r["done"]]

    return render_template(
        "entry.html",
        residents=residents,
        station_options=station_options,
        station_filter=station_filter,
        status_filter=status_filter,
        date_filter=date_filter
    )

@app.route("/administration")
def administration():
    residents = load_residents()
    return render_template("administration.html", residents=residents)

# Bewohner speichern:
def save_residents(residents):
    with open("residents.json", "w", encoding="utf-8") as f:
        json.dump(residents, f, indent=4, ensure_ascii=False)
        
# Bewohner hinzufügen - POST
@app.route("/administration/add", methods=["POST"])
def administration_add():
    residents = load_residents()
    
    # Daten aus dem Formular auslesen
    name = request.form.get("name", "").strip()
    room = request.form.get("room", "").strip()
    station = request.form.get("station", "").strip()
    
    if name and room and station:
        # Höchste bestehende ID ermitteln und um 1 erhöhen
        new_id = max([r["id"] for r in residents]) + 1 if residents else 1
        
        # Neuen Bewohner anhängen
        residents.append({
            "id": new_id,
            "name": name,
            "room": room,
            "station": station
        })
        save_residents(residents)
    
    return redirect("/administration")

# Bewohner entfernen - GET
@app.route("/administration/delete/<int:resident_id>")
def administration_delete(resident_id):
    residents = load_residents()
    
    # Bewohner aus der Liste filtern
    residents = [r for r in residents if r["id"] != resident_id]
    save_residents(residents)
    
    # Optionale Bereinigung: Löscht auch die alten Bestellungen des Bewohners,
    # damit die orders.json sauber bleibt
    orders = load_orders()
    orders = [o for o in orders if o["resident_id"] != resident_id]
    save_orders(orders)
    
    return redirect("/administration")

if __name__ == '__main__':
    from livereload import Server
    server = Server(app.wsgi_app)
    
    # Durch den Punkt ('.') überwacht das Tool ab sofort das KOMPLETTE Projektverzeichnis
    server.watch('.')
    
    server.serve(port=5000, liveport=35729, host='127.0.0.1')

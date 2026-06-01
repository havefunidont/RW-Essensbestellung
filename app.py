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

    wochentage = ["Montag", "Dienstag", "Mittwoch", "Donnerstag", "Freitag", "Samstag", "Sonntag"]
    orders = load_orders()
    
    # Die gewählte Woche aus der URL oder dem Formular holen
    selected_week = request.args.get("week_start") or request.form.get("week_start")
    if not selected_week:
        today = datetime.now().date()
        default_monday = today - timedelta(days=today.weekday())
        if today.weekday() >= 4:
            default_monday += timedelta(weeks=1)
        selected_week = default_monday.isoformat()

    if request.method == "POST":
        station = request.form.get("station", "")
        status = request.form.get("status", "")
        
        # Alle 7 Wochentage durchlaufen und speichern
        for i in range(7):
            date_str = request.form.get(f"date_{i}")
            lunch = request.form.get(f"lunch_{i}")
            dinner = request.form.get(f"dinner_{i}")
            note = request.form.get(f"notes_{i}", "").strip()

            if date_str:
                # Duplikate für diesen Tag und Bewohner entfernen
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

        # Beim Redirect geben wir die 'week_start' wieder mit zurück!
        return redirect(
            f"/entry?week_start={selected_week}&station={station}&status={status}"
        )

    # --- GET-MODUS: Generierung der gewählten Woche ---
    start_of_week = datetime.fromisoformat(selected_week).date()

    days = []
    for i in range(7):
        current_date = start_of_week + timedelta(days=i)
        date_str = current_date.isoformat()
        
        existing_order = next((o for o in orders if o["resident_id"] == resident_id and o["timestamp"] == date_str), None)
        
        days.append({
            "index": i,
            "date_str": date_str,
            "date_de": current_date.strftime("%d.%m.%Y"),
            "day_name": wochentage[i],
            "saved_lunch": existing_order["lunch"] if existing_order else "Menü 1",
            "saved_dinner": existing_order["dinner"] if existing_order else "Menü 1",
            "saved_notes": existing_order["notes"] if existing_order else ""
        })

    return render_template("order.html", resident=resident, days=days, selected_week=selected_week)
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
    
# Hilfsfunktion zur Generierung der drei wählbaren Wochen
def get_week_options():
    today = datetime.now().date()
    # Finde den Montag der aktuellen Kalenderwoche
    current_monday = today - timedelta(days=today.weekday())
    
    weeks = []
    labels = ["Aktuelle Woche", "Kommende Woche", "Übernächste Woche"]
    
    for i, label in enumerate(labels):
        monday = current_monday + timedelta(weeks=i)
        sunday = monday + timedelta(days=6)
        weeks.append({
            "value": monday.isoformat(),
            "label": f"{label} ({monday.strftime('%d.%m.')} – {sunday.strftime('%d.%m.%Y')})"
        })
    return weeks

@app.route("/entry")
def entry():
    residents = load_residents()
    orders = load_orders()

    # Filter aus der URL holen
    station_filter = request.args.get("station", "")
    status_filter = request.args.get("status") if "status" in request.args else "offen"
    
    # Wochen-Optionen generieren
    week_options = get_week_options()
    
    # Standardmäßig die kommende Woche vorauswählen
    today = datetime.now().date()
    current_monday = today - timedelta(days=today.weekday())
    kommender_monday = current_monday + timedelta(weeks=1) # Standard ist die nächste Woche
        
    selected_week = request.args.get("week_start", kommender_monday.isoformat())
    date_filter = request.args.get("date", today.isoformat())
    
    # Station filtern
    if station_filter:
        residents = [r for r in residents if r["station"] == station_filter]

    # Berechne den Datumsbereich für die gewählte Woche (Montag bis Sonntag)
    start_date = datetime.fromisoformat(selected_week).date()
    end_date = start_date + timedelta(days=6)
    
    # Generiere eine Liste aller 7 ISO-Tagesdaten dieser Woche für den Status-Check
    week_days_strs = [(start_date + timedelta(days=i)).isoformat() for i in range(7)]

    for resident in residents:
        # Finde alle Bestellungen dieses Bewohners, die zeitlich in die ausgewählte Woche fallen
        resident_week_orders = [
            order for order in orders 
            if order["resident_id"] == resident["id"] and order.get("timestamp") in week_days_strs
        ]
        
        # Erledigt, wenn für jeden der 7 Tage ein Eintrag existiert (vollständig ausgefüllt)
        resident["done"] = len(resident_week_orders) >= 7
        
        if len(resident_week_orders) > 0:
            first_order = resident_week_orders[0]
            resident["summary"] = f"Erfasst (z.B. M: {first_order['lunch']})"
        else:
            resident["summary"] = ""
    
    # Statusfilter anwenden
    if status_filter == "erledigt":
        residents = [r for r in residents if r["done"]]
    elif status_filter == "offen":
        residents = [r for r in residents if not r["done"]]

    return render_template(
        "entry.html",
        residents=residents,
        station_options=sorted({r["station"] for r in load_residents()}),
        station_filter=station_filter,
        status_filter=status_filter,
        week_options=week_options,
        selected_week=selected_week
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

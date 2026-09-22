from flask import Flask, render_template, request, redirect
from datetime import datetime, timedelta

from database.database import load_sql, create_tables_if_not_exist, get_connection

# RELEASE

app = Flask(__name__)
# app.config['TEMPLATES_AUTO_RELOAD'] = True
    
# Startseite
@app.route("/")
def index():
    return render_template("index.html")
    
# Bestellungen
@app.route("/order/<int:resident_id>", methods=["GET", "POST"])
def order(resident_id):
    # Suche den Bewohner 
    verbindung = get_connection()
    zeiger = verbindung.cursor()

    zeiger.execute(load_sql("get_resident_by_id"), (resident_id,))
    resident = zeiger.fetchone()
    verbindung.close()
    
    if resident is None:
        return "Bewohner nicht gefunden", 404

    wochentage = ["Montag", "Dienstag", "Mittwoch", "Donnerstag", "Freitag", "Samstag", "Sonntag"]
    
    # Die gewählte Woche aus der URL oder dem Formular holen
    selected_week = request.args.get("week_start") or request.form.get("week_start")
    if not selected_week:
        today = datetime.now().date()
        default_monday = today - timedelta(days=today.weekday())
        if today.weekday() >= 4:
            default_monday += timedelta(weeks=1)
        selected_week = default_monday.isoformat()

    # POST Request
    if request.method == "POST":
        station = request.form.get("station", "")
        status = request.form.get("status", "")
        
        verbindung = get_connection()
        zeiger = verbindung.cursor()
        
        # Alle 7 Wochentage durchlaufen und speichern
        for i in range(7):
            # Eingaben erfassen
            date_str = request.form.get(f"date_{i}")
            lunch = request.form.get(f"lunch_{i}")
            dinner = request.form.get(f"dinner_{i}")
            note = request.form.get(f"notes_{i}", "").strip()
            half_portion = f"half_portion_{i}" in request.form
            no_soup = f"no_soup_{i}" in request.form
            
            if date_str:
                # Neue Bestellung einfügen
                zeiger.execute(load_sql("save_order"), (date_str, lunch, dinner, half_portion, no_soup, note, resident_id))

        # Am Ende speichern:
        verbindung.commit()
        verbindung.close()

        # Beim Redirect geben wir die 'week_start' wieder mit zurück!
        return redirect(
            f"/entry?week_start={selected_week}&station={station}&status={status}"
        )
    # --- GET-MODUS: Generierung der gewählten Woche ---
    start_of_week = datetime.fromisoformat(selected_week).date()
    
    verbindung = get_connection()
    zeiger = verbindung.cursor()

    days = []
    # Durchlaufe die Woche
    for i in range(7):
        current_date = start_of_week + timedelta(days=i)
        date_str = current_date.isoformat()
        zeiger.execute(load_sql("get_order_by_resident_and_date"), (resident_id, date_str))
        existing_order = zeiger.fetchone()
        
        days.append({
            "index": i,
            "date_str": date_str,
            "date_de": current_date.strftime("%d.%m.%Y"),
            "day_name": wochentage[i],
            "saved_lunch": existing_order["lunch"] if existing_order else "",
            "saved_dinner": existing_order["dinner"] if existing_order else "",
            "saved_notes": existing_order["notes"] if existing_order else "",
            "saved_half_portion": bool(existing_order["halfPortion"]) if existing_order else False,
            "saved_no_soup": bool(existing_order["noSoup"]) if existing_order else False
        })

    verbindung.close()
    return render_template("order.html", resident=resident, days=days, selected_week=selected_week)

# Küchenübersicht
@app.route("/overview")
def overview():
    # Datums- und Namensfilter laden 
    date_filter = request.args.get("date")
    
    if not date_filter:
        today = datetime.now().date()
        date_filter = today.isoformat()
        
    name_filter = request.args.get("name", "").strip()
        
    verbindung = get_connection()
    zeiger = verbindung.cursor()
    
    # Lade die Bestellungen (mit oder ohne Namens Filter)
    if not name_filter:
        zeiger.execute(load_sql("get_overview_all"), (date_filter,))
        filtered_orders_with_residents = zeiger.fetchall()
    else:
        zeiger.execute(load_sql("get_overview_by_name"), (date_filter, f'%{name_filter}%'))
        filtered_orders_with_residents = zeiger.fetchall()
    
    verbindung.close()
    
    # Statistiken initialisieren
    lunch_stats = {"Menü 1": 0, "Menü 2": 0, "Kein Essen": 0}
    dinner_stats = {"Menü 1": 0, "Menü 2": 0, "Kein Essen": 0}

    for order in filtered_orders_with_residents:
        # Gerichte hochzählen, falls sie in den Statistiken existieren
        l_meal = order["lunch"]
        if l_meal in lunch_stats:
            lunch_stats[l_meal] += 1
            
        d_meal = order["dinner"]
        if d_meal in dinner_stats:
            dinner_stats[d_meal] += 1

    return render_template(
        "overview.html",
        orders=filtered_orders_with_residents,
        #residents=residents,
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
    station_raw = request.args.get("station", "")
    station_id = int (station_raw) if station_raw.isdigit() else None
    
    status_filter = request.args.get("status") if "status" in request.args else "offen"
    
    week_options = get_week_options()
    
    today = datetime.now().date()
    current_monday = today - timedelta(days=today.weekday())
    kommender_monday = current_monday + timedelta(weeks=1)
        
    selected_week = request.args.get("week_start", kommender_monday.isoformat())
    start_date = datetime.fromisoformat(selected_week).date()
    end_date = start_date + timedelta(days=6)

    with get_connection() as verbindung:
        zeiger = verbindung.cursor()

        zeiger.execute(load_sql("get_stations_all"))
        station_options = zeiger.fetchall()
        
        query = load_sql("get_entry_residents")
        params = [start_date.isoformat(), end_date.isoformat()]

        # Identifikation über ID:
        if station_id is not None:
            query += "WHERE Stations.stationID = ?"
            params.append(station_id)

        query += """
            GROUP BY Residents.residentID
            ORDER BY Residents.room ASC
        """

        zeiger.execute(query, params)
        raw_residents = zeiger.fetchall()

        residents = []
        for r in raw_residents:
            res_dict = dict(r)
            is_done = res_dict["order_count"] >= 7
            res_dict["done"] = is_done
            res_dict["summary"] = "Erfasst" if res_dict["order_count"] > 0 else ""

            if status_filter == "erledigt" and not is_done:
                continue
            if status_filter == "offen" and is_done:
                continue

            residents.append(res_dict)

    verbindung.close()

    return render_template(
        "entry.html",
        residents=residents,
        station_options=station_options,
        station_filter=station_id,
        status_filter=status_filter,
        week_options=week_options,
        selected_week=selected_week,
        date_filter=start_date.isoformat()
    )

@app.route("/administration")
def administration():
    with get_connection() as verbindung:
        zeiger = verbindung.cursor()
        # Sammle alle Bewohner mitsamt Stationennamen
        zeiger.execute(load_sql("get_administration_residents"))
        residents = zeiger.fetchall()
        
        # Sammle alle Stationsoptionen (ID, Name)
        zeiger.execute(load_sql("get_stations_all"))
        station_options = zeiger.fetchall()
    verbindung.close()

    return render_template("administration.html", residents=residents, station_options=station_options)
    
# Bewohner hinzufügen - POST
@app.route("/administration/add", methods=["POST"])
def administration_add():
    # Daten aus dem Formular auslesen
    name = request.form.get("name", "").strip()
    room = request.form.get("room", "").strip()
    station_id = request.form.get("station", "").strip()
    
    # Nur fortfahren wenn alles ausgefüllt ist:
    if not (name and room and station_id): 
        return redirect("/administration")
    
    with get_connection() as verbindung:
        zeiger = verbindung.cursor()
        zeiger.execute(load_sql("add_resident"), (name, room, station_id))
        verbindung.commit()
    verbindung.close()

    return redirect("/administration")

# Bewohner entfernen - GET
@app.route("/administration/delete/<int:resident_id>")
def administration_delete(resident_id):
    with get_connection() as verbindung:
        zeiger = verbindung.cursor()
        
        # Zuerst alle Bestellungen ebenfalls löschen des Bewohners:
        zeiger.execute(load_sql("delete_orders_by_resident"), (resident_id,))

        # Bewohner löschen
        zeiger.execute(load_sql("delete_resident"), (resident_id,))
        
        verbindung.commit()
    verbindung.close()

    return redirect("/administration")
    
if __name__ == '__main__':
    create_tables_if_not_exist()
    app.run(host='127.0.0.1', port=5000, debug=False)
    # from livereload import Server
    # server = Server(app.wsgi_app)
    # server.watch('.')
    # server.serve(port=5000, liveport=35729, host='0.0.0.0')

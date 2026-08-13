from flask import Flask, render_template, request, redirect
from datetime import datetime, timedelta
import sqlite3

app = Flask(__name__)
# app.config['TEMPLATES_AUTO_RELOAD'] = True

DB_FILE = "datenbank.db"

# Initialisiere die Datenbank
def init_db():
    verbindung = sqlite3.connect(DB_FILE)
    zeiger = verbindung.cursor()
    
    # Erstelle die DB-Tabellen beim ersten Start
    zeiger.execute("""
                   CREATE TABLE IF NOT EXISTS Stations(
                       stationID INTEGER PRIMARY KEY AUTOINCREMENT,
                       name VARCHAR(50) UNIQUE
                   )
                   """)
    
    # Füge die Station Betreutes Wohnen ein als einzige für den Testlauf:
    zeiger.execute("""
                   INSERT OR IGNORE INTO Stations (name) VALUES ('Betreutes Wohnen')
                   """)
    
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
    
# Startseite
@app.route("/")
def index():
    return render_template(
        "index.html"
    )
    
# Bestellungen
@app.route("/order/<int:resident_id>", methods=["GET", "POST"])
def order(resident_id):
    # Suche den Bewohner 
    verbindung = sqlite3.connect(DB_FILE)
    verbindung.row_factory = sqlite3.Row
    
    zeiger = verbindung.cursor()
    zeiger.execute("""
                   SELECT *
                   FROM Residents
                   WHERE residentID = ?
                   """, (resident_id,))
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
        
        verbindung = sqlite3.connect(DB_FILE)
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
                zeiger.execute("""
                               INSERT OR REPLACE 
                               INTO orders (date, lunch, dinner, halfPortion, noSoup, notes, residentID)
                               VALUES (?, ?, ?, ?, ?, ?, ?)
                               """, (date_str, lunch, dinner, half_portion, no_soup, note, resident_id))

        # Am Ende speichern:
        verbindung.commit()
        verbindung.close()

        # Beim Redirect geben wir die 'week_start' wieder mit zurück!
        return redirect(
            f"/entry?week_start={selected_week}&station={station}&status={status}"
        )
    # --- GET-MODUS: Generierung der gewählten Woche ---
    start_of_week = datetime.fromisoformat(selected_week).date()
    
    verbindung = sqlite3.connect(DB_FILE)
    verbindung.row_factory = sqlite3.Row 
    zeiger = verbindung.cursor()

    days = []
    # Durchlaufe die Woche
    for i in range(7):
        current_date = start_of_week + timedelta(days=i)
        date_str = current_date.isoformat()
        # Suche bestehende Bestellungen
        #existing_order = next((o for o in orders if o["resident_id"] == resident_id and o["timestamp"] == date_str), None)
        
        zeiger.execute("""
                       SELECT *
                       FROM Orders
                       WHERE residentID = ? AND date = ?
                       """, (resident_id, date_str))
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
        start_of_week = today - timedelta(days=today.weekday())
        # Ab Freitag auf die nächste Woches springen
        if today.weekday() >= 4:
            start_of_week += timedelta(weeks=1)
        date_filter = start_of_week.isoformat()
        
    name_filter = request.args.get("name", "").strip()
        
    verbindung = sqlite3.connect(DB_FILE)
    verbindung.row_factory = sqlite3.Row
    zeiger = verbindung.cursor()
    
    # Lade die Bestellungen (mit oder ohne Namens Filter)
    if not name_filter:
        zeiger.execute("""
                    SELECT Residents.name AS residentName, 
                    Residents.room AS residentRoom
                    , Orders.* 
                    FROM Residents
                    INNER JOIN Orders
                    ON Orders.residentID = Residents.residentID
                    WHERE Orders.date = ? 
                    ORDER BY Residents.room ASC
                    """, (date_filter,))
        filtered_orders_with_residents = zeiger.fetchall()
    else:
        zeiger.execute("""
                    SELECT Residents.name AS residentName, 
                    Residents.room AS residentRoom
                    , Orders.* 
                    INNER JOIN Orders
                    ON Orders.residentID = Residents.residentID
                    WHERE Orders.date = ? AND Residents.name LIKE ?
                    ORDER BY Residents.room ASC
                    """, (date_filter, f'%{name_filter}%'))
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
    station_filter = request.args.get("station", "")
    status_filter = request.args.get("status") if "status" in request.args else "offen"
    
    week_options = get_week_options()
    
    today = datetime.now().date()
    current_monday = today - timedelta(days=today.weekday())
    kommender_monday = current_monday + timedelta(weeks=1)
        
    selected_week = request.args.get("week_start", kommender_monday.isoformat())
    start_date = datetime.fromisoformat(selected_week).date()
    end_date = start_date + timedelta(days=6)

    with sqlite3.connect(DB_FILE) as verbindung:
        verbindung.row_factory = sqlite3.Row
        zeiger = verbindung.cursor()

        zeiger.execute("SELECT name FROM Stations ORDER BY name ASC")
        station_options = [row["name"] for row in zeiger.fetchall()]

        query = """
            SELECT 
                Residents.residentID,
                Residents.name,
                Residents.room,
                Stations.name AS station,
                COUNT(DISTINCT Orders.date) AS order_count
            FROM Residents
            INNER JOIN Stations ON Stations.stationID = Residents.stationID
            LEFT JOIN Orders ON Orders.residentID = Residents.residentID 
                            AND Orders.date BETWEEN ? AND ?
        """
        params = [start_date.isoformat(), end_date.isoformat()]

        if station_filter:
            query += " WHERE Stations.name = ?"
            params.append(station_filter)

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

    return render_template(
        "entry.html",
        residents=residents,
        station_options=station_options,
        station_filter=station_filter,
        status_filter=status_filter,
        week_options=week_options,
        selected_week=selected_week,
        date_filter=start_date.isoformat()
    )

@app.route("/administration")
def administration():
    with sqlite3.connect(DB_FILE) as verbindung:
        verbindung.row_factory = sqlite3.Row
        zeiger = verbindung.cursor()
        zeiger.execute("""
                       SELECT Residents.*, Stations.name AS station
                       FROM Residents
                       INNER JOIN Stations 
                       ON Stations.stationID = Residents.stationID
                       ORDER BY Residents.room ASC
                       """)
        residents = zeiger.fetchall()

    return render_template("administration.html", residents=residents)
    
# Bewohner hinzufügen - POST
@app.route("/administration/add", methods=["POST"])
def administration_add():
    # Daten aus dem Formular auslesen
    name = request.form.get("name", "").strip()
    room = request.form.get("room", "").strip()
    station = request.form.get("station", "").strip()
    
    # Nur fortfahren wenn alles ausgefüllt ist:
    if not (name and room and station): return redirect("/administration")
    
    with sqlite3.connect(DB_FILE) as verbindung:
        zeiger = verbindung.cursor()
        zeiger.execute("""
                       INSERT INTO
                       Residents (name, room, stationID)
                       VALUES (?, ?, ?)
                       """, (name, room, 1)) # Im Testlauf gibts nur eine Station
   
    return redirect("/administration")

# Bewohner entfernen - GET
@app.route("/administration/delete/<int:resident_id>")
def administration_delete(resident_id):
    with sqlite3.connect(DB_FILE) as verbindung:
        zeiger = verbindung.cursor()
        
        # Bewohner löschen
        zeiger.execute("""
                    DELETE FROM Residents
                    WHERE residentID = ?
                    """, (resident_id,))
        
        # Alle Bestellungen ebenfalls löschen des Bewohners:
        zeiger.execute("""
                    DELETE FROM Orders
                    WHERE residentID = ?
                    """, (resident_id,))
        
    return redirect("/administration")
    
if __name__ == '__main__':
    init_db()
    app.run(host='127.0.0.1', port=5000, debug=False)
    # from livereload import Server
    # server = Server(app.wsgi_app)
    # server.watch('.')
    # server.serve(port=5000, liveport=35729, host='127.0.0.1')
import sqlite3
from pathlib import Path

# Pfad zum SQL Ordner
BASE_DIR = Path(__file__).parent
SQL_DIR = BASE_DIR / "sql"
DB_FILE = BASE_DIR / "datenbank.db"

# Hilfsfunktion, gibt die Verbindung zurück:
def get_connection():
    verbindung = sqlite3.connect(DB_FILE, timeout=5.0)
    verbindung.row_factory = sqlite3.Row
    verbindung.execute("PRAGMA foreign_keys = ON;")
    verbindung.execute("PRAGMA busy_timeout = 5000;")
    verbindung.execute("PRAGMA journal_mode = WAL;")
    return verbindung

def load_sql(query_name):
    file_path = SQL_DIR / "queries" / f"{query_name}.sql"
    with open(file_path, "r", encoding="utf-8") as f:
        return f.read().strip()

def execute_schema_file(cursor, file_name):
    file_path = SQL_DIR / "schema" / file_name
    with open(file_path, "r", encoding="utf-8") as f:
        sql_script = f.read()
    cursor.executescript(sql_script)

def create_tables_if_not_exist():
    verbindung = get_connection()
    zeiger = verbindung.cursor()

    # Tabellen laden:
    execute_schema_file(zeiger, "stations.sql")
    execute_schema_file(zeiger, "residents.sql")
    execute_schema_file(zeiger, "orders.sql")

    # Füge die Stationen ein
    zeiger.execute("INSERT OR IGNORE INTO Stations (name) VALUES ('Betreutes Wohnen')")
    zeiger.execute("INSERT OR IGNORE INTO Stations (name) VALUES ('Wohngruppe 1')")
    zeiger.execute("INSERT OR IGNORE INTO Stations (name) VALUES ('Wohngruppe 2')")
    zeiger.execute("INSERT OR IGNORE INTO Stations (name) VALUES ('Wohngruppe 3')")
    

    verbindung.commit()
    verbindung.close()
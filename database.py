import sqlite3

conn = sqlite3.connect('data.db')
cur = conn.cursor()

DB_COLUMNS = [
    "ph1_check_0",
    "ph1_check_1",
    "ph1_check_2",
    "ph1_check_3",
    "ph1_check_4",
    "ph1_check_5",
    "ph1_photo_0",
    "ph1_photo_1"
]

def insert_record(record):
    # print("INSERT INTO results (" + ", ".join(DB_COLUMNS) + ") VALUES (" + ", ".join([':' + c for c in DB_COLUMNS]) + ")", flush=True)
    cur.execute("INSERT INTO results VALUES (NULL, " + ", ".join([':' + c for c in DB_COLUMNS]) + ")", record)
    conn.commit()

def results():
    cur.execute("select * from results")
    return [("id", *DB_COLUMNS)] + cur.fetchall()
from database import *

try:
    cur.execute("DROP TABLE results")
except sqlite3.OperationalError:
    pass

cur.execute("""CREATE TABLE results(
    id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    {}
)""".format(", ".join(DB_COLUMNS)))
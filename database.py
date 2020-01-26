import sqlite3

class Database:
    def __init__(self, filename, columns):
        self.conn = sqlite3.connect('data.db')
        self.cur = self.conn.cursor()
        self.columns = columns
        self.cur.execute('select * from results')
        existing_cols = set([d[0] for d in self.cur.description])
        if existing_cols != columns:
            if existing_cols.issubset(columns):
                for col in (columns - existing_cols):
                    self.cur.execute("alter table results add column" + col + " text")
            else:
                self.cur.execute("drop table results")
                self.cur.execute(
                    "create table results (id integer primary key, {})".format(
                        ', '.join(c + ' text' for c in columns)
                    )
                )

    def insert_record(self, record):
        # print("INSERT INTO results (" + ", ".join(DB_COLUMNS) + ") VALUES (" + ", ".join([':' + c for c in DB_COLUMNS]) + ")", flush=True)
        self.cur.execute("INSERT INTO results VALUES (NULL, " + ", ".join([':' + c for c in self.columns]) + ")", record)
        self.conn.commit()

    def results(self):
        self.cur.execute("select * from results")
        return [("id", *self.columns)] + self.cur.fetchall()


# conn = sqlite3.connect('data.db')
# cur = conn.cursor()

# DB_COLUMNS = [
#     "ph1_check_0",
#     "ph1_check_1",
#     "ph1_check_2",
#     "ph1_check_3",
#     "ph1_check_4",
#     "ph1_check_5",
#     "ph1_photo_0",
#     "ph1_photo_1"
# ]


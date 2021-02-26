import sqlite3
import subprocess
import os
import uuid

class Database:
    def __init__(self, file_path, columns):
        self.file_path = file_path
        self.conn = sqlite3.connect(file_path)
        self.cur = self.conn.cursor()
        self.columns = columns
        column_set = set(columns)
        standard_columns = set(['id', 'start_time', 'end_time', 'survey'])
        if len(columns) > 0:
            try:
                self.cur.execute('select * from results')
            except sqlite3.OperationalError:
                self.reset()
            else:
                existing_cols = set([d[0] for d in self.cur.description])
                print('existing columns: ', existing_cols)
                if not standard_columns.issubset(existing_cols):
                    print("missing standard columns")
                    self.reset()
                if existing_cols != column_set.union(standard_columns):
                    # print('existing columns: ', existing_cols)
                    print('new columns: ', columns)
                    if existing_cols.issubset(columns):
                        extra_columns = [c for c in columns if c in (column_set - existing_cols)]
                        print ('adding columns: ', extra_columns)
                        for col in extra_columns:
                            self.commit("alter table results add column" + col + " text")
                    else:
                        self.reset()    

    def reset(self):
        self.backup()
        self.cur.execute("drop table if exists results")
        self.commit(
            """
                create table results (
                    id integer primary key,
                    survey text,
                    start_time TIMESTAMP NOT NULL,
                    end_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
                    {})
            """.format(
                ', '.join(c + ' text' for c in self.columns)
            )
        )

    def insert_record(self, record):
        column_list = ", ".join([c for c in self.columns])
        question_marks = ','.join(':' + c for c in ['survey', 'start_time'] + self.columns)
        query = f"INSERT INTO results (survey, start_time, {column_list}) VALUES ({question_marks})"
        print(query)
        self.commit(query, record)

    def results(self):
        if len(self.columns) == 0:
            return []
        self.cur.execute("select * from results")
        return [[d[0] for d in self.cur.description]] + self.cur.fetchall()

    def query(self, query):
        self.cur.execute(query)
        return self.cur.fetchall()

    def session_id(self):
        try:
            self.cur.execute('select value from session_id')
            result = self.cur.fetchone()[0]
            self.commit(f'update session_id set value={result + 1}')
            return result
        except (sqlite3.OperationalError, TypeError):
            self.cur.execute('drop table if exists session_id')
            self.cur.execute('create table session_id(value integer)')
            self.cur.execute('insert into session_id (value) values (0)')
            self.conn.commit()
            return 0


    def backup(self):
        self.conn.close()
        base, filename = os.path.split(self.file_path)
        name, ext = os.path.splitext(filename)
        backups = os.path.join(base, 'backups')
        backup_name = name + '_' + str(uuid.uuid4()) + '.' + ext
        try:
            subprocess.check_output(['/bin/bash', '-c', f'mkdir -p {backups}; cp {self.file_path} {backups}/{backup_name}'])
        except subprocess.CalledProcessError as e:
            print("Failed to create database backup: " + e.output)
            raise
        print("Backup successfull.")
        self.conn = sqlite3.connect(self.file_path)
        self.cur = self.conn.cursor()

    def commit(self, query, *args):
        self.cur.execute(query, *args)
        self.conn.commit()

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


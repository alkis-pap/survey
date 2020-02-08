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
        try:
            self.cur.execute('select * from results')
        except sqlite3.OperationalError:
            self.reset()
        else:
            existing_cols = set([d[0] for d in self.cur.description]) - set(['id', 'time', 'survey'])
            if existing_cols != columns:
                print('existing columns: ', existing_cols)
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
            "create table results (id integer primary key, survey text, time TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL, {})".format(
                ', '.join(c + ' text' for c in self.columns)
            )
        )

    def insert_record(self, record):
        column_list = ", ".join([c for c in self.columns])
        question_marks = ','.join(':' + c for c in ['survey'] + self.columns)
        query = f"INSERT INTO results (survey, {column_list}) VALUES ({question_marks})"
        print(query)
        self.commit(query, record)

    def results(self):
        self.cur.execute("select * from results")
        return [[d[0] for d in self.cur.description]] + self.cur.fetchall()

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


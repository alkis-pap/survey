import os
import psycopg2

DATABASE_URL = os.environ['DATABASE_URL']

conn = psycopg2.connect(DATABASE_URL, sslmode='require')

from flask import Flask

app = Flask(__name__, static_folder="./static/")


@app.route('/')
def hello_world():
    cur = conn.cursor()
    cur.execute("SELECT * FROM test;")
    return "\n".join(str(x) for x in cur.fetchall())
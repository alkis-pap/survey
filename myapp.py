import os
import psycopg2

DATABASE_URL = os.environ['DATABASE_URL']

conn = psycopg2.connect(DATABASE_URL, sslmode='require')

from flask import Flask, redirect, url_for 

app = Flask(__name__, static_folder="./static/")


@app.route('/')
def index():
    return redirect(url_for('static', filename='index.html'))

@app.route('/test')
def test():
    cur = conn.cursor()
    cur.execute("SELECT * FROM test;")
    return "\n".join(str(x) for x in cur.fetchall())
import os
import sqlite3
from flask import Flask, redirect, url_for, send_from_directory
import random
import atexit

log = open("log.txt", "w")
atexit.register(lambda: log.close())

conn = sqlite3.connect('data.db')
cur = conn.cursor()

app = Flask(__name__, static_folder="./static/")

@app.route('/')
def index():
    return redirect(url_for('static', filename='index.html'))

@app.route('/survey.json')
def survey():
    return send_from_directory('surveys', filename='survey{}.json'.format(random.randint(1, 4)))

@app.route('/update', methods=['POST'])
def post():
    log.write("a")
#     data = request.get_json()
#     if len(data) == n_questions:
#         cur.execute("INSERT INTO results VALUES (NOW()::timestamp, " + ",".join(["%d"] * n_questions) + ")", (data[key] for key in data))

# @app.route('/test')
# def test():
#     cur = conn.cursor()
#     cur.execute("SELECT * FROM test;")
#     return "\n".join(str(x) for x in cur.fetchall())
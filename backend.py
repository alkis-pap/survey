import os
import sqlite3
from flask import Flask, redirect, request, url_for, send_from_directory
import random

def log(msg):
    with open("log.txt", "w") as f:
        f.write(msg + '\n')

conn = sqlite3.connect('data.db')
cur = conn.cursor()

app = Flask(__name__, static_folder="./static/")

@app.route('/')
def index():
    return redirect(url_for('static', filename='index.html'))

@app.route('/survey.json')
def survey():
    filename = 'survey{}.json'.format(random.randint(1, 2))
    log(filename)
    return send_from_directory('surveys', filename=filename)

@app.route('/update', methods=['POST'])
def post():
    data = request.get_json()
    log(str(data))
#     if len(data) == n_questions:
#         cur.execute("INSERT INTO results VALUES (NOW()::timestamp, " + ",".join(["%d"] * n_questions) + ")", (data[key] for key in data))

# @app.route('/test')
# def test():
#     cur = conn.cursor()
#     cur.execute("SELECT * FROM test;")
#     return "\n".join(str(x) for x in cur.fetchall())
# import json

# surveys

# with open("static/survey.json") as f:
#     survey = json.load(f)

# question_types = ["matrix"]

# n_questions = sum(1 for page in survey["pages"] for question in page["questions"] if question["type"] in question_types)
n_questions = 2

import os
import psycopg2

DATABASE_URL = os.environ['DATABASE_URL']

conn = psycopg2.connect(DATABASE_URL, sslmode='require')
cur = conn.cursor()

from flask import Flask, redirect, url_for, send_from_directory
import random

app = Flask(__name__, static_folder="./static/")

@app.route('/')
def index():
    return redirect(url_for('static', filename='index.html'))

@app.route('/survey.json'):
def survey():
    return send_from_directory('surveys', filename='survey{}.json'.format(random.randint(1, 4)))

@app.route('/update', methods=['POST'])
def post():
    data = request.get_json()
    if len(data) == n_questions:
        cur.execute("INSERT INTO results VALUES (NOW()::timestamp, " + ",".join(["%d"] * n_questions) + ")", (data[key] for key in data))

@app.route('/test')
def test():
    cur = conn.cursor()
    cur.execute("SELECT * FROM test;")
    return "\n".join(str(x) for x in cur.fetchall())
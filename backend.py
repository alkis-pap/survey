import os
from flask import Flask, make_response, redirect, request, url_for, send_from_directory
import random

from make_survey import make_survey
import database as db
from util import flatten

def log(msg):
    with open("log.txt", "w+") as f:
        f.write(msg + '\n')

app = Flask(__name__, static_folder="./static/")

@app.route('/index.html')
def index():
    return redirect('/')

@app.route('/')
def main():
    return send_from_directory('static', filename='index.html')

@app.route('/survey.json')
def survey():
    print('survey.json', flush=True)
    surveys = os.listdir("surveys")
    filename = surveys[random.randint(0, len(surveys) - 1)]
    # log(filename)
    return make_survey(os.path.join("surveys", filename))

@app.route('/update', methods=['POST'])
def update():
    print("update", flush=True)
    data = flatten(request.get_json())
    log(str(data))
    db.insert_record(data)
    return 'OK'
    # log(str(data))
#     if len(data) == n_questions:
#         cur.execute("INSERT INTO results VALUES (NOW()::timestamp, " + ",".join(["%d"] * n_questions) + ")", (data[key] for key in data))

@app.route('/export')
def results():
    results = db.results()
    csv_text = "\n".join(",".join(str(val) for val in row) for row in results)
    output = make_response(csv_text)
    output.headers["Content-Disposition"] = "attachment; filename=export.csv"
    output.headers["Content-type"] = "text/csv"
    return output

# @app.route('/test')
# def test():
#     cur = conn.cursor()
#     cur.execute("SELECT * FROM test;")
#     return "\n".join(str(x) for x in cur.fetchall())
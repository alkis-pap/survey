import os
from flask import Flask, make_response, redirect, request, url_for, send_from_directory
import random

from survey import *
from database import *
from util import flatten

def log(msg):
    with open("log.txt", "w+") as f:
        f.write(msg + '\n')

try:
    os.mkdir("static/surveys")
except FileExistsError:
    pass
column_sets = []
for filename in os.listdir("surveys"):
    filepath = os.path.join("surveys", filename)
    if os.path.isfile(filepath):
        s = Survey(filepath)
        s.generate(os.path.join("static/surveys", filename))
        column_set = set(s.columns)
        if len(column_set) != len(s.columns):
            log("duplicate columns in " + filename)
            quit()
        if len(column_sets) > 0 and column_set != column_sets[-1]:
            log("different columns in " + filename)
            quit()
        column_sets.append(column_set)

db = Database("data.db", column_sets[0])

app = Flask(__name__, static_folder="./static/")

@app.route('/index.html')
def index():
    return redirect('/')

@app.route('/')
def main():
    return send_from_directory('static', filename='index.html')

@app.route('/survey.json')
def survey():
    surveys = os.listdir("static/surveys")
    filename = surveys[random.randint(0, len(surveys) - 1)]
    # log(filename)
    return send_from_directory('static/surveys', filename=filename)

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
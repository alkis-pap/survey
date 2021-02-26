import os
import shutil
from flask import Flask, flash, make_response, render_template, session, redirect, request, url_for, send_from_directory
from werkzeug.utils import secure_filename
import random
from mimetypes import guess_type
from datetime import datetime, timedelta

from survey import *
from database import *
from util import flatten
import secret

print('starting survey service')

class AppState:
    def __init__(self):
        pass
    
    def init(self):
        column_lists = []
        try:
            os.mkdir('static/surveys')
        except FileExistsError:
            shutil.rmtree('static/surveys')
            os.mkdir('static/surveys')
        
        self.logs = []

        for filename in os.listdir('static/files'):
            filepath = os.path.join('static/files', filename)
            if filename.endswith('.json') and os.path.isfile(filepath):
                try:
                    s = Survey(filepath)
                    s.generate(os.path.join('static/surveys', filename))
                    column_lists.append(s.columns)
                except SurveyError as e:
                    print(e)
                    self.log(str(e))

        if len(column_lists) == 0:
            columns = []
        elif len(column_lists) == 1:
            columns = column_lists[0]
        else:
            column_sets = [set(l) for l in column_lists]
            common = column_sets[0].intersection(*column_sets[1:])
            columns = [c for c in column_lists[0] if c in common]
        # print(columns)
        self.db = Database('data.db', columns)

    def log(self, msg):
        now = datetime.now()
        for line in msg.split('\n'):
            self.logs.append((now, line))
    

state = AppState()
state.init()

app = Flask(__name__, static_folder='./static/')

app.secret_key = secret.SECRET_KEY

@app.route('/index.html')
def index():
    return redirect('/')


surveys = os.listdir('static/surveys')
# random.shuffle(surveys)

# @app.before_request
# def before_request():
#     if 'id' not in session:
#         session['id'] = state.db.session_id()

sessions = {s : [] for s in surveys}

def remove_expired_sessions():
    now = datetime.now()
    for k in sessions:
        sessions[k] = [t for t in sessions[k] if now - t < timedelta(minutes=50)]

@app.route('/', methods=['GET'])
def main():
    if 'survey' not in session:
        # survey_id = state.db.session_id() % len(surveys)
        remove_expired_sessions()
        res = state.db.query("select survey, count(*) from results where autfunct_6 = 2 and emregul_6 = 5 and IMI_a_11 = 2 group by survey")
        counts = {k : len(sessions[k]) for k in sessions}
        for row in res:
            counts[row[0]] += row[1]
        print(counts)
        min_count = min(counts.values())
        candidate_surveys = [k for k in counts if counts[k] == min_count]
        selected_survey = candidate_surveys[random.randint(0, len(candidate_surveys) - 1)]
        sessions[selected_survey].append(datetime.now())
        session['survey'] = selected_survey
        session['start_time'] = datetime.now().isoformat(sep=' ', timespec='seconds')
    name = request.args.get("name")
    if name is None:
        name = session['survey']
    print(name)
    print(session)
    print('completed' in session)
    return render_template('index.html', survey=name, completed='completed' in session)

@app.route('/submit', methods=['POST'])
def submit():
    # print('submit', flush=True)
    # if 'survey' in session:
    session['completed'] = True
    data = flatten(request.get_json())
    data['survey'] = session['survey']
    data['start_time'] = session['start_time']
    state.db.insert_record(data)
    return 'OK'
    
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        if request.form['pass'] == secret.ADMIN_PASS:
            session['admin'] = True
            return redirect(url_for('admin', _external=True))
        else:
            redirect('/login')
    return '''
        <form method="post">
            <p><input type=text name=pass>
            <p><input type=submit value=Login>
        </form>
    '''
@app.route('/admin')
def admin():
    if 'admin' in session:
        files = [f for f in os.listdir('static/files') if os.path.isfile(os.path.join('static/files', f))]
        return render_template(
            "admin.html", 
            files=sorted(files, key=lambda x: "__" + x if x.endswith('.json') else x),
            results=state.db.results(),
            logs=state.logs
        )
    else:
        return redirect('/login')

@app.route('/delete_file/<filename>', methods=['POST'])
def delete_file(filename=None):
    if 'admin' in session and filename is not None and os.path.isfile(os.path.join('static/files', filename)):
        os.remove(os.path.join('static/files', filename))
        state.init()
        return redirect(url_for('admin'))

@app.route('/files/<filename>')
def files(filename=None):
    # if filename is not None and os.path.isfile(os.path.join('static/files', filename)):
    return send_from_directory('static/files', filename=filename, mimetype=guess_type(filename)[0])

@app.route('/upload', methods=['POST'])
def upload():
    if 'admin' in session:
        for file in request.files.getlist('files'):
            print(file)
            filename = secure_filename(file.filename)
            if filename != '':
                file.save(os.path.join('static/files', filename ))
        state.init()
        return redirect(url_for('admin'))


@app.route('/export')
def export():
    if 'admin' in session:
        results = state.db.results()
        csv_text = "\n".join(",".join(str(val) for val in row) for row in results)
        output = make_response(csv_text)
        output.headers["Content-Disposition"] = "attachment; filename=export.csv"
        output.headers["Content-type"] = "text/csv"
        return output


if __name__ == "__main__":
    print("main")
    app.run(extra_files=[os.path.join('templates', f) for f in os.listdir('templates')])
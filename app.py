import os
import shutil
from flask import Flask, flash, make_response, render_template, session, redirect, request, url_for, send_from_directory
import random
from mimetypes import guess_type

from survey import *
from database import *
from util import flatten

print('starting survey service')

class AppState:
    def __init__(self):
        pass
    
    def init(self):
        column_sets = []
        _surveys = []
        try:
            os.mkdir('static/surveys')
        except FileExistsError:
            shutil.rmtree('static/surveys')
            os.mkdir('static/surveys')
        for filename in os.listdir('static/files'):
            filepath = os.path.join('static/files', filename)
            if filename.endswith('.json') and os.path.isfile(filepath):
                s = Survey(filepath)
                column_set = set(s.columns)
                # if len(column_set) != len(s.columns):
                #     raise Exception('duplicate columns in ' + filename)
                # if len(column_sets) > 0 and column_set != column_sets[-1]:
                #     raise Exception('different columns in ' + filename)
                # _surveys.append((os.path.join('generated', filename), s))
                s.generate(os.path.join('static/surveys', filename))
                column_sets.append(column_set)
        print(column_sets[0])
        self.db = Database('data.db', column_sets[0])

state = AppState()
state.init()

app = Flask(__name__, static_folder='./static/')

app.secret_key = b'\xaf\x82\xfa\xf6\xc8\xd6o\xcc\xa4\x10\xd2\xad\x90\xd0\x01\xb6'
PASSWORD = 'fregoalcomplex'

@app.route('/index.html')
def index():
    return redirect('/')

@app.route('/', methods=['GET'])
def main():
    name = request.args.get("name")
    surveys = os.listdir('static/surveys')
    print(surveys)
    if name is None:
        name = surveys[random.randint(0, len(surveys) - 1)]
    print(name)
    return render_template('index.html', survey=name)

@app.route('/submit', methods=['POST'])
def submit():
    print('submit', flush=True)
    data = flatten(request.get_json())
    state.db.insert_record(data)
    return 'OK'
    
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        if request.form['pass'] == PASSWORD:
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
        return render_template("admin.html", files=sorted(files, key=lambda x: "__" + x if x.endswith('.json') else x))
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
    if 'admin' in session and filename is not None and os.path.isfile(os.path.join('static/files', filename)):
        return send_from_directory('static/files', filename=filename, mimetype=guess_type(filename)[0])

@app.route('/upload', methods=['POST'])
def upload():
    if 'admin' in session:
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file:
            file.save(os.path.join('static/files', file.filename))
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
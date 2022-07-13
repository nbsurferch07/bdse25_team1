import os
from flask import Flask, render_template, request, redirect, url_for
UPLOAD_FOLDER = './static/img'

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/about')
def about():
    return render_template('about.html')


@app.route('/pattern', methods=['GET', 'POST'])
def pattern():
    return render_template('pattern.html')

@app.route('/uploader', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        file = request.files["file"]
        if file.filename != '':
            file.save(os.path.join(UPLOAD_FOLDER, file.filename))
            return redirect(url_for('pattern'))

@app.route('/mortgate_calculator')
def mortgate_calculator():
    return render_template('mortgage.html')


@app.route('/affordable_calculator')
def affordable_calculator():
    return render_template('affordable.html')

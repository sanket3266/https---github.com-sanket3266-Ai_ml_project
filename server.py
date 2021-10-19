import os
import flask
from flask import Flask, flash, render_template, redirect, request, send_file, url_for

app = Flask(__name__)
app.config['SECRET_KEY'] = 'Thisistheserverkey'
app.config['UPLOAD_FOLDER'] = '/tmp/*'

@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'GET':
        # show the upload form
        return render_template('home.html')

    if request.method == 'POST':
        # check if a file was passed into the POST request
        if 'image' not in request.files:
            flash('No file was uploaded.')
            return redirect(request.url)

        image_file = request.files['image']

        # if filename is empty, then assume no upload
        if image_file.filename == '':
            flash('No file was uploaded.')
            return redirect(request.url)

        # if the file is "legit"
        if image_file:
            passed = False
            try:
                filepath = os.path.join('/tmp/', image_file.filename)
                image_file.save(filepath)
                passed = True
            except Exception:
                passed = False


            if passed:
                return redirect(url_for('predict', filename=image_file.filename))
            else:
                flash('An error occurred, try again.')
                return redirect(request.url)

@app.route('/images/<filename>', methods=['GET'])
def images(filename):
    return send_file(os.path.join('/tmp/', filename))

if __name__ == "__main__":
    app.run('127.0.0.1')
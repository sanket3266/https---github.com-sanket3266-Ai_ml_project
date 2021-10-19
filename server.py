import os
from flask import Flask, flash, render_template, redirect, request, send_file, url_for
import random
from werkzeug.utils import secure_filename
from numpy import pi
from bokeh.plotting import figure
from bokeh.embed import components

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ['SECRET_KEY']
app.config['UPLOAD_FOLDER'] = os.environ['UPLOAD_FOLDER']


IMAGE_LABELS = ['Apple Apple scab', 'Apple Black rot', 'Apple Ceda', 'Apple rust',
                'Apple healthy', 'Blueberry healthy', 'Cherry (including sour) healthy',
                'Cherry (including sour) Powdery mildew', 'Corn (maize) Cercospora leaf spot Gray leaf spot',
                'Corn (maize) Common rust', 'Corn (maize) healthy', 'Corn (maize) Northern Leaf Blight',
                'Grape Black rot', 'Grape Esca (Black Measles)', 'Grape healthy',
                'Grape Leaf blight (Isariopsis Leaf Spot)', 'Orange Haunglongbing (Citrus greening)',
                'Peach Bacterial spot', 'Peach healthy', 'Pepper bell Bacterial spot',
                'Pepper bell healthy', 'Potato Early blight',
                'Potato healthy', 'Potato Late blight', 'Raspberry healthy',
                'Soybean healthy', 'Squash Powdery mildew', 'Strawberry healthy',
                'Strawberry Leaf scorch', 'Tomato Bacterial spot',
                'Tomato Early blight', 'Tomato healthy', 'Tomato Late blight',
                'Tomato Leaf Mold', 'Tomato Septoria leaf spot',
                'Tomato Spider mites Two-spotted spider mite', 'Tomato Target Spot',
                'Tomato Tomato mosaic virus', 'Tomato Tomato Yellow Leaf Curl Virus']

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

        if image_file and is_allowed_file(image_file.filename):
            passed = False
            try:
                filename = generate_random_name(image_file.filename)
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                image_file.save(filepath)
                passed = True
            except Exception:
                passed = False

        # if the file is "legit"
        if image_file:
            passed = False
            try:
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], image_file.filename)
                image_file.save(filepath)
                passed = True
            except Exception:
                passed = False


            if passed:
                return redirect(url_for('predict', filename=image_file.filename))
            else:
                flash('An error occurred, try again.')
                return redirect(request.url)

@app.route('/predict/<filename>', methods=['GET'])
def predict(filename):
    image_url = url_for('images', filename=filename)
    predictions = [0.1, 0.5, 0.3, 0.75, 0.9, 0.5, 0.1, 0.0]
    script, div = generate_barplot(predictions)
    return render_template(
        'predict.html',
        plot_script=script,
        plot_div=div,
        image_url=image_url
    )
@app.errorhandler(500)
def server_error(error):
    return render_template('error.html'), 500

@app.route('/images/<filename>', methods=['GET'])
def images(filename):
    return send_file(os.path.join(app.config['UPLOAD_FOLDER'], filename))

ALLOWED_EXTENSIONS = set(['png', 'bmp', 'jpg', 'jpeg', 'gif'])

def is_allowed_file(filename):
    """ Checks if a filename's extension is acceptable """
    allowed_ext = filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
    return '.' in filename and allowed_ext

LETTER_SET = list(set('ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'))

def generate_random_name(filename):
    """ Generate a random name for an uploaded file. """
    ext = filename.split('.')[-1]
    rns = [random.randint(0, len(LETTER_SET) - 1) for _ in range(3)]
    chars = ''.join([LETTER_SET[rn] for rn in rns])

    new_name = "{new_fn}.{ext}".format(new_fn=chars, ext=ext)
    new_name = secure_filename(new_name)

    return new_name

def generate_barplot(predictions):
    """ Generates script and `div` element of bar plot of predictions using
    Bokeh
    """
    plot = figure(x_range=IMAGE_LABELS, plot_height=300, plot_width=400)
    plot.vbar(x=IMAGE_LABELS, top=predictions, width=0.8)
    plot.xaxis.major_label_orientation = pi / 2.

    return components(plot)

if __name__ == "__main__":
    app.run('127.0.0.1')

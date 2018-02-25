from flask import Flask, request, redirect, url_for, render_template, flash

from ocean_efficiency.model.Journey import Journey
from ocean_efficiency.xmlparse.RouteModel import RouteModel

UPLOAD_FOLDER = '/Users/ben.marengo/Downloads'
ALLOWED_EXTENSIONS = {'xml'}


app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 1 * 1024 * 1024


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)

        # if user does not select file, browser also
        # submit a empty part without filename
        file = request.files['file']
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)

        if file and allowed_file(file.filename):
            xml_str = file.read().strip()
            rm = RouteModel.parse(xml_str)
            j = Journey(rm)
            return str(j)
            # return redirect(url_for('uploaded_file', filename=filename))
    return render_template('upload_file.html')


if __name__ == '__main__':
    app.run()

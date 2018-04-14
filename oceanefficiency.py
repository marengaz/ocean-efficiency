from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from flask import Flask, request, redirect, url_for, render_template, flash
from geoalchemy2 import WKTElement
from sqlalchemy import func

from ocean_efficiency.legacy_model.Journey import Journey
from ocean_efficiency.utils.db import provide_session
from ocean_efficiency.www.forms import LatLongForm
from ocean_efficiency.xmlparse.RouteModel import RouteModel
from ocean_efficiency.model import EEZ12, WorldBorders

UPLOAD_FOLDER = '/Users/ben.marengo/Downloads'
ALLOWED_EXTENSIONS = {'xml'}


app = Flask(__name__, template_folder='ocean_efficiency/www/templates')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 1 * 1024 * 1024


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/', methods=['GET', 'POST'])
@app.route('/lookup_coordinates', methods=['GET', 'POST'])
@provide_session
def lookup_coordinates(session):
    form = LatLongForm(request.form)
    if request.method == 'POST' and form.validate():
        lon = form.longitude.data
        lat = form.latitude.data

        current_point = WKTElement('POINT(%s %s)' % (lon, lat), srid=4326)

        zones = session\
            .query(EEZ12.geoname)\
            .filter(func.ST_Within(current_point, EEZ12.geom))\
            .order_by(EEZ12.geoname)\
            .all()

        countries = session\
            .query(WorldBorders.name)\
            .filter(func.ST_Within(current_point, WorldBorders.geom))\
            .order_by(WorldBorders.name)\
            .all()

        data = {
            'input_lat': lat,
            'input_lon': lon,
            'zones': [r.geoname for r in zones],
            'countries': [r.name for r in countries],
        }

        return render_template('ocean/lookup_coordinates.html', form=form, data=data)
    return render_template('ocean/lookup_coordinates.html', form=form, data=None)


@app.route('/route_upload', methods=['GET', 'POST'])
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
            j = Journey.from_route_model(rm)
            return str(j)
            # return redirect(url_for('uploaded_file', filename=filename))
    return render_template('ocean/upload_file.html')


if __name__ == '__main__':
    app.run()

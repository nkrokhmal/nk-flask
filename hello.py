from flask import Flask, request, make_response, redirect, abort, render_template, flash, session, url_for
from flask_bootstrap import Bootstrap
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed, FileRequired
from wtforms import StringField, FloatField, SubmitField, SelectField
from wtforms.ext.sqlalchemy.fields import QuerySelectField
from wtforms.validators import Required, InputRequired
from programs.model import *
from io import BytesIO
import os
import requests
import json
from flask_cors import CORS

from requests_toolbelt.multipart.encoder import MultipartEncoder


host_prod = 'http://flask-backend:8818'
#host_prod = 'http://35.228.186.127'
#host_prod = 'http://0.0.0.0:8818'

app = Flask(__name__)
CORS(app)

app.config['SECRET_KEY'] = 'Alisa'
bootstrap = Bootstrap(app)

basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///' + os.path.join(basedir, 'data.postgresql')
app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True


class NameForm(FlaskForm):
    name = StringField('What is your name?', validators=[Required()])
    curname = StringField('What is your curname?', validators=[Required()])
    submit = SubmitField('Submit')


class ImageForm(FlaskForm):
    url = StringField('What is your avatar?', validators=[Required()])
    submit = SubmitField('Submit')


class UploadForm(FlaskForm):
    validators = [
        FileRequired(message='There was no file!'),
        FileAllowed(['mat'], message='Must be a mat file!')
    ]

    input_file = FileField('', validators=validators)
    model_name = StringField("Enter model name:", validators=[Required()])
    dxvalue = FloatField("Enter value dx, m: ", validators=[Required()])
    submit = SubmitField(label="Submit")


class ScattererForm(FlaskForm):
    model_names_list = SelectField('Field name',  coerce=int, validators=[InputRequired()])
    radius = FloatField("Enter value radius, mm", default=0.0001)
    longitudinal = FloatField("Enter longitudinal speed of sound, m/s", default=2620.0)
    transverse = FloatField("Enter transverse speed of sound, m/s", default=1080.0)
    density_of_scatter = FloatField("Enter density of scatterer, kg/m^3", default=1125.0)
    frequency = FloatField("Enter value of frequency", default=1000000)
    speed_of_sound = FloatField("Enter value of frequency", default=1500.0)
    density_of_medium = FloatField("Enter density of medium", default=1000.0)
    type_value = StringField("Enter type of coordinates (X, Y or Z)", default='Z')
    from_value = FloatField("Enter begin coordinate value", default=-0.02)
    to_value = FloatField("Enter end coordinate value", default=0.02)
    step = FloatField("Enter step value", default=0.001)
    submit = SubmitField(label="Submit")


@app.route("/models", methods=['GET', 'POST', 'PUT', 'DELETE'])
def models():
    data = requests.get(host_prod + '/api/models/').json()
    print(data)
    return render_template('models.html', data=json.loads(data), host=host_prod)


@app.route("/scatterer", methods=['GET', 'POST'])
def scatterer():
    form = ScattererForm()
    data = requests.get(host_prod + '/api/models/').json()
    data = json.loads(data)
    form.model_names_list.choices = [(i, m['model_name']) for i, m in enumerate(data)]
    figure = None
    if request.method == 'POST' and form.validate_on_submit():
        model_info = data[form.model_names_list.data]
        session['Radius'] = form.radius.data
        session['LongitudinalSpeed'] = form.longitudinal.data
        session['TransverseSpeed'] = form.transverse.data
        session['DensityOfScatterer'] = form.density_of_scatter.data
        session['Frequency'] = form.frequency.data
        session['SpeedOfSound'] = form.speed_of_sound.data
        session['DensityOfMedium'] = form.density_of_medium.data
        session['Type'] = form.type_value.data
        session['From'] = form.from_value.data
        session['To'] = form.to_value.data
        session['Step'] = form.step.data
        session['Dx'] = 0.00025
        session['ModelPath'] = 'models/{}.mat'.format(model_info['model_name'])
        session['ModelName'] = model_info['id']
        url = host_prod + '/api/scatterer/'
        headers = {
            'cache-control': "no-cache",
        }
        data = {
            'Radius': session['Radius'],
            'LongitudinalSpeed': session['LongitudinalSpeed'],
            'TransverseSpeed': session['TransverseSpeed'],
            'DensityOfScatterer': session['DensityOfScatterer'],
            'Frequency': session['Frequency'],
            'SpeedOfSound': session['SpeedOfSound'],
            'DensityOfMedium': session['DensityOfMedium'],
            'Dx': session['Dx'],
            'Type': session['Type'],
            'From': session['From'],
            'To': session['To'],
            'Step': session['Step'],
            'ModelPath': session['ModelPath'],
            'ModelName': session['ModelName']
        }
        r = requests.post(url, headers=headers, data=data)
        if r.status_code != 200:
            flash_errors(form)
        else:
            figure = r.content.decode('ascii').replace('"', '')

        print(figure)

        form.radius.data = None
        form.longitudinal.data = None
        form.transverse.data = None
        form.density_of_scatter.data = None
        form.frequency.data = None
        form.speed_of_sound.data = None
        form.density_of_medium.data = None
        form.type_value.data = None
        form.from_value.data = None
        form.to_value.data = None
        form.step.data = None

    return render_template('scatterer.html', form=form, figure=figure, data=data)



@app.route("/loadmodel", methods=['GET', 'POST'])
def modelfield():
    form = UploadForm()
    figure = None
    if request.method == 'POST' and form.validate_on_submit():
        file_bytes = request.files['input_file'].read()
        session['dx'] = form.dxvalue.data
        session['model_name'] = form.model_name.data

        if len(file_bytes) > 0:
            figure = show_model(BytesIO(file_bytes), session['dx'])
            print(figure)

        url = host_prod + '/api/savemodel/'
        headers = {
            'cache-control': "no-cache",
        }
        data = {
            'ModelName': session['model_name'],
            'Parameters': json.dumps({'dx': session['dx']}),
        }
        files = {
            'ModelFile': file_bytes,
            'DistributionFile': base64.b64decode(figure)
        }
        r = requests.post(url, headers=headers, data=data, files=files)
        if r.status_code != 200:
            flash_errors(r.content)
        else:
            flash('Model {}  successfully loaded!'.format(session['model_name']), 'info')
    else:
        flash_errors(form)

    request.files = None
    form.dxvalue.data = None
    form.input_file.data = None
    form.model_name.data = None
    print(figure)

    return render_template('loadmodel.html', form=form, figure=figure)


def flash_errors(form):
    """Flashes form errors"""
    for field, errors in form.errors.items():
        for error in errors:
            flash(u"Error in the %s field - %s" % (
                getattr(form, field).label.text,
                error
            ), 'error')


@app.route("/", methods=['GET', 'POST'])
def home():
    return render_template('home.html')


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500


if __name__ == "__main__":
    app.run(port=5000, debug=True, threaded=True, host='0.0.0.0')

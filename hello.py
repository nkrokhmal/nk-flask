from flask import Flask, request, make_response, redirect, abort, render_template, flash, session, url_for
from flask_bootstrap import Bootstrap
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed, FileRequired
from wtforms import StringField, FloatField, SubmitField
from wtforms.validators import Required
from programs.model import *
from io import BytesIO
import os
import requests
import json
from flask_cors import CORS

from requests_toolbelt.multipart.encoder import MultipartEncoder


host_prod = 'http://flask-backend:6666'
#host_prod = 'http://35.228.186.127'
host_prod = 'http://0.0.0.0:8080'

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
    radius = FloatField("Enter value radius, mm", validators=[Required()])
    longitudinal = FloatField("Enter longitudinal speed of sound, m/s", validators=[Required()])
    transverse = FloatField("Enter transverse speed of sound, m/s", validators=[Required()])
    density = FloatField("Enter density of scatterer, kg/m^3", validators=[Required()])
    submit = SubmitField(label="Submit")


@app.route("/models", methods=['GET', 'POST', 'PUT', 'DELETE'])
def models():
    data = requests.get(host_prod + '/api/models/').json()
    return render_template('models.html', data=json.loads(data), host=host_prod)


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


@app.route("/scatterer", methods=['GET', 'POST'])
def scatterer():
    form = ScattererForm()
    return render_template('scatterer.html', form=form)



@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500


if __name__ == "__main__":
    app.run(port=5000, debug=True, threaded=True, host='0.0.0.0')

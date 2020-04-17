from flask import Flask, request, make_response, redirect, abort, render_template, flash, session, url_for
from flask_bootstrap import Bootstrap
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed, FileRequired
from wtforms import StringField, FloatField, SubmitField
from wtforms.validators import Required
from programs.model import *
from io import BytesIO
import os
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SECRET_KEY'] = 'Alisa'
bootstrap = Bootstrap(app)

basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///' + os.path.join(basedir, 'data.postgresql')
app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True

db = SQLAlchemy(app)


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
    dx = FloatField("Enter value dx, m: ", validators=[Required()])
    submit = SubmitField(label="Submit")


class ScattererForm(FlaskForm):
    radius = FloatField("Enter value radius, mm", validators=[Required()])
    longitudinal = FloatField("Enter longitudinal speed of sound, m/s", validators=[Required()])
    transverse = FloatField("Enter transverse speed of sound, m/s", validators=[Required()])
    density = FloatField("Enter density of scatterer, kg/m^3", validators=[Required()])
    submit = SubmitField(label="Submit")


@app.route('/')
def index():
    user_agent = request.headers.get('User-Agent')
    return '<p>Your browser is %s</p>' % user_agent


@app.route("/modelfield", methods=['GET', 'POST'])
def modelfield():
    form = UploadForm()
    figure = None
    if request.method == 'POST' and form.validate_on_submit():
        file = BytesIO(request.files['input_file'].read())
        session['dx'] = form.dx.data

        if file is not None:
            figure = show_model(file, session['dx'])

        form.dx.data = None
        form.input_file.data = None
    else:
        flash_errors(form)

    return render_template('model.html', form=form, figure=figure)


def flash_errors(form):
    """Flashes form errors"""
    for field, errors in form.errors.items():
        for error in errors:
            flash(u"Error in the %s field - %s" % (
                getattr(form, field).label.text,
                error
            ), 'error')


@app.route("/user", methods=['GET', 'POST'])
def user():
    form = NameForm()
    im_form = ImageForm()
    if form.validate_on_submit():
        old_name = session.get('name')
        old_curname = session.get('curname')
        if old_name is not None and old_name != form.name.data:
            flash('Looks like you have changed your name!')
        if old_curname is not None and old_curname != form.curname.data:
            flash('Looks like you have changed your curname!')
        session['name'] = form.name.data
        session['curname'] = form.curname.data
        form.name.data = ''
        form.curname.data = ''
        return redirect(url_for('user'))
    if im_form.validate_on_submit():
        session['image'] = im_form.url.data
        im_form.url.data = ''

    return render_template('user.html', form=form, im_form=im_form,
                           name=session.get('name'), curname=session.get('curname'),
                           image=session.get('image'))


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

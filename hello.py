from flask import Flask
from flask import request
from flask import make_response
from flask import redirect
from flask import abort
from flask import render_template
from flask_bootstrap import Bootstrap
from flask_wtf import Form
from wtforms import StringField, SubmitField
from wtforms.validators import Required

app = Flask(__name__)
app.config['SECRET_KEY'] = 'Alisa=Dyrinda'
bootstrap = Bootstrap(app)


# moment = Moment(app)

# class NameForm(Form):
#     def __init__(self, question, *args, **kwargs):
#         Form.__init__(self, *args, **kwargs)
#         self.name = StringField(question, validators=[Required()])
#         self.submit = SubmitField('Submit')

class NameForm(Form):
    name = StringField('What is your name?', validators=[Required()])
    curname = StringField('What is your curname?', validators=[Required()])
    submit = SubmitField('Submit')


@app.route('/')
def index():
    user_agent = request.headers.get('User-Agent')
    return '<p>Your browser is %s</p>' % user_agent


@app.route('/cookie')
def cookie():
    response = make_response('<h1>This document carries a cookie!</h1>')
    response.set_cookie('answer', 42)
    return response


@app.route('/redirect')
def redirect():
    return redirect('http://example.com')


@app.route('/username/<user>')
def user_error(username):
    if not username:
        abort(404)
    return '<h1>Hello, %s</h1>' % username


@app.route("/user", methods=['GET', 'POST'])
def user():
    name = None
    curname = None
    form = NameForm()

    if form.validate_on_submit():
        name = form.name.data
        curname = form.curname.data
        form.name.data = ''
        form.curname.data = ''
    return render_template('user.html', form=form, name=name, curname=curname)


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500


if __name__ == "__main__":
    app.run(debug=True)

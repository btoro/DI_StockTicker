from flask import Flask, render_template, request, redirect
from flask_wtf import FlaskForm as Form
from wtforms import FieldList, FormField, StringField, TextField, FloatField, IntegerField, BooleanField, TextAreaField, SubmitField, RadioField, SelectField, validators

app = Flask(__name__)

import os

app.secret_key = os.environ.get("FLASK_SECRET_KEY", "you-will-never-guess")


class tickerlookupSubmitForm(Form):

    ticker = TextField(
        'Ticker', [validators.optional()])




@app.route('/', methods=['post', 'get'])
def index():

  # if request.method == 'POST':
  #   return render_template('plot.html', form=form )

  # else:

  form = tickerlookupSubmitForm(request.form)

  return render_template('index.html', form=form )



@app.route('/lookup/<string:id>')
def tickerplot(id):
  print( id )
  return render_template('lookup.html', id=id)


@app.route('/about')
def about():
  return render_template('about.html')

if __name__ == '__main__':
  app.run(port=33507, debug=True)






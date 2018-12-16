import os
from flask import Flask, render_template, request, redirect, flash
from flask_wtf import FlaskForm as Form
from wtforms import FieldList, FormField, StringField, TextField, FloatField, IntegerField, BooleanField, TextAreaField, SubmitField, RadioField, SelectField, DateField, validators
from wtforms.fields.html5 import IntegerRangeField

from stock_data import getPlotData, createFigure, filterDatabyRange

import requests
import pandas as pd

from bokeh.plotting import figure
from bokeh.embed import components
from bokeh.models.sources import ColumnDataSource

yaxis_choices = [('open', 'Opening Price'),
                 ('close', 'Closing Price'),
                 ('high', 'High Price'),
                 ('low', 'Low Price'),
                 ('adj_open', 'Adjusted Opening Price'),
                 ('adj_close', 'Adjusted Closing Price'),
                 ('adj_high', 'Adjusted High Price'),
                 ('adj_low', 'Adjusted Low Price'),
                 ]

app = Flask(__name__)

month_choices = [(1, 'January'), (2, 'February'), (3, 'March'), (4, 'April'),
                 (5, 'May'), (6, 'June'), (7, 'July'), (8,
                                                        'August'), (9, 'September'),
                 (10, 'October'), (11, 'November'), (12, 'December')]


errormsg = [
    (0, 0), ('No records found within selection range. Displaying all data.', 'warning'),
    ('Unable to make request.', 'danger'),
    ('Could not find stock ticker.', 'danger'),
]

app.secret_key = os.environ.get("FLASK_SECRET_KEY", "you-will-never-guess")


class tickerlookupSubmitForm(Form):
    ticker = TextField(
        'Ticker', [validators.required()])


class tickerloopup_settingsForm(Form):
    ticker = TextField('Ticker')

    yaxis = SelectField('Pricing data', choices=yaxis_choices)
    yearChoices = [(2018, 2018)]

    startMonth = SelectField('Month', choices=month_choices)
    startYear = SelectField('Year', choices=yearChoices)

    endMonth = SelectField('Month', choices=month_choices)
    endYear = SelectField('Year', choices=yearChoices)


@app.route('/', methods=['post', 'get'])
def index():
    form = tickerlookupSubmitForm(request.form)

    if request.method == 'POST':
        ticker = form.ticker.data
        return redirect('/lookup/{}'.format(ticker))
    else:

        return render_template('index.html', form=form)


@app.route('/lookup/<string:id>', methods=['post', 'get'])
def tickerplot(id):

    form = tickerloopup_settingsForm(request.form)
    error = 0

    if request.method == 'POST':
        if form.ticker.data != id:
            return redirect('/lookup/{}'.format(form.ticker.data), code=307)

        data, error = getPlotData(id)

        # Check for: request and result count
        if(error):
            flash(errormsg[error][0], errormsg[error][1])
            return render_template('lookup.html', id=[], the_div=[], the_script=[], form=form)

        yaxis = request.form.get('yaxis')
        label = dict(form.yaxis.choices).get(form.yaxis.data)

        data2, error = filterDatabyRange(
            data, int(form.startYear.data), int(form.startMonth.data), int(form.endYear.data), int(form.endMonth.data),)

        # Check for: filter result count
        if(error):
            flash(errormsg[error][0], errormsg[error][1])
            return render_template('lookup.html', id=None, the_div=None, the_script=None, form=form)
    else:
        data, error = getPlotData(id)

        # Check for: request and result count
        if(error):
            flash(errormsg[error][0], errormsg[error][1])
            return render_template('lookup.html', id=[], the_div=[], the_script=[], form=form)

        yaxis = 'close'
        label = 'Closing Price'
        data2 = data
        form.ticker.data = id

    maxyear = data['date'].dt.year.max()
    minyear = data['date'].dt.year.min()

    choices = []
    for year in range(minyear, maxyear+1):
        choices.append((year, year))

    form.endYear.default = maxyear
    form.endMonth.default = 12

    form.startYear.choices = choices
    form.endYear.choices = choices

    plot = createFigure(data2, yaxis, id, 'Date', label)

    script, div = components(plot)

    return render_template('lookup.html', id=id, the_div=div, the_script=script, form=form)


@app.route('/about')
def about():
    return render_template('about.html')


if __name__ == '__main__':
    app.run(port=33507, debug=True)

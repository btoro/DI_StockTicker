from bokeh.models import Range1d
from bokeh.models.sources import ColumnDataSource
from bokeh.embed import components
from bokeh.plotting import figure
import requests
import pandas as pd


def getPlotData(ticker):
    api = '7mF86XvCkjAfdKj7yv1M'
    r = requests.get(
        'https://www.quandl.com/api/v3/datatables/WIKI/prices.json?ticker={}&api_key={}'.format(ticker, api))

    df = 0
    error = 0

    if r.status_code != 200:
        error = 2
        return df, error

    j = r.json()

    df = pd.DataFrame(j['datatable']['data'])

    if(df.empty):
        error = 3
        return df, error

    columnNames = []

    for x in j['datatable']['columns']:
        columnNames.append(x['name'])
    df.columns = columnNames

    df['date'] = pd.to_datetime(df['date'], format='%Y-%m-%d')

    return df, error


def filterDatabyRange(df, startYear, startMonth, endYear, endMonth):
    df2 = df.copy()
    import datetime

    mask = (df2['date'] >= datetime.date(year=startYear, month=startMonth, day=1)) & (
        df2['date'] < datetime.date(year=endYear, month=endMonth, day=1))

    df2 = df2[mask]
    error = 0

    if(df2.shape[0] > 0):

        return df2, error
    else:
        error = 1
        return df, error


def createFigure(data, y_select, title, x_name, y_name,
                 width=1200, height=600):
    source = ColumnDataSource(data)

    p = figure(title='Stock selected: {}'.format(title),  x_axis_type="datetime", plot_width=width, plot_height=height, h_symmetry=False, v_symmetry=False,
               min_border=0, toolbar_location="above",
               outline_line_color="#666666")

    p.xaxis.axis_label = x_name
    p.yaxis.axis_label = y_name

    interval = 50
    ymin = data[y_select].min()-50
    if ymin < 0:
        ymin = 0

    p.y_range = Range1d(ymin, data[y_select].max(
    )+interval, bounds=(ymin, data[y_select].max()+interval))

    print(ymin)

    p.x_range = Range1d(data['date'].min(), data['date'].max(), bounds=(
        data['date'].min(), data['date'].max()))

    # tools=tools,

    p.line(x='date', y=y_select, source=source)
    return p

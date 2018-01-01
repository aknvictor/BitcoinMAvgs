import os
import datetime as dt
import time
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State, Event
import plotly.plotly as py
from plotly.graph_objs import *
import numpy as np
from scipy.stats import rayleigh
from tinydb import TinyDB, Query
from flask import Flask, send_from_directory

server = Flask('BitcoinMAvgs')

app = dash.Dash('BitcoinMAvgs-App', server=server,
                url_base_pathname='/dash/',
                csrf_protect=False)


app.layout = html.Div([

    html.Div([
        html.H2("Bitcoin prices with moving averages")
    ], className='banner'),

    html.Div([
        html.Div([
            html.H3("Price(USD) " + str(dt.datetime.now().date()))
        ], className='Title'),


        html.Div([
            dcc.Graph(id='bpi'),
        ], className='twelve columns bpi'),
        dcc.Interval(id='bpi-update', interval=12000)
    ], className='row bpi-row'),

    html.Div([
        html.P("Period"),
        dcc.Dropdown(id='period', options=[
                     {'label': i, 'value': i} for i in ['5', '10', '15']], value='10')
    ], style={'width': '31%', 'display': 'inline-block'}),

    html.Div([
        html.P("Box plot Period"),
        dcc.Dropdown(id='box_plot_period', options=[
                     {'label': i, 'value': i} for i in ['5', '10', '15']], value='10')
    ], style={'width': '31%', 'margin-left': '3%', 'display': 'inline-block'}),

    html.Div([
        html.P("Time frame"),
        dcc.Dropdown(id='timeframe', options=[
                     {'label': i, 'value': i} for i in ['1', '2', '3', '4']], value='2')
    ], style={'width': '31%', 'float': 'right', 'display': 'inline-block'})


], className='main-div')


@app.callback(
    Output(component_id='bpi', component_property='figure'),
    [
        Input(component_id='period', component_property='value'),
        Input(component_id='box_plot_period', component_property='value'),
        Input(component_id='timeframe', component_property='value')

    ],
    [],
    [Event('bpi-update', 'interval')]

)
def get_bpi(N, bN, T):

    #T hour time frame

    T = int(T)
    curr_time = time.time()
    begin_time = curr_time - T * 60 * 60

    db = TinyDB('bpi.db')
    BPI = Query()
    data = db.search(BPI.updatedTime > begin_time)

    prices = []
    EMA = []
    SMA = []
    dtime = []
    names = []

    N = int(N)  # period
    bN = int(bN)  # box-plot period

    #get time difference
    for bpi in data:

        prices.append(bpi["currentPrice"])
        a = dt.datetime.fromtimestamp(int(bpi["updatedTime"]))

        dtime.append(str(a.hour) + ":" + str(a.minute))

    plen = len(prices)

    #build data for boxplots
    boxtraces = []

    for i in xrange(0, plen, bN):

        y = prices[i:i + bN]
        ind = i + bN - 1

        if (i + bN) > len(dtime):

            ind = len(dtime) - 1

        name = dtime[ind]
        names.append(name)

        trace = Box(y=y, name=name, showlegend=False,
                    x=[i for j in range(len(y))])
        boxtraces.append(trace)

    #build data for EMA

    if plen > N:

        EMA = [None for i in range(N - 1)]

        y = prices[0: i + N]
        avg = reduce(lambda x, y_: x + y_, y) / len(y)
        EMA.append(avg)

        for i in xrange(N, plen, 1):

            new_ema = ((prices[i] - EMA[-1])
                       * 2.0 / 11.0) + EMA[-1]

            EMA.append(new_ema)

    #build data for SMA
    if plen > N:

        SMA = [None for i in range(N - 1)]

        for i in xrange(0, plen - N - 1, 1):

            y = prices[i: i + N]
            sma = reduce(lambda x, y__: x + y__, y) / len(y)
            SMA.append(sma)

    trace = Scatter(
        y=SMA,
        x=[i for i in xrange(0, plen, 1)],
        line=Line(
            color='#42C4F7'
        ),
        mode='lines',
        name='SMA'
    )

    trace2 = Scatter(
        y=EMA,
        x=[i for i in xrange(0, plen, 1)],
        line=Line(
            color='#32DD32'
        ),
        mode='lines',
        name=str(N) + '-period-EMA'
    )

    layout = Layout(
        xaxis=dict(
            tickmode="array",
            ticktext=names,
            tickvals=[i for i in xrange(0, plen, bN)],
            showticklabels=True
        ),
        height=450,
        margin=Margin(
            t=45,
            l=50,
            r=50))

    traces = []

    traces.append(trace)
    traces.append(trace2)
    boxtraces.extend(traces)

    return Figure(data=boxtraces, layout=layout)


external_css = ["https://cdnjs.cloudflare.com/ajax/libs/skeleton/2.0.4/skeleton.min.css",
                "https://fonts.googleapis.com/css?family=Raleway:400,400i,700,700i",
                "https://fonts.googleapis.com/css?family=Product+Sans:400,400i,700,700i"]


for css in external_css:
    app.css.append_css({"external_url": css})

css_directory = os.getcwd()
stylesheets = ['BitcoinMAvgs.css']
static_css_route = '/static/'


@app.server.route('{}<stylesheet>'.format(static_css_route))
def serve_stylesheet(stylesheet):
    if stylesheet not in stylesheets:
        raise Exception(
            '"{}" is excluded from the allowed static files'.format(
                stylesheet
            )
        )
    return send_from_directory(css_directory, stylesheet)


for stylesheet in stylesheets:
    app.css.append_css({"external_url": "/static/{}".format(stylesheet)})

if __name__ == '__main__':
    app.run_server()

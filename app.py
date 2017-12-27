from tinydb import TinyDB, Query
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State, Event
import plotly.plotly as py
from plotly.graph_objs import *
from scipy.stats import rayleigh
from flask import Flask, send_from_directory
import numpy as np
import os
import datetime as dt
import time

server = Flask('EWMABitcoin')

app = dash.Dash('EWMABitcoin-App', server=server,
                url_base_pathname='/dash/',
                csrf_protect=False)


app.layout = html.Div([
    html.Div([
        html.H2("Bitcoin prices with exponential moving average"),
    ], className='banner'),
    html.Div([
        html.Div([
            html.H3("Price(USD)")
        ], className='Title'),
        html.Div([
            dcc.Graph(id='bpi'),
        ], className='twelve columns bpi'),
        dcc.Interval(id='bpi-update', interval=12000),
    ], className='row bpi-row')], style={'padding': '0px 10px 15px 10px',
          'marginLeft': 'auto', 'marginRight': 'auto', "width": "900px",
          'boxShadow': '0px 0px 5px 5px rgba(204,204,204,0.4)'})

@app.callback(Output('bpi', 'figure'), [],[],[Event('bpi-update', 'interval')])
def get_bpi():

    #1 hour time frame

    begin_time = time.time() - 1 * 60 * 60

    db = TinyDB('bpi.db')
    BPI = Query()
    data = db.search(BPI.updatedTime > begin_time)
    prices = []
    EMA = []

    EMA.append(None)
    for bpi in data:

        prices.append(bpi["currentPrice"])
        
        if(len(prices) > 1):

            a = (prices[-1] - prices[-2] ) * (2.0/float(len(data) + 1))

            EMA.append(float(a) + float(prices[-2]))

    trace = Scatter(
    y=prices,
    line=Line(
        color='#42C4F7'
    ),
    mode='lines')

    trace2 = Scatter(
    y=EMA,
    line=Line(
        color='#42C4G7'
    ),
    mode='lines')

    layout = Layout(
        height=450,
        margin=Margin(
            t=45,
            l=50,
            r=50))
    
    return Figure(data=[trace, trace2], layout=layout)


external_css = ["https://cdnjs.cloudflare.com/ajax/libs/skeleton/2.0.4/skeleton.min.css",
                "https://fonts.googleapis.com/css?family=Raleway:400,400i,700,700i",
                "https://fonts.googleapis.com/css?family=Product+Sans:400,400i,700,700i"]


for css in external_css:
    app.css.append_css({"external_url": css})

css_directory = os.getcwd()
stylesheets = ['stylesheet.css']
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

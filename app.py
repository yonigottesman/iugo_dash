import datetime

import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly
from dash.dependencies import Input, Output
from flask import Flask,request
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate



# pip install pyorbital
from pyorbital.orbital import Orbital
satellite = Orbital('TERRA')

app = dash.Dash(__name__)
server = app.server # the Flask app
server.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
server.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(server)
migrate = Migrate(server, db)

class Feed(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128))
    coverage = db.Column(db.Float())


@server.route('/update', methods=['GET', 'POST'])
def update():
    content = request.get_json(silent=False)
    secondary_feeds = content['secondary_feeds']
    for feed_map in secondary_feeds:
        feed = Feed.query.filter(Feed.name==feed_map['name'])
        if feed.count() == 0:
            feed = Feed(name=feed_map['name'],coverage=feed_map['coverage'])
        else:
            feed = feed[0]
            feed.coverage = feed_map['coverage']
        db.session.add(feed)
    db.session.commit()
    return 'Hello, World!'
    

app.layout = html.Div(children=[
    html.H1(children='Iugo Dashboard'),

    html.Div(children='''
        Feed coverage
    '''),

    dcc.Graph(
        id='coverage-graph'
    ),
     dcc.Interval(
            id='interval-component',
            interval=1*1000, # in milliseconds
            n_intervals=0
        )
])

@app.callback(Output('coverage-graph', 'figure'),
              [Input('interval-component', 'n_intervals')])
def update_graph_live(n):


    secondary_feeds = Feed.query.all()
    x = []
    y = []
    for feed in secondary_feeds:
        x.append(feed.name)
        y.append(feed.coverage)
    
    figure={
        'data': [
            {'x': x, 'y': y, 'type': 'bar', 'name': 'SF'},
        ],
        'layout': {
            'title': 'Coverage'
        }
    }

    return figure



if __name__ == '__main__':
    app.run_server(debug=True)

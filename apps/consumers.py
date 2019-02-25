# -*- coding: utf-8 -*-
import math
import json
from datetime import date
import dateutil.parser
import common_db_calls_saved
import pandas as pd
import flask
import dash
from dash.dependencies import Input, Output, State
import dash_core_components as dcc
import dash_html_components as html
import plotly.plotly as py
from plotly import graph_objs as go
import db_interface 
import pytz
from datetime import timedelta, datetime
from app import app, indicator, indicator_with_value
import pandas as pd
import pandas.io.sql as psql
import plotly.graph_objs as go
from collections import defaultdict
from collections import Counter
from itertools import combinations



def get_number_of_customers_data(df):
    df1 = df.groupby(['orderdate'])['consumerid'].nunique().reset_index()
    df2 = df.groupby(['orderdate'])['orderid'].nunique().reset_index()

    merged_df = df1.join(df2.set_index('orderdate'), on='orderdate', how="outer")


    X = merged_df['orderdate'].values
    Y1 = merged_df['orderid'].values
    Y2 = merged_df['consumerid'].values



    trace1 = go.Bar(
        x=X,
        y=Y1,
        name='Number of Orders'
    )

    trace2 = go.Bar(
        x=X,
        y=Y2,
        name='Number of Consumers'
    )

    data = [trace1, trace2]

    return data



def get_number_of_customers_layout():
    
    layout = go.Layout(
        title='Number of Customers by Date',
        barmode='stack'
    )

    return layout


def is_weekday(dt):
    if dt.weekday() < 5:
        return 1
    return 0


def get_consumer_distribution_layout():
    layout = go.Layout(
        title='Customers by time of day',
        barmode='stack'
    )

    return layout


def get_consumer_distribution_data(df):
    df['hour_of_day'] = df.apply(lambda row : row['ordertime'].hour, axis=1)
    df['is_weekday'] = df.apply(lambda row : is_weekday(row['orderdate']), axis=1)
    
    df_weekend = df[df['is_weekday'] == 0]
    df_weekday = df[df['is_weekday'] == 1]

    df_weekend = df_weekend.groupby(['hour_of_day'])['consumerid'].nunique().reset_index()
    df_weekday = df_weekday.groupby(['hour_of_day'])['consumerid'].nunique().reset_index()
 
    merged_df = df_weekend.join(df_weekday.set_index('hour_of_day'), on='hour_of_day', how="outer", lsuffix='_weekend', rsuffix='_weekday')


    X = merged_df['hour_of_day'].values
    Y1 = merged_df['consumerid_weekend'].values
    Y2 = merged_df['consumerid_weekday'].values



    trace1 = go.Scatter(
        x = X,
        y = Y1,
        mode = 'lines+markers',
        name = 'weekend'
    )

    trace2 = go.Scatter(
        x = X,
        y = Y2,
        mode = 'lines+markers',
        name = 'weekday'
    )
    data = [trace1, trace2]

    return data


def get_consumer_spend_distribution_layout():

    layout = go.Layout(
        title='How much Consumers Spend'
    )

    return layout


def get_consumer_spend_distribution_data(df_attr):

    X = df_attr['moneyspent'].values
    mi = min(X)
    ma = max(X)
    trace = go.Histogram(x=X,
        name='Consumer Spend vs Count',
        xbins=dict(
        start=mi-500.0,
        end=ma+500,
        size=100
        ),
    )

    data = [trace]

    return data






def get_list_of_stores():
    list_of_stores = db_interface.get_list_of_stores()
    #indices_of_stores = list(map(lambda x: 'store{}'.format(x), range(1, len(list_of_stores)+1)))
    return list(map(lambda x: {"label": x[0], "value": x[0]}, list_of_stores))


list_of_stores = get_list_of_stores()

layout = [

        html.Div(id="chain_consumer_content", className="row", style={"margin": "2% 3%"}),

        html.Div(
        [
            html.Div(
                dcc.Dropdown(
                    id="store_name",
                    options=list_of_stores,
                    value=list_of_stores[0]['value'],
                    clearable=False,
                ),
                className="two columns",
            ),
        ],

        className="row",
        style={"marginBottom": "10"},
        ),

        html.Div(id="store_specific_consumer_content", className="row", style={"margin": "2% 3%"}),

        html.Div(
        [
            html.H1('Recommendations')
        ],),

        html.Div(id="store_specific_consumer_recommendations", className="row", style={"margin": "2% 3%"}),


    ]


@app.callback(Output("store_specific_consumer_recommendations", "children"), [Input("store_name", "value")])
def employee_recommendations_content(store_name):
    
    if store_name == 'Ulsoor Road':
        layout = [
            html.Div(
                html.H5('In Ulsoor Road store, same day repeating customers are very few, try incentivsing multiple visits a day.')
            ),
            html.Div(

                html.H5('In Ulsoor Road store, customers generally visit before and after office hours.'),
            ),
        ]
    elif store_name == 'IndiraNagar':
        layout = [
            html.Div(
                html.H5('In IndiraNagar store, sales were extremely low from 11 to 16 February. Kindly Investigate.')
            ),
            html.Div(

                html.H5('In IndiraNagar store, there\'s a very high demand at lunch hour'),
            ),
        ]
    elif store_name == 'Airport':
        layout = [
            html.Div(
                html.H5('In Airport store, lot of variation in sales between 6th and 7th February. Kindly investigate.')
            ),
            html.Div(

                html.H5('In Airport store, people prefer early morning and evening timing'),
            ),
        ]



    return layout




@app.callback(Output("chain_consumer_content", "children"), [Input("store_name", "value")])
def render_chain_content(store_name):


    query = "SELECT orderid, consumerid, storeid, dishid, price, discount, coupon, orderdate, ordertime FROM order_details;"
    df = psql.read_sql(query, db_interface.conn)

    query_attr = "SELECT consumerid, lastvisit, numberofvisits, moneyspent, discountsaved, companyid FROM consumer_attributes;"
    df_attr = psql.read_sql(query_attr, db_interface.conn)


    layout = [

        html.Div(
        [                

            html.Div(
            [                
                dcc.Graph(
                    id="chain_consumer_count",
                    figure=go.Figure(data = get_number_of_customers_data(df), 
                    layout = get_number_of_customers_layout()),

                    config=dict(displayModeBar=False),
                    style={"height": "89%", "width": "98%"},
                ),
            ],
            className="six columns chart_div"
        ),


            html.Div(
            [                
                dcc.Graph(
                    id="chain_consumer_time_distribution",
                    figure=go.Figure(data = get_consumer_distribution_data(df), 
                    layout = get_consumer_distribution_layout()),

                    config=dict(displayModeBar=False),
                    style={"height": "89%", "width": "98%"},
                ),
            ],
            className="six columns chart_div"
        ),

        ]),


            html.Div(
            [                
                dcc.Graph(
                    id="chain_consumer_spend_distribution",
                    figure=go.Figure(data = get_consumer_spend_distribution_data(df_attr), 
                    layout = get_consumer_spend_distribution_layout()),

                    config=dict(displayModeBar=False),
                    style={"height": "89%", "width": "98%"},
                ),
            ],
            className="six columns chart_div"
        ),

    
    ]

    return layout


@app.callback(Output("store_specific_consumer_content", "children"), [Input("store_name", "value")])
def render_store_content(store_name):

    store_id = common_db_calls_saved.store_name_to_id[store_name]
    store_id = "'{}'".format(store_id)

    query = "SELECT orderid, consumerid, storeid, dishid, price, discount, coupon, orderdate, ordertime FROM order_details WHERE storeId={};".format(store_id)
    df = psql.read_sql(query, db_interface.conn)

    layout = [        


        html.Div(
        [                

            html.Div(
            [                
                dcc.Graph(
                    id="store_consumer_count",
                    figure=go.Figure(data = get_number_of_customers_data(df), 
                    layout = get_number_of_customers_layout()),

                    config=dict(displayModeBar=False),
                    style={"height": "89%", "width": "98%"},
                ),
            ],
            className="six columns chart_div"
        ),

            html.Div(
            [                
                dcc.Graph(
                    id="store_consumer_distribution",
                    figure=go.Figure(data = get_consumer_distribution_data(df), 
                    layout = get_consumer_distribution_layout()),

                    config=dict(displayModeBar=False),
                    style={"height": "89%", "width": "98%"},
                ),
            ],
            className="six columns chart_div"
        ),

        ]),

    ]

    return layout

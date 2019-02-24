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
from common_db_calls_saved import dish_id_to_name, store_name_to_id


def map_id_to_name(ids):
    return list(map(lambda x: dish_id_to_name[x], ids))

def get_dish_combinations_layout():
    layout = go.Layout(
        title='Favorutie Combinations')

    return layout



def get_most_discounted_dish(df):

    df1 = df.groupby(['dishid'])['price'].sum().reset_index()
    df2 = df.groupby(['dishid'])['discount'].sum().reset_index()
    Y1 = df1['price'].values
    Y2 = df2['discount'].values

    return dish_id_to_name[X[np.argmax(list(map(lambda x: x[1]/x[0], zip(Y1, Y2))))]]


def get_best_combination(df):
    df['dish_list'] = df.apply(lambda row: [row['dishid']], axis=1)
    df1 = df.groupby(['orderid'])['dish_list'].sum().reset_index()
    df1['dishes_list'] = df1.apply(lambda row: [row['dish_list']], axis=1)
    dishes_list = df1['dishes_list'].sum()
  

    dish_pairs = defaultdict(int)

    for dishes in dishes_list:
        dishes = sorted(dishes)    

        for dish_pair in combinations(dishes, 2):
            dish_pairs[tuple(dish_pair)] += 1
    
    X = []
    Y = []

    for pair in dish_pairs.keys():
        X.append('{}+{}'.format(dish_id_to_name[pair[0]], dish_id_to_name[pair[1]]))
        Y.append(dish_pairs[pair])

    sortx = [x for _,x in sorted(zip(Y,X))]
    sorty = sorted(Y)

    sortx = sortx[:15]
    sorty = sorty[:15]
    
    best_combination = sortx[0].split('+')  

    return best_combination

def get_dish_combinations_data(df):
    global best_combination
    df['dish_list'] = df.apply(lambda row: [row['dishid']], axis=1)
    df1 = df.groupby(['orderid'])['dish_list'].sum().reset_index()
    df1['dishes_list'] = df1.apply(lambda row: [row['dish_list']], axis=1)
    dishes_list = df1['dishes_list'].sum()
  

    dish_pairs = defaultdict(int)

    for dishes in dishes_list:
        dishes = sorted(dishes)    

        for dish_pair in combinations(dishes, 2):
            dish_pairs[tuple(dish_pair)] += 1
    
    X = []
    Y = []

    for pair in dish_pairs.keys():
        X.append('{}+{}'.format(dish_id_to_name[pair[0]], dish_id_to_name[pair[1]]))
        Y.append(dish_pairs[pair])

    sortx = [x for _,x in sorted(zip(Y,X))]
    sorty = sorted(Y)

    sortx = sortx[:15]
    sorty = sorty[:15]
    
    best_combination = sortx[0].split('+')  
  
    trace = go.Bar(
        x=sorty,
        y=sortx,
        name='Combinations',
        orientation = 'h'
    )

    return [trace]


def get_dishes_revenue_layout():

    layout = go.Layout(
        title='Revenue of Dishes',
        barmode='stack'
    )

    return layout


def get_dishes_revenue_data(df):

    df1 = df.groupby(['dishid'])['price'].sum().reset_index()
    df2 = df.groupby(['dishid'])['discount'].sum().reset_index()
    Y1 = df1['price'].values
    Y2 = df2['discount'].values
    X = map_id_to_name(df1['dishid'].values)


    sortx = [x for _,x in sorted(zip(Y1,X))]
    sorty1 = sorted(Y1)
    sorty2 = [x for _,x in sorted(zip(Y1,Y2))]

    trace1 = go.Bar(
        x=sorty1,
        y=sortx,
        name='Price',
        orientation = 'h'
    )
    trace2 = go.Bar(
        x=sorty2,
        y=sortx,
        name='Discount',
        orientation = 'h'
    )

    data = [trace1, trace2]

    return data



def get_dishes_count_layout():

    layout = go.Layout(
        title='Count of Dishes',
        barmode='stack'
    )

    return layout


def get_dishes_count_data(df):

    df1 = df.groupby(['dishid']).size().reset_index(name='counts')
    Y = df1['counts'].values
    X = map_id_to_name(df1['dishid'].values)

    trace1 = go.Bar(
        x=X,
        y=Y,
        name='Counts')

    data = [trace1]

    return data



def get_list_of_stores():
    list_of_stores = db_interface.get_list_of_stores()
    #indices_of_stores = list(map(lambda x: 'store{}'.format(x), range(1, len(list_of_stores)+1)))
    return list(map(lambda x: {"label": x[0], "value": x[0]}, list_of_stores))


list_of_stores = get_list_of_stores()

layout = [

        html.Div(id="chain_content", className="row", style={"margin": "2% 3%"}),

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

        html.Div(id="store_specific_content", className="row", style={"margin": "2% 3%"}),

        html.Div(
        [
            html.H1('Recommendations')
        ],),

        html.Div(id="store_specific_recommendations", className="row", style={"margin": "2% 3%"}),


    ]


@app.callback(Output("store_specific_recommendations", "children"), [Input("store_name", "value")])
def store_specific_recommendations_content(store_name):
    
    store_id = common_db_calls_saved.store_name_to_id[store_name]
    store_id = "'{}'".format(store_id)

    query = "SELECT orderid, consumerid, storeid, dishid, price, discount, coupon, orderdate, ordertime FROM order_details WHERE storeId={};".format(store_id)
    df = psql.read_sql(query, db_interface.conn)
    best_combination = get_best_combination(df)


    layout = [
        html.Div(
            html.H5('In {} store, Best Dish Combination is {} plus {}. You may want to use this dish in Upsell Algorithm.'.format(store_name, best_combination[0], best_combination[1]))
        ),
        html.Div(

            html.H5('In {} store, {} has too much discount. You may want to reduce the discount on this dish.'.format(store_name, best_combination[0], best_combination[1])),
        ),
        html.Div(

            html.H5('In {} store, {} is trending. You may want improve the position of this dish in menu.'.format(store_name, common_db_calls_saved.store_to_dish[common_db_calls_saved.store_name_to_id[store_name]])),
        )
    ]

    return layout


@app.callback(Output("chain_content", "children"), [Input("store_name", "value")])
def render_chain_content(store_name):


    query = "SELECT orderid, consumerid, storeid, dishid, price, discount, coupon, orderdate, ordertime FROM order_details;"
    df = psql.read_sql(query, db_interface.conn)

    layout = [

        html.Div([

        html.Div(
            [                
                dcc.Graph(
                    id="chain_dishes_revenue",
                    figure=go.Figure(data = get_dishes_revenue_data(df), 
                    layout = get_dishes_revenue_layout()),

                    config=dict(displayModeBar=False),
                    style={"height": "89%", "width": "98%"},
                ),
            ],
            className="six columns chart_div"
        ),

        html.Div(
            [                
                dcc.Graph(
                    id="chain_dishes_count",
                    figure=go.Figure(data = get_dishes_count_data(df), 
                    layout = get_dishes_count_layout()),

                    config=dict(displayModeBar=False),
                    style={"height": "89%", "width": "98%"},
                ),
            ],
            className="six columns chart_div"
        )
    ]),

        html.Div(
        [                
            dcc.Graph(
                id="dishes_pairs",
                figure=go.Figure(data = get_dish_combinations_data(df), 
                layout = get_dish_combinations_layout()),

                config=dict(displayModeBar=False),
                style={"height": "89%", "width": "98%"},
            ),
        ],
        className="six columns chart_div"
        )

    ]
        
    return layout


@app.callback(Output("store_specific_content", "children"), [Input("store_name", "value")])
def render_store_content(store_name):

    store_id = common_db_calls_saved.store_name_to_id[store_name]
    store_id = "'{}'".format(store_id)

    query = "SELECT orderid, consumerid, storeid, dishid, price, discount, coupon, orderdate, ordertime FROM order_details WHERE storeId={};".format(store_id)
    df = psql.read_sql(query, db_interface.conn)

    layout = [


        html.Div([

        html.Div(
            [                
                dcc.Graph(
                    id="store_dishes_revenue",
                    figure=go.Figure(data = get_dishes_revenue_data(df), 
                    layout = get_dishes_revenue_layout()),

                    config=dict(displayModeBar=False),
                    style={"height": "89%", "width": "98%"},
                ),
            ],
            className="six columns chart_div"
        ),

        html.Div(
            [                
                dcc.Graph(
                    id="store_dishes_count",
                    figure=go.Figure(data = get_dishes_count_data(df), 
                    layout = get_dishes_count_layout()),

                    config=dict(displayModeBar=False),
                    style={"height": "89%", "width": "98%"},
                ),
            ],
            className="six columns chart_div"
        )
    ]),


    html.Div(
        [                
            dcc.Graph(
                id="store_dishes_pairs",
                figure=go.Figure(data = get_dish_combinations_data(df), 
                layout = get_dish_combinations_layout()),

                config=dict(displayModeBar=False),
                style={"height": "89%", "width": "98%"},
            ),
        ],
        className="six columns chart_div"
    )

    ]
        
    return layout

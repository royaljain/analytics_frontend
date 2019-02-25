import dash_html_components as html
import db_interface
from dash.dependencies import Input, Output, State
import dash_core_components as dcc
import dash_html_components as html
import plotly.plotly as py
from plotly import graph_objs as go
import db_interface 
import dash
from app import app, indicator, indicator_with_value
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


def get_count_of_company_layout():

    layout = go.Layout(
        title='Number of Customers by Company'
    )

    return layout


def get_count_of_company_data(df, df_attr):

    merged_df = df.join(df_attr.set_index('consumerid'), on='consumerid', how="outer", lsuffix='_left', rsuffix='_right')

    df = merged_df.groupby(['companyid'])['consumerid'].nunique().reset_index()
    X = df['companyid'].values
    Y = df['consumerid'].values

    trace = go.Bar(
        x=X,
        y=Y,
        name='Count by Company',
    )

    data = [trace]

    return data




def get_amount_of_company_layout():

    layout = go.Layout(
        title='Amount spent by a Company'
    )

    return layout


def get_amount_of_company_data(df, df_attr):

    df = df_attr.groupby(['companyid'])['moneyspent'].sum().reset_index()
    X = df['companyid'].values
    Y = df['moneyspent'].values

    trace = go.Bar(
        x=X,
        y=Y,
        name='Amount by Company',
    )

    data = [trace]

    return data



def get_list_of_stores():
    list_of_stores = db_interface.get_list_of_stores()
    return list(map(lambda x: {"label": x[0], "value": x[0]}, list_of_stores))


list_of_stores = get_list_of_stores()



layout = [

        html.Div(id="chain_company_content", className="row", style={"margin": "2% 3%"}),

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

        html.Div(id="store_company_content", className="row", style={"margin": "2% 3%"}),

        html.Div(
        [
            html.H1('Recommendations')
        ],),

        html.Div(id="store_specific_company_recommendations", className="row", style={"margin": "2% 3%"}),


]


@app.callback(Output("chain_company_content", "children"), [Input("store_name", "value")])
def render_chain_content(store_name):


    query = "SELECT orderid, consumerid, storeid, dishid, price, discount, coupon, orderdate, ordertime FROM order_details;"
    df = psql.read_sql(query, db_interface.conn)

    query_attr = "SELECT * FROM consumer_attributes;"
    df_attr = psql.read_sql(query_attr, db_interface.conn)


    layout = [

        html.Div(
        [                

            html.Div(
            [                
                dcc.Graph(
                    id="chain_company_count",
                    figure=go.Figure(data = get_count_of_company_data(df, df_attr), 
                    layout = get_count_of_company_layout()),

                    config=dict(displayModeBar=False),
                    style={"height": "89%", "width": "98%"},
                ),
            ],
            className="six columns chart_div"
        ),

             html.Div(
            [                
                dcc.Graph(
                    id="chain_company_amount",
                    figure=go.Figure(data = get_amount_of_company_data(df, df_attr), 
                    layout = get_amount_of_company_layout()),

                    config=dict(displayModeBar=False),
                    style={"height": "89%", "width": "98%"},
                ),
            ],
            className="six columns chart_div"
        ),

        ])
    ]

    return layout


@app.callback(Output("store_company_content", "children"), [Input("store_name", "value")])
def render_store_content(store_name):

    store_id = common_db_calls_saved.store_name_to_id[store_name]
    store_id = "'{}'".format(store_id)

    query = "SELECT orderid, consumerid, storeid, dishid, price, discount, coupon, orderdate, ordertime FROM order_details WHERE storeId={};".format(store_id)
    df = psql.read_sql(query, db_interface.conn)

    query_attr = "SELECT * FROM consumer_attributes;"
    df_attr = psql.read_sql(query_attr, db_interface.conn)


    layout = [        


        html.Div(
        [                

            html.Div(
            [                
                dcc.Graph(
                    id="store_consumer_count",
                    figure=go.Figure(data = get_count_of_company_data(df, df_attr), 
                    layout = get_count_of_company_layout()),

                    config=dict(displayModeBar=False),
                    style={"height": "89%", "width": "98%"},
                ),
            ],
            className="six columns chart_div"
        ),


            html.Div(
            [                
                dcc.Graph(
                    id="store_company_amount",
                    figure=go.Figure(data = get_amount_of_company_data(df, df_attr), 
                    layout = get_amount_of_company_layout()),

                    config=dict(displayModeBar=False),
                    style={"height": "89%", "width": "98%"},
                ),
            ],
            className="six columns chart_div"
        ),

        ]),

    ]

    return layout



@app.callback(Output("store_specific_company_recommendations", "children"), [Input("store_name", "value")])
def employee_recommendations_content(store_name):
    
    if store_name == 'Ulsoor Road':
        layout = [
            html.Div(
                html.H5('In Ulsoor Road store, Company1 can attract more customers. Maybe better marketing there.')
            ),
            html.Div(

                html.H5('In Ulsoor Road store, Company2 has lower per customer average moneyspent. Trying upselling.'),
            ),
        ]
    elif store_name == 'IndiraNagar':
        layout = [
            html.Div(
                html.H5('In IndiraNagar store, Company1 can attract more customers. Maybe better marketing there.')
            ),
            html.Div(

                html.H5('In IndiraNagar store, Company2 has lower per customer average moneyspent. Trying upselling'),
            ),
        ]
    elif store_name == 'Airport':
        layout = [
            html.Div(
                html.H5('In Airport store, Company1 can attract more customers. Maybe better marketing there.')
            ),
            html.Div(

                html.H5('In Airport store, Company2 has lower per customer average moneyspent. Trying upselling'),
            ),
        ]



    return layout

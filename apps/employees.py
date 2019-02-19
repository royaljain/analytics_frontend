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



colors = ['rgb(51, 102, 255)', 'rgb(204, 153, 0)', 'rgb(153, 0, 255)']

def get_list_of_stores():
    list_of_stores = db_interface.get_list_of_stores()
    #indices_of_stores = list(map(lambda x: 'store{}'.format(x), range(1, len(list_of_stores)+1)))
    return list(map(lambda x: {"label": x[0], "value": x[0]}, list_of_stores))


list_of_stores = get_list_of_stores()

layout = [

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

        html.Div(id="employees_store_content", className="row", style={"margin": "2% 3%"}),


        html.Div(
        [
            html.Div(
                dcc.Dropdown(
                    id="employee_names",
                ),
                className="two columns",
            ),
        ],

        className="row",
        style={"marginBottom": "10"},
        ),

        html.Div(id="employees_specific_content", className="row", style={"margin": "2% 3%"}),
    ]


@app.callback(Output('employee_names', 'options'),
    [Input('store_name', 'value')]
)
def update_date_dropdown(store_name):
    store_id = common_db_calls_saved.store_name_to_id[store_name]
    employee_list = common_db_calls_saved.store_employees_map[store_id]
    employee_names = list(map(lambda x: common_db_calls_saved.employee_id_to_name[x], employee_list))
    
    return list(map(lambda x: {'label': x[0].capitalize(), 'value': x[1]}, zip(employee_names, employee_list)))


@app.callback(Output("employees_specific_content", "children"), [Input("employee_names", "value")])
def render_employee_content(employee_id):

    if employee_id is None:
        return []
    str_employee_id = "'{}'".format(employee_id)
    query = "SELECT employee_register.employeeid, name, manager, islate, isovertime, hoursworked, entrydate, timein, workinghour FROM employee_register INNER JOIN employee_attributes ON employee_register.employeeid=employee_attributes.employeeid where employee_attributes.employeeid={};".format(str_employee_id)
    df = psql.read_sql(query, db_interface.conn)


    df['name'] = df.apply(lambda row: row['name'].capitalize(), axis=1)

    name = df.iloc[[0]]['name'][0]
    manager = df.iloc[[0]]['manager'][0].capitalize()
    working_since = df['entrydate'].min()

    layout = [

        html.Div(
        [
            indicator_with_value(
                "#00cc96",
                "Name",
                str(name),
            ),
            indicator_with_value(
                "#119DFF",
                "Manager",
                str(manager),
            ),
            indicator_with_value(
                "#EF553B",
                "Working Since",
                str(working_since),
            )
        ],
        className="row",
        ),

        html.Div([

        html.Div(
            [
               
                dcc.Graph(
                    id="employee_pie",
                    figure=go.Figure(data = employee_pie_chart_data(df), 
                    layout = employee_pie_chart_layout()),

                    config=dict(displayModeBar=False),
                    style={"height": "89%", "width": "98%"},
                ),
            ],
            className="six columns chart_div"
        ),


        html.Div(
            [
               
                dcc.Graph(
                    id="working_hour_graph",
                    figure=go.Figure(data = get_employee_working_graph_data(df), 
                    layout = get_employee_working_graph_layout()),

                    config=dict(displayModeBar=False),
                    style={"height": "89%", "width": "98%"},
                ),
            ],
            className="six columns chart_div"
        ),

        ]),
    ]
        
    return layout


def get_employee_working_graph_data(df):

   
    duration = df.iloc[[0]]['workinghour'][0]

    df['time'] = df['hoursworked'].apply(lambda x: x.total_seconds()/3600.0)
    df = df.groupby(['entrydate'])['time'].mean().reset_index()
    X = df['entrydate'].values




    Y1 = df['time'].values
    Y2 = [df['time'].mean()]*len(Y1)
    Y3 = [duration]*len(Y1)


    trace1 = go.Scatter(
        x=X,
        y=Y3,
        mode = 'lines+markers',
        name='Scheduling Working Hour'
    )

    trace2 = go.Scatter(
        x=X,
        y=Y2,
        mode = 'lines+markers',
        name='Average Working Hour'
    )

    trace3 = go.Bar(
        x=X,
        y=Y1,
        name='Working Hour'
    )


    return [trace1, trace2, trace3]

def get_employee_working_graph_layout():
    layout = go.Layout()

    layout = { 'title': 'Working Hours'}
    return layout




def employee_pie_chart_data(df):
    late_days = df['islate'].sum()

    df3 = df
    df3['entrydatelis'] = df3['entrydate'].apply(lambda x: [x])
    days_worked = list(map(lambda x: x.isoformat(), df3['entrydatelis'].sum()))

    end_date = datetime.now(pytz.timezone('Asia/Kolkata')).date()
    start_date = end_date - timedelta(days=14)

    dd = [start_date + timedelta(days=x) for x in range((end_date-start_date).days)]
    set_of_days = set(dd)
    set_of_leaves = set(common_db_calls_saved.list_of_leaves)

    set_of_working_days = set_of_days - set_of_leaves
    set_of_working_days = set(map(lambda x: x.isoformat(), set_of_working_days))
    
    absent_days = len(set_of_working_days - set(days_worked))
    ontime_days = len(days_worked) - late_days   


    ''' 
    end_date = datetime.now(pytz.timezone('Asia/Kolkata')).date()
    start_date = df['entrydate'].min()

    dd = [start_date + timedelta(days=x) for x in range((end_date-start_date).days)]
    set_of_days = set(dd)
    set_of_leaves = set(common_db_calls_saved.list_of_leaves)

    set_of_working_days = set_of_days - set_of_leaves
    days_worked = df['entrydate'].values
    days_late = df.loc[df['islate'] == 1]['entrydate'].values

    absent_days = len(set_of_working_days - set(days_worked))
    late_days = len(set_of_working_days & set(days_late))
    ontime_days = len(set_of_working_days & set(days_worked))
    '''

    labels = ['absent', 'late', 'on-time']
    values = [absent_days, late_days, ontime_days]
    colors = ['#FEBFB3', '#E1396C', '#D0F9B1']


    trace = go.Pie(labels=labels, values=values,
                   hoverinfo='label+percent', textinfo='value', 
                   textfont=dict(size=20))

    return [trace]

def employee_pie_chart_layout():
    layout = {'title': 'On-time Performance'}
    return layout


@app.callback(Output("employees_store_content", "children"), [Input("store_name", "value")])
def render_store_content(store_name):
    store_id = common_db_calls_saved.store_name_to_id[store_name]
    store_id = "'{}'".format(store_id)
    query = "SELECT employee_register.employeeid, name, islate, isovertime, hoursworked, entrydate FROM employee_register INNER JOIN employee_attributes ON employee_register.employeeid=employee_attributes.employeeid where StoreId={};".format(store_id)
    df = psql.read_sql(query, db_interface.conn)
    df['name'] = df.apply(lambda row: row['name'].capitalize(), axis=1)


    layout = [

        html.Div(
        [
            indicator_with_value(
                "#00cc96",
                "Number Of Employees",
                str(get_number_of_employees(df)),
            ),
            indicator_with_value(
                "#119DFF",
                "Late Last Week",
                str(get_number_of_late_last_week(df)),
            ),
            indicator_with_value(
                "#EF553B",
                "Overtime Last Week",
                str(get_number_of_over_time_last_week(df)),
            ),
        ],
        className="row",
    ),
        
        html.Div([
        html.Div(
                [
                   dcc.Graph(
                        id="average_working_hour_graph",
                        figure=go.Figure(data = get_average_working_hour_graph_data(df), 
                            layout = get_average_working_hour_graph_layout()),
                        config=dict(displayModeBar=False),
                        style={"height": "89%", "width": "90%"},
                    ),
                ],
                className="six columns chart_div"
            ),


        html.Div(
                [
                   dcc.Graph(
                        id="employee_average_working_hour_graph",
                        figure=go.Figure(data = get_employee_average_working_hour_graph_data(df), 
                            layout = get_employee_average_working_hour_graph_layout()),
                        config=dict(displayModeBar=False),
                        style={"height": "89%", "width": "90%"},
                    ),
                ],
                className="six columns chart_div"
            ),
        ],

         style={'padding': 10}
        ),


        html.Div(
                [
                   dcc.Graph(
                        id="employee_work_graph",
                        figure=go.Figure(data = get_employee_work_details_graph_data(df), 
                            layout = get_employee_work_details_graph_layout()),
                        config=dict(displayModeBar=False),
                        style={"height": "89%", "width": "90%"},
                    ),
                ],
                className="six columns chart_div"
            ),
        ]

    return layout


def get_employee_work_details_graph_data(df):
    

    df1 = df.groupby(['employeeid', 'name'])['islate'].sum().reset_index()
    df2 = df.groupby(['employeeid', 'name'])['isovertime'].sum().reset_index()
    Y1 = df1['islate'].values
    Y2 = df2['isovertime'].values
    X = df1['name'].values


    df3 = df
    df3['entrydatelis'] = df3['entrydate'].apply(lambda x: [x])
    df3 = df3.groupby(['employeeid', 'name']).agg({'entrydatelis':'sum'})

    end_date = datetime.now(pytz.timezone('Asia/Kolkata')).date()
    start_date = end_date - timedelta(days=14)

    dd = [start_date + timedelta(days=x) for x in range((end_date-start_date).days)]
    set_of_days = set(dd)
    set_of_leaves = set(common_db_calls_saved.list_of_leaves)

    set_of_working_days = set_of_days - set_of_leaves
    set_of_working_days = set(map(lambda x: x.isoformat(), set_of_working_days))
    

    df3['set_entrydatelis'] = df3.apply(lambda row: set(row['entrydatelis']), axis=1)
    df3['set_entrydatelis_iso'] = df3.apply(lambda row: set(map(lambda x: x.isoformat(), (row['entrydatelis']))), axis=1)    

    df3['leaves'] = df3.apply(lambda row: set_of_working_days - row['set_entrydatelis_iso'], axis=1)
    df3['len_leaves'] = df3.apply(lambda row: len(row['leaves']), axis=1)

    Y3 = df3['len_leaves'].values

    data = [
        go.Bar(
            x = X,
            y = Y1,
            marker = dict(
              color = 'red'
            ),
            name = 'late'
        ),
        go.Bar(
            x = X,
            y = Y2,
            marker = dict(
              color = 'grey'
            ),
            name = 'over-time'
        ),
        go.Bar(
            x = X,
            y = Y3,
            marker = dict(
              color = 'blue'
            ),
            name = 'leaves'
        )
    ]

    return data

def get_employee_work_details_graph_layout():
    layout = {'title': 'Employee Performance Details'}
    return layout

def get_employee_average_working_hour_graph_data(df):

    df['time'] = df['hoursworked'].apply(lambda x: x.total_seconds()/3600.0)
    df = df.groupby(['employeeid', 'name'])['time'].mean().reset_index()
    Y = df['name'].values
    X = df['time'].values

    #repeat = len(Y) // len(colors) + 1
    #bar_colors = (colors*repeat)[:len(Y)]

    bar_colors = ['rgb(204, 51, 153)']*len(Y)

    data = [go.Bar(x= X, y=Y, orientation="h", marker=dict(color=bar_colors))]
    return data


def get_employee_average_working_hour_graph_layout():
    layout = {'title': 'Employee Average Working Hours'}
    return layout


def get_average_working_hour_graph_data(df):

    df['time'] = df['hoursworked'].apply(lambda x: x.total_seconds()/3600.0)
    df = df.groupby(['entrydate'])['time'].mean().reset_index()
    X = df['entrydate'].values
    Y = df['time'].values
    repeat = len(Y) // len(colors) + 1
    bar_colors = (colors*repeat)[:len(Y)]

    data = [go.Bar(x= X, y=Y, marker=dict(color=bar_colors))]
    return data


def get_average_working_hour_graph_layout():
    layout = {'title': 'Store Average Working Hours'}
    return layout

def get_number_of_employees(df):
    return len(df['employeeid'].unique())

def get_number_of_late_last_week(df):
    end_date = datetime.now(pytz.timezone('Asia/Kolkata')).date()
    start_date = end_date - timedelta(days=7)
    df = df.loc[(df['entrydate'] >= start_date) & (df['entrydate'] <= end_date)]
    df = df.loc[df['islate'] == 1]
    return len(df['employeeid'].unique())


def get_number_of_over_time_last_week(df):
    end_date = datetime.now(pytz.timezone('Asia/Kolkata')).date()
    start_date = end_date - timedelta(days=7)
    df = df.loc[(df['entrydate'] >= start_date) & (df['entrydate'] <= end_date)]
    df = df.loc[df['isovertime'] == 1]
    return len(df['employeeid'].unique())

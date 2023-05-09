# Data visualization
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# Dash Framework
import dash_bootstrap_components as dbc
from dash import Dash, callback, clientside_callback, html, dcc, dash_table as dt, Input, Output, State, MATCH, ALL
from dash.exceptions import PreventUpdate
import dash_daq as daq

# import local modules
from config_settings import *

# ----------------------------------------------------------------------------
# DATA VISUALIZATION
# ----------------------------------------------------------------------------

def build_sankey(nodes_dataframe, data_dataframe):
    sankey_fig = go.Figure(data=[go.Sankey(
        # Define nodes
        node = dict(
          pad = 15,
          thickness = 20,
          line = dict(color = "black", width = .5),
          label =  nodes_dataframe['Node'],
           # color =  "red"
        ),
        # Add links
        link = dict(
          source =  data_dataframe['sourceID'],
          target =  data_dataframe['targetID'],
          value =  data_dataframe['value'],
          ),
        # orientation = 'v'
    )])
    return sankey_fig


# ----------------------------------------------------------------------------
# DATA FOR DASH UI COMPONENTS
# ----------------------------------------------------------------------------

# Data table of API data
def build_datatable(data_source, table_id):
    new_datatable =  dt.DataTable(
            id = table_id,
            data=data_source.to_dict('records'),
            columns=[{"name": i, "id": i} for i in data_source.columns],
            css=[{'selector': '.row', 'rule': 'margin: 0; flex-wrap: nowrap'},
                {'selector':'.export','rule':EXPORT_STYLE }
                # {'selector':'.export','rule':'position:absolute;right:25px;bottom:-35px;font-family:Arial, Helvetica, sans-serif,border-radius: .25re'}
                ],
            style_cell= {
                'text-align':'left',
                'padding': '5px'
                },
            style_as_list_view=True,
            style_header={
                'backgroundColor': 'grey',
                'fontWeight': 'bold',
                'color': 'white'
            },

            export_format="csv",
        )
    return new_datatable

def build_dash_content(chart, data_table): # build_sankey(nodes, sankey_df) build_datatable(redcap_df,'table_csv') redcap_df
    dash_content = [
        dbc.Row([
            dbc.Col([
                html.Div(chart, id='div_sankey'),
            ],width=12),
            dbc.Col([
                html.Div(data_table, id='div_table'),
            ], width=12)
        ])
    ]
    return dash_content
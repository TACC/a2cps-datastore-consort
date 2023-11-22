# File Management
import os # Operating system library
import flask
import pathlib # file paths

# Data Cleaning and transformations
import pandas as pd
import numpy as np
from datetime import datetime
import json

# Data visualization
import plotly.express as px
import plotly.graph_objects as go

from flask import Flask

# Dash Framework
import dash_bootstrap_components as dbc
from dash import Dash, callback, clientside_callback, html, dcc, dash_table as dt, Input, Output, State, MATCH, ALL
from dash.exceptions import PreventUpdate
import dash_daq as daq

from flask import request

# import local modules
from config_settings import *
from datastore_loading import *
from data_processing import *
from dash_components import *

# ----------------------------------------------------------------------------
# APP Settings
# ----------------------------------------------------------------------------

external_stylesheets_list = [dbc.themes.SANDSTONE, 'https://codepen.io/chriddyp/pen/bWLwgP.css'] #  set any external stylesheets

app = Dash(__name__,
                external_stylesheets=external_stylesheets_list,
                meta_tags=[{'name': 'viewport', 'content': 'width=device-width, initial-scale=1'}],
                assets_folder=ASSETS_PATH,
                requests_pathname_prefix=REQUESTS_PATHNAME_PREFIX,
                suppress_callback_exceptions=True
                )
gunicorn_logger = logging.getLogger('gunicorn.error')
app.logger = logging.getLogger("consort_ui")
app.logger.handlers = gunicorn_logger.handlers
app.logger.setLevel(logging.INFO)

# ----------------------------------------------------------------------------
# Sample JSON
# ----------------------------------------------------------------------------
latest_data = [{"source": "Screened Patients", "target": "Declined - Not interested in research", "value": 249, "mcc": "1"}, {"source": "Screened Patients", "target": "Declined - COVID-related", "value": 9, "mcc": "1"}, {"source": "Screened Patients", "target": "Declined - Compensation insufficient", "value": 2, "mcc": "1"}, {"source": "Screened Patients", "target": "Declined - Specific study procedure", "value": 226, "mcc": "1"}, {"source": "Screened Patients", "target": "Declined - Time related", "value": 762, "mcc": "1"}, {"source": "Screened Patients", "target": "Declined - No reason provided", "value": 662, "mcc": "1"}, {"source": "Screened Patients", "target": "Consented Patients", "value": 476, "mcc": "1"}, {"source": "Consented Patients", "target": "Withdrawl Prior to Surgery - Subject chose to discontinue the study", "value": 14, "mcc": "1"}, {"source": "Consented Patients", "target": "Withdrawl Prior to Surgery - Site PI chose to discontinue subject participation", "value": 25, "mcc": "1"}, {"source": "Consented Patients", "target": "Withdrawl Prior to Surgery - Subject is lost to follow-up, unable to locate", "value": 2, "mcc": "1"}, {"source": "Consented Patients", "target": "Patients Reaching Baseline", "value": 409, "mcc": "1"}, {"source": "Patients Reaching Baseline", "target": "Patients With Surgery", "value": 398, "mcc": "1"}, {"source": "Patients With Surgery", "target": "Early Terminations - Subject chose to discontinue the study", "value": 3, "mcc": "1"}, {"source": "Patients With Surgery", "target": "Early Terminations - Subject is lost to follow-up, unable to locate", "value": 2, "mcc": "1"}, {"source": "Patients With Surgery", "target": "Patients Reaching Week 6", "value": 377, "mcc": "1"}, {"source": "Patients Reaching Week 6", "target": "Early Terminations - Subject chose to discontinue the study", "value": 1, "mcc": "1"}, {"source": "Patients Reaching Week 6", "target": "Patients Reaching Month 3", "value": 328, "mcc": "1"}, {"source": "Reaching Month 3", "target": "Early Terminations - Subject is lost to follow-up, unable to locate", "value": 3, "mcc": "1"}, {"source": "Patients Reaching Month 3", "target": "Patients Reaching Month 6", "value": 247, "mcc": "1"}, {"source": "Screened Patients", "target": "Declined - Not interested in research", "value": 123, "mcc": "2"}, {"source": "Screened Patients", "target": "Declined - COVID-related", "value": 2, "mcc": "2"}, {"source": "Screened Patients", "target": "Declined - Compensation insufficient", "value": 6, "mcc": "2"}, {"source": "Screened Patients", "target": "Declined - Specific study procedure", "value": 112, "mcc": "2"}, {"source": "Screened Patients", "target": "Declined - Time related", "value": 176, "mcc": "2"}, {"source": "Screened Patients", "target": "Declined - No reason provided", "value": 128, "mcc": "2"}, {"source": "Screened Patients", "target": "Consented Patients", "value": 184, "mcc": "2"}, {"source": "Consented Patients", "target": "Withdrawl Prior to Surgery - Subject chose to discontinue the study", "value": 13, "mcc": "2"}, {"source": "Consented Patients", "target": "Withdrawl Prior to Surgery - Site PI chose to discontinue subject participation", "value": 4, "mcc": "2"}, {"source": "Consented Patients", "target": "Withdrawl Prior to Surgery - Subject is lost to follow-up, unable to locate", "value": 1, "mcc": "2"}, {"source": "Consented Patients", "target": "Withdrawl Prior to Surgery - Death", "value": 2, "mcc": "2"}, {"source": "Consented Patients", "target": "Patients Reaching Baseline", "value": 152, "mcc": "2"}, {"source": "Patients Reaching Baseline", "target": "Patients With Surgery", "value": 137, "mcc": "2"}, {"source": "Patients With Surgery", "target": "Early Terminations - Subject chose to discontinue the study", "value": 1, "mcc": "2"}, {"source": "Patients With Surgery", "target": "Early Terminations - Death", "value": 1, "mcc": "2"}, {"source": "Patients With Surgery", "target": "Patients Reaching Week 6", "value": 124, "mcc": "2"}, {"source": "Patients Reaching Week 6", "target": "Patients Reaching Month 3", "value": 96, "mcc": "2"}, {"source": "Reaching Month 3", "target": "Early Terminations - Subject chose to discontinue the study", "value": 3, "mcc": "2"}, {"source": "Reaching Month 3", "target": "Early Terminations - Site PI chose to discontinue subject participation", "value": 2, "mcc": "2"}, {"source": "Patients Reaching Month 3", "target": "Patients Reaching Month 6", "value": 56, "mcc": "2"}]


# ---------------------------------
#   Page components
# ---------------------------------

def serve_layout():
    # get data via in the internal docker network
    api_address = DATASTORE_URL +'consort'
    app.logger.info('Requesting data from api {0}'.format(api_address))
    api_json = get_api_data(api_address)
    
    if 'error' in api_json:
        app.logger.info('Error response from datastore: {0}'.format(api_json))
        if 'error_code' in api_json:
            error_code = api_json['error_code']
            if error_code in ('MISSING_SESSION_ID', 'INVALID_TAPIS_TOKEN'):
                app.logger.warn('Auth error from datastore, asking user to authenticate')
                return html.Div([html.H1('CONSORT REPORT'),
                                         html.H4('Please login and authenticate on the portal to access the report.')])
            else:
                report_title = html.Div([html.H1('CONSORT REPORT (sample data)'), 
                                 html.P('Current data unavailable')])


    # ignore cache and request again.
    if 'data' not in api_json[1] or 'consort' not in api_json[1]['data']:
        app.logger.info('Requesting data from api {0} to ignore cache.'.format(api_address))
        api_json = get_api_data(api_address, True)

    if api_json[0]==200:
        consort_data = api_json[1]['data']['consort']
        report_title = html.Div([html.H1('CONSORT REPORT')])
    else:
        app.logger.warn('api failed')
        consort_data = latest_data
        report_title = html.Div([html.H1('CONSORT REPORT (sample data)'), 
                                 html.P('Current data unavailable')])

    layout =  html.Div([
        html.Div([
            dcc.Loading(
                id="loading-1",
                type="default",
                children=html.Div([
                    dcc.Store(id='api_data', data=consort_data),
                    html.Div(id='div_store_data'),
                    html.Div(id='div_test'),
                    dbc.Row([
                        dbc.Col([
                            report_title
                        ],md = 8),
                        # dbc.Col([
                        #     dcc.Dropdown(
                        #         id='dropdown-date',
                        #         options=date_options,
                        #         value=date_options[0]['value'],
                        #     ),
                        # ],id='dd_date',md=2),
                        dbc.Col([
                            # TO DO: Convert this dropdown to use a list generated from the date selected in the dates dropdown.
                            dcc.Dropdown(
                                id='dropdown-mcc',
                                options=[
                                    {'label': 'MCC1', 'value': '1'},
                                    {'label': 'MCC2', 'value': '2'}
                                ],

                            ),
                        ],id='dd_mcc',md=2),
                    ]),
                    dbc.Row([
                        dbc.Col([
                            html.Div(id="report_msg"),
                        ],md = 9),
                        dbc.Col([

                        ],md = 3),
                    ]),
                    html.Div(id = 'dash_content'),
                ],id="loading-output-1")
            ),

        ], style =CONTENT_STYLE)
    ],style=TACC_IFRAME_SIZE)
    return layout

app.layout = serve_layout


# ----------------------------------------------------------------------------
# DATA CALLBACKS
# ----------------------------------------------------------------------------
# Load content of page
@app.callback(
    Output('dash_content','children'),
    Input('dropdown-mcc', 'value'),
    State('api_data', 'data'),)
def show_store_data(mcc, api_data):
    if not get_django_user():
        raise PreventUpdate
    
    df_json = api_data
    error_div = html.Div('There is no data available for this selection')
    
    print(mcc)
    if not mcc:
        return html.Div('Please select an mcc to view data')
    if not df_json:
        print('no df')
        return error_div
    else:
        df = pd.DataFrame.from_dict(df_json)
        df = df.astype({'mcc':'string'}) # Convert to string for easier fitlering since dropdown provides filter
    
        if len(df) == 0:
            return error_div
        else:
            chart_title = 'CONSORT Report from api data'

            selected_df = df[df['mcc']==mcc] 

            if len(selected_df) > 0:
                data_table = build_datatable(selected_df,'table_selected')
                nodes, sankey_df = get_sankey_dataframe(selected_df) # transform data into sankey data format
                sankey_fig = build_sankey(nodes, sankey_df) # turn sankey data into sankey figure
                sankey_fig.update_layout(title = chart_title)
                chart = dcc.Graph(id="sankey_chart",figure=sankey_fig) # create dash component chart from figure
                dash_content = build_dash_content(chart, data_table) # create page content from variables
                return dash_content  
            else:
                return error_div




# ----------------------------------------------------------------------------
# RUN APPLICATION
# ----------------------------------------------------------------------------

if __name__ == '__main__':
    app.run_server(debug=True)
else:
    server = app.server


from dash import Dash, dcc, html, Input, Output, dash_table, callback
import plotly.express as px
import pandas as pd
import numpy as np
import dash

import layouts
import callbacks
import config
import sites
import utils

app = Dash(__name__, title=config.title, suppress_callback_exceptions=True)

server = app.server

app.layout = html.Div([
    dcc.Location(id='url', refresh=True),
    html.Div(id='page-content')
])


@callback(Output('page-content', 'children'),
          [Input('url', 'pathname')])
def display_page(pathname):

    if pathname == '/':
        
        return layouts.home_layout

    else:

        for site in sites.site_list:

            if pathname == site['site_url']:

                site_config = site

                break

        return layouts.call_layout(site_config)    


@app.callback(Output('intermediate-value', 'data'), Input('site-config', 'data'))
def process_data(site_config):

    df = utils.df_process(data_file_name=site_config['data_file_name'],
                          date_range=site_config['date_range'])

    return df.to_json(date_format='iso', orient='split')


@app.callback(Output('weather-value', 'data'), Input('site-config', 'data'))
def clean_data(site_config):

    df_temp = utils.weather_data(site_config['weather_file_name'])

    return df_temp.to_json(date_format='iso', orient='split')


@app.callback(Output('daily-notes', 'data'), Input('site-config', 'data'))
def add_notes(site_config):

    df_temp = utils.note_data(site_config['note_file_name'])

    return df_temp.to_json(date_format='iso', orient='split')


@app.callback(Output('site-config', 'data'), Input('url', 'pathname'))
def clean_data(pathname):

    for site in sites.site_list:

        site_config = 0

        if pathname == site['site_url']:

            site_config = site

            break

    return site_config


if __name__ == '__main__':
    app.run(debug=False)
    # app.run(debug=True)

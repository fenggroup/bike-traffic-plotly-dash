from dash import dcc, html, dash_table
import config
import sites

import numpy as np
import pandas as pd

def call_layout(site_config):

    layout = html.Div([

        html.Div(id='dash-header',
                 children=[
                    html.H1(children=config.title),
                    html.H3(children=dcc.Markdown(
                            site_config['loc_msg_markdown'])),
                    # html.H3(children=site_config['dates_msg']),
                ]),

        html.Div(id='dash-controls',
                 children=[
                    html.Div(id='select-date-range',
                            children=[
                                html.Span(children='Select dates', style={'font-weight': 'bold'}),
                                dcc.DatePickerRange(id='my-date-picker-range',
                                                        min_date_allowed=site_config['date_range'][0],
                                                        max_date_allowed=site_config['date_range'][1],
                                                        start_date=site_config['date_range'][0],
                                                        end_date=site_config['date_range'][1],
                                                        first_day_of_week=1,  # start on Mondays
                                                        minimum_nights=0,
                                                        updatemode='singledate',
                                                        ),
                            ]),

                    html.Div(id='select-direction',
                            children=[
                                html.Span(children='Traffic direction', style={'font-weight': 'bold'}),
                                dcc.RadioItems(options={'bi_direction': 'Both',
                                                        'in': site_config['config_direction']['in'] + ' only',
                                                        'out': site_config['config_direction']['out'] + ' only'},
                                                value='bi_direction',
                                                inputStyle={"margin-left": "10px"},
                                                inline=True,
                                                id='data-dir-radio'),
                            ]),
                 ]),

        html.Div(id='bar-graph-div',
                 children=[
                 html.Div(id='select-resolution',
                            children=[
                                html.Span(children='Select time resolution', style={'font-weight': 'bold'}),
                                dcc.RadioItems(options={'1_month': 'monthly',
                                                        '1_week': 'weekly',
                                                        '1_day': 'daily',
                                                        '1_hour': 'hourly',
                                                        '30_min': '30 min',
                                                        '15_min': '15 min'},
                                                value=site_config['default_res'],
                                                inputStyle={"margin-left": "10px"},
                                                inline=True,
                                                id='data-agg-radio'),
                            ]),

            dcc.Graph(id='bar-graph', 
                      config={'toImageButtonOptions': {
                              'format': 'png', 'filename': 'bar_chart', 'height': None, 'width': None, 'scale': 10}, 'displaylogo': False}
                      )]),

        html.Div(id='table-div',
            children=[
            html.H3(children='Traffic summary on the selected dates'),
            dash_table.DataTable(data=pd.DataFrame(np.zeros((3, 4))).to_dict('records'),
                                 columns=[
                dict(id='dir', name=''),
                dict(id='total_vol', name='Total traffic', type='numeric',
                     format=dash_table.Format.Format().group(True)),
                dict(id='daily_avg', name='Average daily traffic', type='numeric', format=dash_table.Format.Format(
                        precision=1, scheme=dash_table.Format.Scheme.fixed)),
                dict(id='perc', name='Percent', type='numeric',
                     format=dash_table.FormatTemplate.percentage(1))
            ],
                style_cell_conditional=[
                {'if': {'column_id': 'dir'},
                 'width': '25%'},
                {'if': {'column_id': 'total_vol'},
                 'width': '25%'},
                {'if': {'column_id': 'daily_avg'},
                 'width': '25%'},
                {'if': {'column_id': 'perc'},
                 'width': '20%'},
            ],
                style_cell={'font-family': 'Roboto',
                            'padding-right': '10px', 
                            'padding-left': '10px'},
                id='avg-table'),
        ]),

        html.Div(id='time-of-day-div',
            children=[
            html.Div(id='select-dayofweek-1',
                children=[
                # html.Span(children='Select day of week', style={'font-weight': 'bold'}),
                dcc.Checklist(id='time-day-checklist',
                            options=config.weekday_list,
                            value=config.weekday_list,
                            inputStyle={"margin-left": "10px"},
                            inline=True,
                            )]),
            
            dcc.Graph(id='time-of-day', 
                    config={'toImageButtonOptions': {'format': 'png', 'filename': 'time_of_day_chart', 'height': None, 'width': None, 'scale': 10}, 'displaylogo': False}
            )]),

        html.Div(children=[dcc.Graph(id='avg-hour-traffic',
                                     config={'toImageButtonOptions': {'format': 'png', 'filename': 'avg_hourly_traffic_chart', 'height': 350, 'width': 750, 'scale': 10}, 'displaylogo': False})]),

        html.Div(children=[dcc.Graph(id='day-of-week',
                                     config={'toImageButtonOptions': {'format': 'png', 'filename': 'day_of_week_chart', 'height': 350, 'width': 750, 'scale': 10}, 'displaylogo': False})]),

        html.Div(children=[dcc.Checklist(id='day-checklist',
                                         options=config.weekday_list,
                                         value=config.weekday_list,
                                         inputStyle={"margin-left": "10px"},
                                         inline=True,
                                         )]),

        html.Div(children=[dcc.RadioItems(id='rain-radio',
                                         options=['All days', 'Only days without rain'],
                                         value='All days',
                                         inputStyle={"margin-left": "10px"},
                                         style={"margin-top": "15px",
                                             "margin-bottom": "5px",},
                                         inline=True,
                                         )]),

        html.Div(children=[dcc.Graph(id='weather-plot',
                                     config={'toImageButtonOptions': {'format': 'png', 'filename': 'weather_chart', 'height': 350, 'width': 750, 'scale': 10}, 'displaylogo': False})]),

        html.Div(id='footer',
        children=[
                        html.H4(children=dcc.Markdown('This dashboard is open source and hosted on a [GitHub repository](https://github.com/fenggroup/bike-traffic-plotly-dash).')),
            html.H4(children=dcc.Markdown('Download the [bike counter data](https://github.com/fenggroup/bike-traffic-plotly-dash/tree/main/data/counter)')),
            # html.H4(children=dcc.Markdown('[Click here](https://fenggroup.org/bike-counter/) to learn more about our bike counting project.')),
            # html.H4(children=dcc.Markdown('[Feng Group](https://fenggroup.org/) 2022'))
        ]),

        # dcc.Store stores the values
        dcc.Store(id='intermediate-value'),
        dcc.Store(id='weather-value'),
        dcc.Store(id='daily-notes'),
        dcc.Store(id='site-config'),

    ])

    return layout


home_layout = html.Div(children=[
    html.H1(children='Bike counter dashboard'),

    html.H3(children='Select a bike counter below to see its dashboard.'),

    html.Div([html.Br(),
              dcc.Link(sites.site_01['site_title'], href=sites.site_01['site_url']),
              html.Br(),
              html.Br(),
              dcc.Link(sites.site_02['site_title'], href=sites.site_02['site_url']),
              html.Br(),
              html.Br(),
              dcc.Link(sites.site_03['site_title'], href=sites.site_03['site_url']),
              html.Br(),
              html.Br(),
    ]),

    html.Div(children=[
    html.H4(children=dcc.Markdown('The dashboards are open source and hosted on [our GitHub repository](https://github.com/fenggroup/bike-traffic-plotly-dash).')),
    html.H4(children=dcc.Markdown('[Feng Group](https://fenggroup.org/) 2022'))
    ]),

])
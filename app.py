from dash import Dash, dcc, html, Input, Output, dash_table, callback
import plotly.express as px
import pandas as pd
import numpy as np
import dash


title = 'Bicycle Traffic Dashboard'

app = Dash(__name__, title=title, suppress_callback_exceptions=True)

# Declare server for Heroku deployment. Needed for Procfile.
server = app.server

# Set plotly template
template = 'plotly_white'

# Set color codes
color_both_direction = 'rgb(80, 123, 0)' # "#507B00"  # green
color_in = 'rgb(99, 110, 250)'   # blue
color_out = 'rgb(230, 180, 0)'   # yellow

# A function to pre-prossess the raw data from bike counter to a pandas dataframe
def df_preprocess(data_file_name, date_range):

    path = "./data/" + data_file_name

    df = pd.read_excel(path, names=["time", "in", "out"], skiprows=3)

    df["bi_direction"] = df["in"] + df["out"]

    # Convert the time to a pandas datetime object
    df["time"] = pd.to_datetime(df["time"])

    df = df.set_index("time")

    df = df[date_range[0] : date_range[1]]

    return df

# A function to update the dataframe based on the specified resample rule and date range
def df_update(df, rule, start_date, end_date):

    df_resample = df.resample(rule).sum()

    df_filtered = df_resample[(df_resample.index.strftime("%Y-%m-%d") >= start_date) & 
                              (df_resample.index.strftime("%Y-%m-%d") <= end_date)]

    df_filtered["day_of_week"] = df_filtered.index.strftime("%a")

    return df_filtered

# reads the temperature data into the dash
df_temp = pd.read_csv("./data/weather-noaa-annarbor.csv")

# Convert the time to a pandas datetime object
df_temp["DATE"] = pd.to_datetime(df_temp["DATE"])

df_temp = df_temp.set_index("DATE")

# convert rgb to rgba with transparency (alpha) value
def rgb2rgba(rgb, alpha):
    return 'rgba' + rgb[3:-1]  + ', ' + str(alpha) + ')'

# Set up a preliminary dataframe for the data table
table = pd.DataFrame(np.zeros((3,4)))

# Set font style for all figures
figure_font = dict(family='Roboto',
                   size=16, 
                   color='black')


index_page = html.Div([
    dcc.Link('Home', href='/'),
    html.Br(),
    dcc.Link('Ann Arbor data', href='/annarbor'),
    html.Br(),
    dcc.Link('Dearborn data', href='/dearborn'),
])

app.layout = html.Div([
    dcc.Location(id='url', refresh=True),
    html.Div(id='page-content')
])

home_layout = html.Div(children=[
    html.H1(children='Welcome to our interact bike traffic dashboard'),

    html.Div(children='''
        Select the location you want to see traffic for above
    '''),

])

def call_layout():

    # create a global variable to save the data at the site
    global df
    df = df_preprocess(data_file_name=site_config['data_file_name'],
                       date_range=site_config['date_range'])

    layout =  html.Div([
        
        html.Div(children=[
                html.H1(children=title), 
                html.H3(children=dcc.Markdown(site_config['loc_msg_markdown'])),
                html.H3(children=site_config['dates_msg']),
                ]),
        
        html.Div(id='select-date-range',
                children=[
                html.H3(children='Select dates'), 
                dcc.DatePickerRange(id='my-date-picker-range',
                                    min_date_allowed = site_config['date_range'][0],
                                    max_date_allowed = site_config['date_range'][1],
                                    start_date = site_config['date_range'][0],
                                    end_date = site_config['date_range'][1],
                                    first_day_of_week=1,  # start on Mondays
                                    minimum_nights=0,),
                ]),
        
        html.Div(id='select-direction',
                children=[
                html.H3(children='Select traffic direction'), 
                dcc.RadioItems(options={'bi_direction': 'Both directions', 
                                        'in': site_config['config_direction']['in'], 
                                        'out': site_config['config_direction']['out']},
                                value='bi_direction',
                                id='data-dir-radio'),
                ]),
        
        html.Div(id='select-resolution',
                children=[
                html.H3(children='Select data resolution'), 
                dcc.RadioItems(options={'1_week': 'weekly',
                                        '1_day': 'daily',
                                        '1_hour': 'hourly', 
                                        '15_min': '15 min'}, 
                                value='1_day',
                                id='data-agg-radio'),
                ]),

    html.Div(children=[
    dcc.Graph(id='bar-graph',style={'margin-top': '20px', 'margin-bottom': '40px'},
    config = {'toImageButtonOptions': {'format': 'png','filename': 'bar_chart', 'height': 350,'width': 750,'scale': 10}}
    )]),

        html.Div(children=[
                html.H3(children='Traffic summary on the selected dates'), 
                dash_table.DataTable(data = table.to_dict('records'), 
                                    columns =[
                                        dict(id='dir', name=''),
                                        dict(id='total_vol', name='Total traffic', type='numeric', format=dash_table.Format.Format().group(True)),
                                        dict(id='daily_avg', name='Average daily traffic', type='numeric', format=dash_table.Format.Format(precision=1, scheme=dash_table.Format.Scheme.fixed)),
                                        dict(id='perc', name='Percent', type='numeric', format=dash_table.FormatTemplate.percentage(1))
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
                                    style_table={'height': '250px', 'overflowY': 'auto'},
                                    style_cell={'font-family':'Roboto', 'padding-right': '10px', 'padding-left': '10px'},
                                    id='avg-table'),
                ]), 
        

        html.Div(children=[dcc.Graph(id='time-of-day', style={'margin-top': '-100px', 'margin-bottom': '20px'},
                                config = {'toImageButtonOptions': {'format': 'png','filename': 'time_of_day_chart', 'height': 350,'width': 750,'scale': 10}})]),        

        html.Div(children=[dcc.Graph(id='avg-hour-traffic', style={'margin-bottom': '20px'},   
                                config = {'toImageButtonOptions': {'format': 'png','filename': 'avg_hourly_traffic_chart', 'height': 350,'width': 750,'scale': 10}})]),

        html.Div(children=[dcc.Graph(id='day-of-week', style={'margin-bottom': '20px'},   
                                config = {'toImageButtonOptions': {'format': 'png','filename': 'day_of_week_chart', 'height': 350,'width': 750,'scale': 10}})]),
        
        html.Div(children=[dcc.Checklist(id='day-checklist',          
                                options=['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
                                value=['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'])]),

        html.Div(children=[dcc.Graph(id='weather-plot',
                                config = {'toImageButtonOptions': {'format': 'png','filename': 'weather_chart', 'height': 350,'width': 750,'scale': 10}})]),

        html.Div(children=[
            html.H4(children=dcc.Markdown('Download the [data files](https://github.com/fenggroup/bike-traffic-plotly-dash/tree/main/data)')),
            html.H4(children=dcc.Markdown('[Click here](https://fenggroup.org/bike-counter/) to learn more about our bike counting project.')), 
            html.H4(children=dcc.Markdown('This dashboard is open source and hosted on [our GitHub repository](https://github.com/fenggroup/bike-traffic-plotly-dash).')), 
            html.H4(children=dcc.Markdown('[Feng Group](https://fenggroup.org/) 2022'))
        ])

        
    ])

    return layout

@callback(Output('page-content', 'children'),
              [Input('url', 'pathname')])
def display_page(pathname):

    global site_config

    if pathname == '/dearborn':

        # Config for Dearborn data
        site_config = dict(data_file_name='bike_data_dearborn.xlsx', 
                           config_direction={'in':'Eastbound', 
                                             'out':'Westbound'}, 
                           loc_msg_markdown='Location: [Rouge Gateway Trail, Dearborn, MI](https://goo.gl/maps/WzSvLWxtkyoro9oK8)',
                           dates_msg='Data collection: 5 weeks (2022-06-15 to 2022-07-19)', 
                           date_range=['2022-06-15',    # the first full *day* of data collection in Dearborn
                                       '2022-07-19'],
                           )

    elif pathname == '/annarbor':

        # Config for Ann Arbor data
        site_config = dict(data_file_name='export_data_domain_7992.xlsx', 
                           config_direction={'in':'Northbound', 
                                             'out':'Southbound'}, 
                           loc_msg_markdown='Location: N Division, Ann Arbor, MI ([Site photo](https://fenggroup.org/images/respic/bike-counter-a2division.png), [Google Maps](https://goo.gl/maps/1bcfHrqSYbqiRSXa8))',
                           dates_msg='Data collection: 2022-08-26 to 2022-10-24 (ongoing)', 
                           date_range=['2022-08-26',   # the first full *day* of data collection in AA
                                       '2022-10-24'],
                           )

    return call_layout()

    # elif pathname == '/':
    #     return home_layout

@callback(
    Output(component_id='bar-graph', component_property='figure'),
    Input(component_id='data-dir-radio', component_property='value'),
    Input(component_id='data-agg-radio', component_property='value'),
    Input(component_id='my-date-picker-range', component_property='start_date'),
    Input(component_id='my-date-picker-range', component_property='end_date'))

def update_figure(dir_radio_val, agg_radio_val, start_date, end_date):

    if agg_radio_val == '15_min':
        rule = '15T'
    elif agg_radio_val == '1_hour':
        rule = 'H'
    elif agg_radio_val == '1_day':
        rule = 'D'
    elif agg_radio_val == '1_week':
        rule = 'W'

    df_updated = df_update(df=df, rule=rule, start_date=start_date, end_date=end_date)


    labels = {'time': 'Date', 
              'bi_direction': 'Total count',
              'in': site_config['config_direction']['in'],
              'out': site_config['config_direction']['out'],
              'day_of_week': 'Day of week',
              }

    if dir_radio_val == 'in':

        hover_data= ['day_of_week']
        marker_color = color_in
    
    elif dir_radio_val == 'out':

        hover_data= ['day_of_week']
        marker_color = color_out

    elif dir_radio_val == 'bi_direction':

        hover_data = ['in', 'out', 'day_of_week']
        marker_color = color_both_direction


    # add features for *daily* chart
    if agg_radio_val == '1_day':

        df_updated = df_updated.join(df_temp)

        labels.update({'TMAX': 'Temperature high (F)',
                       'TMIN': 'Temperature low (F)',
                       'PRCP': 'Precipitation (inches)',
                      })

        hover_data = hover_data + ['TMIN', 'TMAX', 'PRCP']

    fig1 = px.bar(df_updated, 
                  x=df_updated.index, 
                  y=dir_radio_val, 
                  labels=labels, 
                  hover_data=hover_data,
                  template=template)

    fig1.update_traces(marker_color=marker_color)

    fig1.update_layout(xaxis_title='Date & time', 
                       yaxis_title='Count', 
                       title='<b>Bike traffic counts by date & time</b>',
                       title_x=0.5,  # center title
                       transition_duration=500, 
                       font=figure_font,
                       hoverlabel=dict(font_color='white'),
                       modebar_remove=['zoom', 'pan', 'select','lasso2d', 'zoomIn', 'zoomOut', 'autoScale'])
       
    # number of days in the selected date range
    numdays = (df_updated.index.max() - df_updated.index.min()).days
    
    # Disable showing time of day on x-axis in the daily bar chat.
    # instead, show everyday once (delta tick of 1 day)
    if (agg_radio_val == '1_day') and (numdays <= 7):
        fig1.update_xaxes(dtick='d1', tickformat='%b%e\n%Y')
    
    return fig1
    

@callback(
    Output(component_id='avg-table', component_property='data'),
    Input(component_id='my-date-picker-range', component_property='start_date'),
    Input(component_id='my-date-picker-range', component_property='end_date'))

def update_table(start_date, end_date):

    df_updated = df_update(df=df, 
                           rule='D', 
                           start_date=start_date, 
                           end_date=end_date)

    df_updated.drop(columns='day_of_week', inplace=True)

    total_vol = df_updated.sum()
    daily_avg = df_updated.mean()

    # Calculate percentages
    perc_in = total_vol.loc['in'] / total_vol.loc['bi_direction']
    perc_out = total_vol.loc['out'] / total_vol.loc['bi_direction']

    perc = pd.Series({'in': perc_in, 
                      'out': perc_out, 
                      'bi_direction': 1})

    direction = pd.Series({'in': site_config['config_direction']['in'], 
                           'out': site_config['config_direction']['out'], 
                           'bi_direction': 'Both directions'})

    table = pd.DataFrame((direction, total_vol, daily_avg, perc)).T

    table.columns = ['dir', 'total_vol', 'daily_avg', 'perc']

    data_table = table.loc[['bi_direction', 'in', 'out']].to_dict('records')
    
    return  data_table

@callback(
    Output(component_id='time-of-day', component_property='figure'),
    Input(component_id='data-dir-radio', component_property='value'),
    Input(component_id='my-date-picker-range', component_property='start_date'),
    Input(component_id='my-date-picker-range', component_property='end_date'))

def update_figure(dir_radio_val, start_date, end_date):
   
    df_time = df_update(df=df, rule='15T', start_date=start_date, end_date=end_date)
       
    ctb_time = pd.crosstab(index = [df_time.index.isocalendar().week, df_time.index.day], 
                           columns  =df_time.index.hour,
                           rownames=['week', 'day'],
                           values = df_time[dir_radio_val], 
                           aggfunc = 'sum')
    
    labels = {'col_0': 'Time of day', 
              'value': 'Count'}

    fig2 = px.box(data_frame=ctb_time,
                  labels=labels, 
                  points=False)

    xticks=np.arange(-0.5, 24, 1) 
    xlabels=np.arange(0, 25, 1)

    fig2['layout'] = {'xaxis':{'tickvals':xticks, 
                               'ticktext':xlabels,
                               'showline':True
                               }
                      }

    fig2.add_trace(px.strip(data_frame=ctb_time, labels=labels).data[0])

    alpha = 0.4

    if dir_radio_val == 'in':

        marker_color = rgb2rgba(color_in, alpha)
    
    elif dir_radio_val == 'out':

        marker_color = rgb2rgba(color_out, alpha)

    elif dir_radio_val == 'bi_direction':

        marker_color = rgb2rgba(color_both_direction, alpha)
    
    fig2.update_traces(marker_color=marker_color,
                       marker_size=10,
                       jitter=0.7)

    fig2.update_layout(xaxis_title='Time of day', 
                       yaxis_title='Count',
                       title='<b>Hourly traffic by time of day</b>',
                       title_x=0.5,  # center title
                       transition_duration=500,
                       font=figure_font,
                       yaxis_range=[0, ctb_time.max().max()+5], 
                       height=500,
                       template=template,
                       modebar_remove=['zoom', 'pan', 'select','lasso2d', 'zoomIn', 'zoomOut', 'autoScale'])
    
    return fig2

@callback(
    Output(component_id='day-of-week', component_property='figure'),
    Input(component_id='data-dir-radio', component_property='value'),
    Input(component_id='my-date-picker-range', component_property='start_date'),
    Input(component_id='my-date-picker-range', component_property='end_date'))

def update_figure(dir_radio_val, start_date, end_date):
    
    df_day = df_update(df=df, rule='15T', start_date=start_date, end_date=end_date)


    ctb_day = pd.crosstab(index=df_day.index.isocalendar().week,
                          columns=df_day.day_of_week,
                          values = df_day[dir_radio_val],
                          aggfunc='sum')

    category_orders = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']

    labels = {'day_of_week': 'Day of week', 
              'value': 'Count'}

    fig3 = px.box(data_frame=ctb_day, 
                    category_orders=category_orders,
                    labels=labels,
                    hover_data=['day_of_week'], 
                    template=template, 
                    points='all')

    alpha = 0.7

    if dir_radio_val == 'in':

        marker_color = rgb2rgba(color_in, alpha)
    
    elif dir_radio_val == 'out':

        marker_color = rgb2rgba(color_out, alpha)

    elif dir_radio_val == 'bi_direction':

        marker_color = rgb2rgba(color_both_direction, alpha)

    fig3.update_traces(marker_color=marker_color,
                       marker_size=20,
                       jitter=0.3)

    fig3.update_layout(xaxis_title='',
                       yaxis_title='Count',
                       title='<b>Daily traffic by day of week</b>',
                       title_x=0.5,  # center title
                       yaxis_range=[0, ctb_day.max().max()+20], 
                       transition_duration=500,
                       font=figure_font,
                       height=500,
                       modebar_remove=['zoom', 'pan', 'select','lasso2d', 'zoomIn', 'zoomOut', 'autoScale'])

    fig3.update_xaxes(categoryorder='array', categoryarray=category_orders)
    
    return fig3

@callback(
    Output(component_id='avg-hour-traffic', component_property='figure'),
    Input(component_id='data-dir-radio', component_property='value'),
    Input(component_id='my-date-picker-range', component_property='start_date'),
    Input(component_id='my-date-picker-range', component_property='end_date'))
    
def update_figure(dir_radio_val, start_date, end_date):
    
    df_updated = df_update(df=df, rule='H', start_date=start_date, end_date=end_date)

    days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']

    ctb_time = pd.crosstab(index = df_updated.day_of_week, 
                           columns = df_updated.index.hour,
                           rownames=['day of week'],
                           values = df_updated[dir_radio_val], 
                           aggfunc = 'mean').reindex(days)

    labels = {'col_0': 'Time of day', 
              'value': 'Count'}

    fig4 = px.line(ctb_time.T,
                       labels = labels)

    xticks = np.arange(-0.5, 24, 1) 
    xlabels = np.arange(0, 25, 1)

    fig4['layout'] = {'xaxis':{'tickvals':xticks, 
                      'ticktext':xlabels,
                      'showline':True
                            }
                      }

    fig4.update_traces(line=dict(width=4))

    fig4.update_layout(xaxis_title='Time of day', 
                       yaxis_title='Count',
                       title='<b>Average hourly traffic by time of day</b>',
                       title_x=0.5,  # center title
                       transition_duration=500,
                       font=figure_font,
                       yaxis_range=[0, ctb_time.max().max()+5], 
                       height=500,
                       template=template,
                       modebar_remove=['zoom', 'pan', 'select','lasso2d', 'zoomIn', 'zoomOut', 'autoScale'])
    
    # add annotation
    fig4.add_annotation(dict(font=dict(color='gray',size=18),
                                            x=1.08,
                                            y=1.1,
                                            showarrow=False,
                                            text="You can click on a particular day-of-week in the legend to show/hide the data ↓",
                                            textangle=0,
                                            xanchor='right',
                                            xref="paper",
                                            yref="paper"))

    return fig4

@callback(
    Output(component_id='weather-plot', component_property='figure'),
    Input(component_id='data-dir-radio', component_property='value'),
    Input(component_id='day-checklist', component_property='value'),
    Input(component_id='my-date-picker-range', component_property='start_date'),
    Input(component_id='my-date-picker-range', component_property='end_date'))

def update_figure(dir_radio_val, day_checklist_val, start_date, end_date):

    df_updated = df_update(df=df, rule='D', start_date=start_date, end_date=end_date)

    dff_temp = df_temp[start_date : end_date]

    df_weather = df_updated.join(dff_temp)

    df_weather = df_weather[df_weather['day_of_week'].isin(day_checklist_val)]

    labels = {'bi_direction': 'Daily count', 
              'value': 'Temperature',
              'TMAX': 'Maximum temperature (F)',
              'day_of_week': 'Day of week',
              'PRCP': 'Precipitation (inches)'}


    hover_data= ['day_of_week', 'PRCP']

    fig5 = px.scatter(df_weather, 
                      x='TMAX', 
                      y=dir_radio_val,
                      labels = labels,
                      hover_data=hover_data, 
                      trendline='ols')

    alpha = 0.7

    if dir_radio_val == 'in':

        marker_color = rgb2rgba(color_in, alpha)
    
    elif dir_radio_val == 'out':

        marker_color = rgb2rgba(color_out, alpha)

    elif dir_radio_val == 'bi_direction':

        marker_color = rgb2rgba(color_both_direction, alpha)

    fig5.update_traces(marker_color=marker_color, 
                       marker_size=20)

    fig5.update_layout(xaxis_title='Maximum temperature (Fahrenheit)', 
                       yaxis_title='Daily count',
                       title='<b>Daily traffic by maximum temperature</b>',
                       title_x=0.5,  # center title
                       transition_duration=500,
                       font=figure_font, 
                       height=500,
                       template=template,
                       modebar_remove=['zoom', 'pan', 'select','lasso2d', 'zoomIn', 'zoomOut', 'autoScale'])
                       

    return fig5


if __name__ == '__main__':
    # app.run(debug=False)
    app.run(debug=True)
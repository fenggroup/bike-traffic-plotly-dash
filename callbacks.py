from dash import Input, Output, callback
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
import pandas as pd

import layouts
import config
import utils

# Callback for the main bar chart
@callback(
    Output(component_id='bar-graph', component_property='figure'),
    Input(component_id='data-dir-radio', component_property='value'),
    Input(component_id='data-agg-radio', component_property='value'),
    Input(component_id='my-date-picker-range', component_property='start_date'),
    Input(component_id='my-date-picker-range', component_property='end_date'),
    Input('intermediate-value', 'data'),
    Input('weather-value', 'data'),
    Input('site-config', 'data'),
    )
    
def update_figure(dir_radio_val, agg_radio_val, start_date, end_date, df, df_temp, site_config):

    df = pd.read_json(df, orient='split')

    df_temp = pd.read_json(df_temp, orient='split')

    if agg_radio_val == '15_min':
        rule = '15T'
    elif agg_radio_val == '1_hour':
        rule = 'H'
    elif agg_radio_val == '1_day':
        rule = 'D'
    elif agg_radio_val == '1_week':
        rule = 'W'

    df_updated = utils.df_update(df=df, rule=rule, start_date=start_date, end_date=end_date)

    labels = {'index': 'Date', 
              'bi_direction': 'Total count',
              'in': site_config['config_direction']['in'],
              'out': site_config['config_direction']['out'],
              'day_of_week': 'Day of week',
              }

    hover_data= ['day_of_week']

    if dir_radio_val == 'in':

        marker_color = config.color_in
    
    elif dir_radio_val == 'out':

        marker_color = config.color_out

    elif dir_radio_val == 'bi_direction':

        hover_data = ['in', 'out'] + hover_data
        marker_color = config.color_both_direction

    # add weather data for *daily* chart
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
                  template=config.template)

    fig1.update_traces(marker_color=marker_color)

    fig1.update_layout(xaxis_title='Date & time', 
                       yaxis_title='Count', 
                       title='<b>Bike traffic counts by date & time</b>',
                       title_x=0.5,  # center title
                       transition_duration=500, 
                       font=config.figure_font,
                       hoverlabel=dict(font_color='white'),
                       modebar_remove=config.modebar_remove)
       
    # number of days in the selected date range
    numdays = (df_updated.index.max() - df_updated.index.min()).days
    
    # Disable showing time of day on x-axis in the daily bar chat.
    # instead, show everyday once (delta tick of 1 day)
    if (agg_radio_val == '1_day') and (numdays <= 7):
        fig1.update_xaxes(dtick='d1', tickformat='%b%e\n%Y')
    
    return fig1
    

# Callback for the summary table
@callback(
    Output(component_id='avg-table', component_property='data'),
    Input(component_id='my-date-picker-range', component_property='start_date'),
    Input(component_id='my-date-picker-range', component_property='end_date'),
    Input('intermediate-value', 'data'),
    Input('site-config', 'data'),
    )

def update_table(start_date, end_date, df, site_config):

    df = pd.read_json(df, orient='split')

    df_updated = utils.df_update(df=df, 
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


# Callback for the time of day chart (showing raw data)
@callback(
    Output(component_id='time-of-day', component_property='figure'),
    Input(component_id='data-dir-radio', component_property='value'),
    Input(component_id='time-day-checklist', component_property='value'),
    Input(component_id='my-date-picker-range', component_property='start_date'),
    Input(component_id='my-date-picker-range', component_property='end_date'),
    Input('intermediate-value', 'data'),
    )

def update_figure(dir_radio_val, day_checklist_val, start_date, end_date, df):

    df = pd.read_json(df, orient='split')
   
    df_time = utils.df_update(df=df, rule='1H', start_date=start_date, end_date=end_date)

    df_time = df_time[df_time['day_of_week'].isin(day_checklist_val)]
       
    
    labels = {'x': 'Time of day', 
              'bi_direction': 'Count',
              'in': 'Count',
              'out': 'Count',
              'hover_data_0':'Date',
              'day_of_week':'Day of Week'}

    fig2 = px.box(data_frame=df_time,
                  x=df_time.index.hour, 
                  y=df_time[dir_radio_val],
                  labels=labels, 
                  points=False)

    xticks=np.arange(-0.5, 24, 1) 
    xlabels=np.arange(0, 25, 1)

    fig2['layout'] = {'xaxis':{'tickvals':xticks, 
                               'ticktext':xlabels,
                               'showline':True
                               }
                      }

    hover_data= [df_time.index.date, 'day_of_week']

    fig2.add_trace(px.strip(df_time, 
                            x=df_time.index.hour, 
                            y=df_time[dir_radio_val], 
                            labels=labels,
                            hover_data=hover_data).data[0])

    marker_color = utils.find_mark_color(dir_radio_val, alpha=0.4)
    
    fig2.update_traces(marker_color=marker_color,
                       marker_size=10,
                       jitter=0.7)

    fig2.update_layout(xaxis_title='Time of day', 
                       yaxis_title='Count',
                       title='<b>Hourly traffic by time of day</b>',
                       title_x=0.5,  # center title
                       transition_duration=500,
                       font=config.figure_font,
                       yaxis_range=[0, df_time[dir_radio_val].max()+5], 
                       height=500,
                       template=config.template,
                       modebar_remove=config.modebar_remove)
    
    return fig2


# Callback for the day of week chart
@callback(
    Output(component_id='day-of-week', component_property='figure'),
    Input(component_id='data-dir-radio', component_property='value'),
    Input(component_id='my-date-picker-range', component_property='start_date'),
    Input(component_id='my-date-picker-range', component_property='end_date'),
    Input('intermediate-value', 'data'),
    Input('weather-value', 'data'),
    )

def update_figure(dir_radio_val, start_date, end_date, df, df_temp):

    df = pd.read_json(df, orient='split')

    df_temp = pd.read_json(df_temp, orient='split')
    
    df_day = utils.df_update(df=df, rule='1D', start_date=start_date, end_date=end_date)

    df_day = df_day.join(df_temp)

    category_orders = config.weekday_list

    labels = {'day_of_week': 'Day of week', 
              'bi_direction': 'Count',
              'in': 'Count',
              'out': 'Count',
              'hover_data_0':'Date',
              'TMAX': 'Temperature high (F)',
              'TMIN': 'Temperature low (F)',
              'PRCP': 'Precipitation (inches)',}

    hover_data= [df_day.index.date,  'TMIN', 'TMAX','PRCP']

    fig3 = px.box(data_frame=df_day,
                  x=df_day.day_of_week,
                  y=df_day[dir_radio_val], 
                  category_orders=category_orders,
                  labels=labels,
                  hover_data=hover_data, 
                  template=config.template, 
                  points='all')

    marker_color = utils.find_mark_color(dir_radio_val, alpha=0.7)

    fig3.update_traces(marker_color=marker_color,
                       marker_size=20,
                       jitter=0.3)

    fig3.update_layout(xaxis_title='',
                       yaxis_title='Count',
                       title='<b>Daily traffic by day of week</b>',
                       title_x=0.5,  # center title
                    #    yaxis_range=[0, df_day[dir_radio_val].max()+20], 
                       transition_duration=500,
                       font=config.figure_font,
                       height=500,
                       modebar_remove=config.modebar_remove)

    fig3.update_xaxes(categoryorder='array', categoryarray=category_orders)
    
    return fig3


# Callback for the average traffic by time of day line chart
@callback(
    Output(component_id='avg-hour-traffic', component_property='figure'),
    Input(component_id='data-dir-radio', component_property='value'),
    Input(component_id='my-date-picker-range', component_property='start_date'),
    Input(component_id='my-date-picker-range', component_property='end_date'),
    Input('intermediate-value', 'data'),
    )
    
def update_figure(dir_radio_val, start_date, end_date, df):

    df = pd.read_json(df, orient='split')
    
    df_updated = utils.df_update(df=df, rule='H', start_date=start_date, end_date=end_date)

    days = config.weekday_list

    ctb_time = pd.crosstab(index = df_updated.day_of_week, 
                           columns = df_updated.index.hour,
                           rownames=['day of week'],
                           values = df_updated[dir_radio_val], 
                           aggfunc = 'mean').reindex(days)

    labels = {'col_0': 'Time of day', 
              'value': 'Count'}

    # A walkaround to fix a known issue: https://github.com/plotly/plotly.py/issues/3441
    
    fig4 = px.line(ctb_time.T, labels=labels)

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
                       font=config.figure_font,
                       yaxis_range=[0, ctb_time.max().max()+5], 
                       height=500,
                       template=config.template,
                       modebar_remove=config.modebar_remove)
    
    # add annotation
    fig4.add_annotation(dict(font=dict(color='gray',size=18),
                                            x=1.08,
                                            y=1.1,
                                            showarrow=False,
                                            text="You can click on a particular day-of-week label to show/hide the data ↓",
                                            textangle=0,
                                            xanchor='right',
                                            xref="paper",
                                            yref="paper"))

    return fig4


# Callback for the temperature vs count scatter chart
@callback(
    Output(component_id='weather-plot', component_property='figure'),
    Input(component_id='data-dir-radio', component_property='value'),
    Input(component_id='day-checklist', component_property='value'),
    Input(component_id='rain-radio', component_property='value'),
    Input(component_id='my-date-picker-range', component_property='start_date'),
    Input(component_id='my-date-picker-range', component_property='end_date'),
    Input('intermediate-value', 'data'),
    Input('weather-value', 'data'),
    )

def update_figure(dir_radio_val, day_checklist_val, rain_radio_val,start_date, end_date, df, df_temp):

    df = pd.read_json(df, orient='split')

    df_temp = pd.read_json(df_temp, orient='split')

    df_updated = utils.df_update(df=df, rule='D', start_date=start_date, end_date=end_date)

    dff_temp = df_temp[start_date : end_date]

    df_weather = df_updated.join(dff_temp)

    df_weather = df_weather[df_weather['day_of_week'].isin(day_checklist_val)]

    if rain_radio_val == 'Days with no rain':
        df_weather = df_weather.loc[df_weather['PRCP'] == 0]

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

    marker_color = utils.find_mark_color(dir_radio_val, alpha=0.7)

    fig5.update_traces(marker_color=marker_color, 
                       marker_size=20)

    fig5.update_layout(xaxis_title='Maximum temperature (Fahrenheit)', 
                       yaxis_title='Daily count',
                       title='<b>Daily traffic by maximum temperature</b>',
                       title_x=0.5,  # center title
                       transition_duration=500,
                       font=config.figure_font, 
                       height=500,
                       template=config.template,
                       modebar_remove=config.modebar_remove, 
                       yaxis_range=[0, df_weather[dir_radio_val].max()+20])
                       
    return fig5
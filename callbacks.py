from dash import Input, Output, callback
import plotly.express as px
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
    Input('daily-notes', 'data'),
    Input('site-config', 'data'),
    )
    
def update_figure(dir_radio_val, agg_radio_val, start_date, end_date, df, df_weather, df_notes, site_config):

    df = pd.read_json(df, orient='split')

    df_weather = pd.read_json(df_weather, orient='split')

    df_notes = pd.read_json(df_notes, orient='split')

    bargap = 0.1

    if agg_radio_val == '15_min':
        rule = '15T'
        bargap = 0
    elif agg_radio_val == '30_min':
        rule = '30T'
        bargap = 0
    elif agg_radio_val == '1_hour':
        rule = 'H'
        bargap = 0
    elif agg_radio_val == '1_day':
        rule = 'D'
    elif agg_radio_val == '1_week':
        rule = 'W'
    elif agg_radio_val == '1_month':
        rule = 'M'

    df_updated = utils.df_update(df=df, rule=rule, start_date=start_date, end_date=end_date)

    marker_color = config.color[dir_radio_val]

    # add additional hover data for *daily* chart
    if agg_radio_val == '1_day':

        df_updated = df_updated.join(df_weather)

        df_updated = df_updated.join(df_notes)

        hover_data = ['day_of_week', 'TMIN', 'TMAX', 'PRCP', 'notes', 'in', 'out']

        # To format date/time: https://github.com/d3/d3-time-format
        hovertemplate = 'Date: %{x|%b %d, %Y} (%{customdata[0]})' + \
                        '<br>Count: %{y}' + \
                        '<br>' + site_config['config_direction']['in'] + ': %{customdata[5]}' + \
                        '<br>' + site_config['config_direction']['out'] + ': %{customdata[6]}' + \
                        '<br>Temperature (F): %{customdata[1]}\u00B0 - %{customdata[2]}\u00B0' + \
                        '<br>Precipitation: %{customdata[3]} inches' + \
                        '<br>Notes: %{customdata[4]}<extra></extra>' 

    elif agg_radio_val == '1_week':

        hover_data = ['day_of_week']

        hovertemplate = 'Week that ends on %{x|%b %d, %Y}' + \
                        '<br>Count: %{y}'

    else:

        hover_data = ['day_of_week']

        hovertemplate = 'Date: %{x|%b %d, %Y} (%{customdata[0]})' + \
                        '<br>Time: %{x|%I:%M %p}' + \
                        '<br>Count: %{y}<extra></extra>' 

    fig1 = px.bar(df_updated, 
                  x=df_updated.index, 
                  y=dir_radio_val, 
                  hover_data=hover_data,
                  template=config.template)

    fig1.update_traces(marker_color=marker_color, 
                       hovertemplate=hovertemplate) 

    fig1.update_layout(xaxis_title='', 
                       yaxis_title='Count', 
                       title='<b>Bike traffic by date & time</b>',
                       title_x=0.5,  # center title
                       transition_duration=500, 
                       font=config.figure_font,
                       hoverlabel=dict(font_color='white'),
                       modebar_remove=config.modebar_remove,
                       bargap=bargap,
                       margin=dict(l=0, r=0, t=40, b=0),
                    #    paper_bgcolor="rgba(0,0,0,0)",    # transparent chart
                    #    plot_bgcolor="rgba(0,0,0,0)",
                       )
       
    # number of days in the selected date range
    numdays = (df_updated.index.max() - df_updated.index.min()).days

    # fig1.write_html("bike-counter-annarbor.html", full_html=False)
    
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

    fig2 = px.box(data_frame=df_time,
                  x=df_time.index.hour, 
                  y=df_time[dir_radio_val],
                  points=False)

    xticks=np.arange(-0.5, 25, 1) 
    # xlabels=np.arange(0, 25, 1)

    fig2['layout'] = {'xaxis':{'tickvals':xticks, 
                               'ticktext':config.time_of_day_labels,
                               'showline':True
                               }
                      }

    hover_data= [df_time.index.date, 'day_of_week']

    # To format date/time: https://github.com/d3/d3-time-format
    hovertemplate = 'Date: %{customdata[0]|%b %d, %Y} (%{customdata[1]})' + \
                    '<br>Count: %{y}'

    fig2.add_trace(px.strip(df_time, 
                            x=df_time.index.hour, 
                            y=df_time[dir_radio_val], 
                            # labels=labels,
                            hover_data=hover_data).data[0])

    marker_color = utils.rgb2rgba(config.color[dir_radio_val], alpha=0.4)
    
    fig2.update_traces(marker_color=marker_color,
                       marker_size=10,
                       jitter=0.7, 
                       width=0.8,
                       hovertemplate=hovertemplate)

    fig2.update_layout(xaxis_title='', 
                       yaxis_title='Count',
                       title='<b>Hourly traffic by time of day</b>',
                       title_x=0.5,  # center title
                       transition_duration=500,
                       font=config.figure_font,
                       yaxis_range=[0, df_time[dir_radio_val].max()+5], 
                       height=500,
                       template=config.template,
                       modebar_remove=config.modebar_remove,
                       margin=dict(l=0, r=0, t=40, b=0),
                       xaxis_range=[-0.5, 24],
                       )
    
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

def update_figure(dir_radio_val, start_date, end_date, df, df_weather):

    df = pd.read_json(df, orient='split')

    df_weather = pd.read_json(df_weather, orient='split')
    
    df_day = utils.df_update(df=df, rule='1D', start_date=start_date, end_date=end_date)

    df_day = df_day.join(df_weather)

    category_orders = config.weekday_list

    hover_data = [df_day.index.date, 'TMIN', 'TMAX', 'PRCP']

    # To format date/time: https://github.com/d3/d3-time-format
    hovertemplate = 'Date: %{customdata[0]|%b %d, %Y} (%{x})' + \
                    '<br>Count: %{y}' + \
                    '<br>Temperature (F): %{customdata[1]}\u00B0 - %{customdata[2]}\u00B0' + \
                    '<br>Precipitation: %{customdata[3]} inches'

    fig3 = px.box(data_frame=df_day,
                  x=df_day.day_of_week,
                  y=df_day[dir_radio_val], 
                  category_orders=category_orders,
                #   labels=labels,
                #   hover_data=hover_data, 
                #   template=config.template, 
                #   points='all',
                  points=False,
                  )

    marker_color = utils.rgb2rgba(config.color[dir_radio_val], alpha=0.7)

    fig3.add_trace(px.strip(df_day, 
                            x=df_day.day_of_week,
                            y=df_day[dir_radio_val], 
                            # labels=labels,
                            hover_data=hover_data).data[0])

    fig3.update_traces(marker_color=marker_color,
                       marker_size=20,
                       jitter=0.8,
                       width=0.6, 
                       hovertemplate=hovertemplate)

    fig3.update_layout(xaxis_title='',
                       yaxis_title='Count',
                       title='<b>Daily traffic by day of week</b>',
                       title_x=0.5,  # center title
                       yaxis_range=[0, df_day[dir_radio_val].max()+20], 
                       transition_duration=500,
                       font=config.figure_font,
                       height=500,
                       modebar_remove=config.modebar_remove,
                       margin=dict(l=0, r=0, t=40, b=0),
                       template=config.template,
                       )

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
                           rownames=['day_of_week'],
                           values = df_updated[dir_radio_val], 
                           aggfunc = 'mean').reindex(days)

    labels = {'col_0': 'Time of day', 
              'day_of_week': 'Day of week', 
              'value': 'Average hourly count'}

    # hover_data = [ctb_time.index]

    # # To format date/time: https://github.com/d3/d3-time-format
    # hovertemplate = 'Day of week: %{customdata[0]}' + \
    #                   '<br>Time of day: %{x}' + \
    #                 '<br>Count: %{y}'

    # day of week=Mon<br>Time of day=%{x}<br>Avg. hourly count=%{y}<extra></extra>

    # A walkaround to fix a known issue: https://github.com/plotly/plotly.py/issues/3441
    
    fig4 = px.line(ctb_time.round(1).T,    # round number to 1 decimal
                  labels=labels, 
                  markers=True, 
                #   hover_data=hover_data,
                  )

    xticks = np.arange(-0.5, 24, 1) 
    # xlabels = np.arange(0, 25, 1)

    # fig4['layout'] = {'xaxis':{'tickvals':xticks, 
    #                   'ticktext':xlabels,
    #                   'showline':True
    #                         }
    #                   }

    fig4.update_traces(line=dict(width=3), 
                       marker=dict(size=8),
                    #    hovertemplate=hovertemlate,
                       )

    fig4.update_layout(xaxis_title='', 
                       yaxis_title='Count',
                       title='<b>Average hourly traffic by time of day</b>',
                       title_x=0.5,  # center title
                       transition_duration=500,
                       font=config.figure_font,
                       yaxis_range=[0, ctb_time.max().max()+5], 
                       height=500,
                       template=config.template,
                       modebar_remove=config.modebar_remove,
                       margin=dict(l=0, r=0, t=60, b=0),
                       legend=dict(yanchor="top",
                                   y=1.04,
                                   xanchor="center",
                                   x=0.5,
                                   orientation='h',
                                   entrywidth=170,
                                   ),
                      legend_title='Click on a label to hide the day of week → ',
                       xaxis={'tickvals':xticks, 
                      'ticktext':config.time_of_day_labels,
                      'showgrid':False,
                            },
                        xaxis_range=[-0.5, 24],     
                       )

    # print("plotly express hovertemplate:", fig4.data[0].hovertemplate)
    
    # # add annotation
    # fig4.add_annotation(dict(font=dict(color='gray',size=18),
    #                                         x=0.06,
    #                                         y=0.97,
    #                                         showarrow=False,
    #                                         text="↓ Click on a label to show/hide its data",
    #                                         textangle=0,
    #                                         xanchor='left',
    #                                         xref="paper",
    #                                         yref="paper"))

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

def update_figure(dir_radio_val, day_checklist_val, rain_radio_val, start_date, end_date, df, df_temp):

    df = pd.read_json(df, orient='split')

    df_temp = pd.read_json(df_temp, orient='split')

    df_updated = utils.df_update(df=df, rule='D', start_date=start_date, end_date=end_date)

    dff_temp = df_temp[start_date : end_date]

    df_weather = df_updated.join(dff_temp)

    df_weather = df_weather[df_weather['day_of_week'].isin(day_checklist_val)]

    if rain_radio_val == 'Only days without rain':
        df_weather = df_weather.loc[df_weather['PRCP'] == 0]

    hover_data = [df_weather.index.date, 'day_of_week', 'TMIN', 'TMAX', 'PRCP']

    # To format date/time: https://github.com/d3/d3-time-format
    hovertemplate = 'Date: %{customdata[0]|%b %d, %Y} (%{customdata[1]})' + \
                    '<br>Count: %{y}' + \
                    '<br>Temperature (F): %{customdata[2]}\u00B0 - %{x}\u00B0' + \
                    '<br>Precipitation: %{customdata[3]} inches'


    fig5 = px.scatter(df_weather, 
                      x='TMAX', 
                      y=dir_radio_val,
                      hover_data=hover_data, 
                      trendline='ols')

    marker_color = utils.rgb2rgba(config.color[dir_radio_val], alpha=0.7)
    
    fig5.update_traces(marker_color=marker_color, 
                       marker_size=20, 
                       hovertemplate=hovertemplate)

    fig5.update_layout(xaxis_title='Daily high temperature (Fahrenheit)', 
                       yaxis_title='Daily count',
                       title='<b>Daily traffic by daily high temperature</b>',
                       title_x=0.5,  # center title
                       transition_duration=500,
                       font=config.figure_font, 
                       height=500,
                       template=config.template,
                       modebar_remove=config.modebar_remove, 
                       yaxis_range=[0, df_weather[dir_radio_val].max()+30],
                       margin=dict(l=0, r=0, t=40, b=0),
                       )
                       
    return fig5